# ========================================
# 认证状态管理模块
# ========================================
# 提供登录状态（Cookie、localStorage、sessionStorage）的保存和加载功能
# 支持免登录复用，加速测试执行
# ========================================

import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from playwright.sync_api import Page, BrowserContext

from config.settings import Settings
from utils.logger import Logger

logger = Logger("AuthHelper")


class AuthHelper:
    """
    认证状态助手

    提供登录状态的保存和加载功能，支持：
    - 保存浏览器状态（Cookie + localStorage + sessionStorage）
    - 加载已保存的状态实现免登录
    - 状态过期检测
    - 多用户状态管理

    使用示例：
        # 方式1：在 TestContextHelper 中使用（推荐）
        helper = TestContextHelper()
        helper.login_and_init(page, base_url, "admin", "password123", save_auth=True)

        # 方式2：直接使用 AuthHelper
        auth = AuthHelper()

        # 保存状态
        auth.save_auth_state(page, "admin")

        # 加载状态
        if auth.load_auth_state(page, "admin"):
            print("免登录成功")
        else:
            print("需要重新登录")
    """

    # 认证状态文件存放目录
    AUTH_DIR = Settings.PROJECT_ROOT / ".auth"

    # 状态有效期（小时），超过此时间需要重新登录
    DEFAULT_EXPIRE_HOURS = 24

    def __init__(self, expire_hours: int = DEFAULT_EXPIRE_HOURS):
        """
        初始化认证助手

        Args:
            expire_hours: 状态有效期（小时），默认24小时
        """
        self.expire_hours = expire_hours
        self._ensure_auth_dir()

    def _ensure_auth_dir(self):
        """确保认证状态目录存在"""
        self.AUTH_DIR.mkdir(parents=True, exist_ok=True)

    def _get_state_file(self, user_key: str) -> Path:
        """
        获取状态文件路径

        Args:
            user_key: 用户标识（如用户名或角色名）

        Returns:
            状态文件路径
        """
        # 清理文件名中的特殊字符
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in user_key)
        return self.AUTH_DIR / f"{safe_key}_state.json"

    def save_auth_state(self, page: Page, user_key: str) -> bool:
        """
        保存当前页面的认证状态

        保存内容包括：
        - Cookies
        - localStorage
        - sessionStorage
        - 保存时间（用于过期检测）

        Args:
            page: Playwright 页面对象
            user_key: 用户标识（如用户名或角色名）

        Returns:
            True 保存成功，False 保存失败

        使用示例：
            # 登录成功后保存状态
            auth = AuthHelper()
            auth.save_auth_state(page, "admin")
        """
        try:
            context = page.context

            # 获取 cookies
            cookies = context.cookies()

            # 获取 localStorage 和 sessionStorage
            storage_state = page.evaluate("""() => {
                const state = {
                    localStorage: {},
                    sessionStorage: {}
                };

                // 获取 localStorage
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    state.localStorage[key] = localStorage.getItem(key);
                }

                // 获取 sessionStorage
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    state.sessionStorage[key] = sessionStorage.getItem(key);
                }

                return state;
            }""")

            # 组装完整状态
            auth_state = {
                "cookies": cookies,
                "localStorage": storage_state.get("localStorage", {}),
                "sessionStorage": storage_state.get("sessionStorage", {}),
                "saved_at": datetime.now().isoformat(),
                "expire_hours": self.expire_hours,
                "url": page.url
            }

            # 保存到文件
            state_file = self._get_state_file(user_key)
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(auth_state, f, ensure_ascii=False, indent=2)

            logger.info(f"认证状态已保存: {user_key} -> {state_file}")
            return True

        except Exception as e:
            logger.error(f"保存认证状态失败: {e}")
            return False

    def load_auth_state(self, page: Page, user_key: str, base_url: str = None) -> bool:
        """
        加载已保存的认证状态

        Args:
            page: Playwright 页面对象
            user_key: 用户标识
            base_url: 基础URL（用于设置cookie域名），如不提供则从状态文件获取

        Returns:
            True 加载成功且状态有效，False 状态不存在或已过期

        使用示例：
            auth = AuthHelper()
            if auth.load_auth_state(page, "admin", base_url):
                # 免登录成功，直接进行后续操作
                page.goto(base_url + "/dashboard")
            else:
                # 需要重新登录
                login_page.login(username, password)
        """
        state_file = self._get_state_file(user_key)

        # 检查状态文件是否存在
        if not state_file.exists():
            logger.info(f"认证状态文件不存在: {user_key}")
            return False

        try:
            # 读取状态文件
            with open(state_file, "r", encoding="utf-8") as f:
                auth_state = json.load(f)

            # 检查是否过期
            if self._is_expired(auth_state):
                logger.info(f"认证状态已过期: {user_key}")
                self.clear_auth_state(user_key)
                return False

            context = page.context

            # 先访问一个页面以设置正确的域
            target_url = base_url or auth_state.get("url", "about:blank")
            if target_url and target_url != "about:blank":
                page.goto(target_url, wait_until="domcontentloaded")

            # 加载 cookies
            cookies = auth_state.get("cookies", [])
            if cookies:
                context.add_cookies(cookies)

            # 加载 localStorage
            local_storage = auth_state.get("localStorage", {})
            if local_storage:
                page.evaluate("""(items) => {
                    for (const [key, value] of Object.entries(items)) {
                        localStorage.setItem(key, value);
                    }
                }""", local_storage)

            # 加载 sessionStorage
            session_storage = auth_state.get("sessionStorage", {})
            if session_storage:
                page.evaluate("""(items) => {
                    for (const [key, value] of Object.entries(items)) {
                        sessionStorage.setItem(key, value);
                    }
                }""", session_storage)

            # 刷新页面使状态生效
            page.reload(wait_until="domcontentloaded")

            logger.info(f"认证状态已加载: {user_key}")
            return True

        except Exception as e:
            logger.error(f"加载认证状态失败: {e}")
            return False

    def _is_expired(self, auth_state: dict) -> bool:
        """
        检查状态是否过期

        Args:
            auth_state: 状态数据

        Returns:
            True 已过期，False 未过期
        """
        try:
            saved_at_str = auth_state.get("saved_at")
            if not saved_at_str:
                return True

            saved_at = datetime.fromisoformat(saved_at_str)
            expire_hours = auth_state.get("expire_hours", self.DEFAULT_EXPIRE_HOURS)
            expire_time = saved_at + timedelta(hours=expire_hours)

            return datetime.now() > expire_time

        except Exception:
            return True

    def is_auth_valid(self, user_key: str) -> bool:
        """
        检查指定用户的认证状态是否有效

        Args:
            user_key: 用户标识

        Returns:
            True 状态存在且未过期，False 状态不存在或已过期
        """
        state_file = self._get_state_file(user_key)

        if not state_file.exists():
            return False

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                auth_state = json.load(f)
            return not self._is_expired(auth_state)
        except Exception:
            return False

    def clear_auth_state(self, user_key: str) -> bool:
        """
        清除指定用户的认证状态

        Args:
            user_key: 用户标识

        Returns:
            True 清除成功，False 清除失败
        """
        try:
            state_file = self._get_state_file(user_key)
            if state_file.exists():
                state_file.unlink()
                logger.info(f"认证状态已清除: {user_key}")
            return True
        except Exception as e:
            logger.error(f"清除认证状态失败: {e}")
            return False

    def clear_all_auth_states(self) -> bool:
        """
        清除所有认证状态

        Returns:
            True 清除成功，False 清除失败
        """
        try:
            for state_file in self.AUTH_DIR.glob("*_state.json"):
                state_file.unlink()
            logger.info("所有认证状态已清除")
            return True
        except Exception as e:
            logger.error(f"清除所有认证状态失败: {e}")
            return False

    def get_auth_info(self, user_key: str) -> Optional[dict]:
        """
        获取认证状态信息（不包含敏感数据）

        Args:
            user_key: 用户标识

        Returns:
            状态信息字典，不存在返回 None
        """
        state_file = self._get_state_file(user_key)

        if not state_file.exists():
            return None

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                auth_state = json.load(f)

            return {
                "user_key": user_key,
                "saved_at": auth_state.get("saved_at"),
                "expire_hours": auth_state.get("expire_hours"),
                "is_expired": self._is_expired(auth_state),
                "url": auth_state.get("url"),
                "cookies_count": len(auth_state.get("cookies", [])),
                "localStorage_keys": list(auth_state.get("localStorage", {}).keys()),
                "sessionStorage_keys": list(auth_state.get("sessionStorage", {}).keys())
            }
        except Exception:
            return None


# ==================== 便捷函数 ====================

def save_auth(page: Page, user_key: str, expire_hours: int = 24) -> bool:
    """
    保存认证状态的便捷函数

    Args:
        page: Playwright 页面对象
        user_key: 用户标识
        expire_hours: 有效期（小时）

    Returns:
        True 成功，False 失败
    """
    return AuthHelper(expire_hours).save_auth_state(page, user_key)


def load_auth(page: Page, user_key: str, base_url: str = None) -> bool:
    """
    加载认证状态的便捷函数

    Args:
        page: Playwright 页面对象
        user_key: 用户标识
        base_url: 基础URL

    Returns:
        True 成功且状态有效，False 失败或已过期
    """
    return AuthHelper().load_auth_state(page, user_key, base_url)


def is_auth_valid(user_key: str) -> bool:
    """
    检查认证状态是否有效的便捷函数

    Args:
        user_key: 用户标识

    Returns:
        True 有效，False 无效或已过期
    """
    return AuthHelper().is_auth_valid(user_key)
