# ========================================
# 光穹课堂登录页面
# ========================================
# 继承 BasePage，使用基类方法操作元素
# 日志在 BasePage 中统一输出，Page 层不写 log
# ========================================

from typing import Optional
from playwright.sync_api import Page
from base.base_page import BasePage
import allure

from config.env_config import EnvConfig


class GqktLoginPage(BasePage):
    """
    光穹课堂登录页面

    设计原则：
    - 继承 BasePage，复用基类方法
    - Page 层不写 log，日志由 BasePage 统一输出
    - 方法返回 self 支持链式调用
    - URL 从配置或参数获取，不写死

    使用方法：
        # 使用环境配置的 base_url
        login_page = GqktLoginPage(page)

        # 或指定 base_url（如从 fixture 注入）
        login_page = GqktLoginPage(page, base_url="https://www.gqkt.cn")

        login_page.goto().login("admin", "123456")
    """

    # 登录路径（相对 base_url）
    LOGIN_PATH = "/login"

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page)
        # base_url 优先使用传入参数，否则从环境配置获取
        self._base_url = base_url or EnvConfig().base_url or "https://www.gqkt.cn"
        self._login_url = self._base_url.rstrip("/") + self.LOGIN_PATH

        # ========== 元素定位器 ==========
        self.username_input = page.get_by_placeholder("请输入您的账户")
        self.password_input = page.get_by_placeholder("请输入您的密码")
        self.login_button = page.get_by_role("button", name="登录")

    # ==================== 页面导航 ====================

    @allure.step("打开登录页面")
    def goto(self) -> "GqktLoginPage":
        """打开登录页面"""
        self.navigate_to(self._login_url)
        return self

    # ==================== 元素操作 ====================

    @allure.step("输入账号: {username}")
    def enter_username(self, username: str) -> "GqktLoginPage":
        """输入账号"""
        self.fill_input(self.username_input, username)
        return self

    @allure.step("输入密码")
    def enter_password(self, password: str) -> "GqktLoginPage":
        """输入密码"""
        self.fill_input(self.password_input, password)
        return self

    @allure.step("点击登录按钮")
    def click_login(self) -> "GqktLoginPage":
        """点击登录按钮"""
        self.click_element(self.login_button)
        self.wait_for_load_state("networkidle")
        return self

    # ==================== 业务方法 ====================

    @allure.step("登录: {username}")
    def login(self, username: str, password: str) -> "GqktLoginPage":
        """
        执行登录（完整登录流程）

        Args:
            username: 账号
            password: 密码
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self

    # ==================== 断言方法 ====================

    def is_login_success(self) -> bool:
        """检查是否登录成功"""
        try:
            self.page.wait_for_url(lambda url: "/login" not in url, timeout=10000)
            # 使用基类的 logger
            self.logger.info(f"✓ 登录成功，跳转到: {self.page.url}")
            return True
        except Exception as e:
            self.logger.error(f"✗ 登录失败: {e}")
            return False

    def get_error_message(self) -> str:
        """获取错误提示信息"""
        error_element = self.page.locator(".el-message--error, .error-message")
        if error_element.is_visible():
            return error_element.inner_text()
        return ""
