# ========================================
# 光穹课堂测试上下文助手
# ========================================
# 提供光穹课堂测试的公共操作方法
# 通过实例化使用，无需继承
#
# 支持认证状态持久化（免登录）
# ========================================

import allure
from playwright.sync_api import Page

from pages import GqktLoginPage
from pages.gqkt import TopMenuPage, LeftMenuPage
from utils.auth_helper import AuthHelper


class TestContextHelper:
    """
    光穹课堂测试上下文助手

    提供常用的公共方法：
    - 登录并初始化（登录 + 切换学校 + 切换角色）
    - 单独的登录、切换学校、切换角色方法
    - 认证状态保存和加载（免登录）

    使用示例：
        def test_example(self, page, base_url, initial_admin):
            # 创建助手实例
            helper = TestContextHelper()

            # 一键完成登录和初始化（自动尝试免登录）
            helper.login_and_init(page, base_url, initial_admin["username"], initial_admin["password"], "智慧大学", "机构管理员")

            # 后续的测试步骤...
    """

    def __init__(self):
        """初始化助手"""
        self.auth_helper = AuthHelper()

    def login_and_init(
        self,
        page: Page,
        base_url: str,
        username: str,
        password: str,
        school_name: str = "智慧大学",
        role_name: str = "机构管理员",
        use_saved_auth: bool = True,
        save_auth: bool = True
    ) -> tuple:
        """
        登录并初始化（登录 + 切换学校 + 切换角色）

        这是一个便捷方法，一次性完成登录、切换学校和切换角色三个操作。
        支持免登录：如果之前保存过认证状态，会自动尝试加载。

        Args:
            page: Playwright 页面对象
            base_url: 基础URL
            username: 登录用户名
            password: 登录密码
            school_name: 学校名称，默认"智慧大学"
            role_name: 角色名称，默认"机构管理员"
            use_saved_auth: 是否尝试使用保存的认证状态（免登录），默认True
            save_auth: 登录成功后是否保存认证状态，默认True

        Returns:
            tuple: (login_page, top_menu_page) 返回登录页和顶部菜单页对象，方便后续使用

        Raises:
            AssertionError: 如果登录失败

        使用示例：
            helper = TestContextHelper()

            # 使用默认学校和角色（自动尝试免登录）
            helper.login_and_init(page, base_url, "admin", "password123")

            # 指定学校和角色
            helper.login_and_init(page, base_url, "admin", "password123", "测试学校", "教师")

            # 强制重新登录（不使用缓存）
            helper.login_and_init(page, base_url, "admin", "password123", use_saved_auth=False)
        """
        # 生成认证状态的唯一标识（用户名 + 学校 + 角色）
        user_key = f"{username}_{school_name}"

        # 尝试使用保存的认证状态（免登录）
        if use_saved_auth and self.auth_helper.is_auth_valid(user_key):
            with allure.step(f"尝试免登录: {username}"):
                if self._try_restore_auth(page, base_url, user_key):
                    login_page = GqktLoginPage(page, base_url)
                    # 免登录成功后也要切换学校和角色
                    with allure.step(f"切换学校: {school_name}"):
                        top_menu_page = self.switch_school(page, school_name)
                    with allure.step(f"切换角色: {role_name}"):
                        self.switch_role(page, role_name)
                    return login_page, top_menu_page

        # 正常登录流程
        with allure.step(f"登录用户: {username}"):
            login_page = self.do_login(page, base_url, username, password)

        with allure.step(f"切换学校: {school_name}"):
            top_menu_page = self.switch_school(page, school_name)

        with allure.step(f"切换角色: {role_name}"):
            self.switch_role(page, role_name)

        # 保存认证状态供下次免登录使用
        if save_auth:
            with allure.step("保存认证状态"):
                self.auth_helper.save_auth_state(page, user_key)

        return login_page, top_menu_page

    def _try_restore_auth(self, page: Page, base_url: str, user_key: str) -> bool:
        """
        尝试恢复认证状态

        Args:
            page: Playwright 页面对象
            base_url: 基础URL
            user_key: 用户标识

        Returns:
            True 恢复成功且登录有效，False 恢复失败或登录已失效
        """
        try:
            # 免密登陆时进入 /console 页面
            console_url = base_url.rstrip("/") + "/console"
            if not self.auth_helper.load_auth_state(page, user_key, console_url):
                return False

            # 验证登录是否真的有效（检查页面是否跳转到登录页）
            login_page = GqktLoginPage(page, base_url)
            if login_page.is_login_success():
                allure.attach("免登录成功", "使用缓存的认证状态", allure.attachment_type.TEXT)
                return True

            # 登录已失效，清除缓存
            self.auth_helper.clear_auth_state(user_key)
            return False

        except Exception as e:
            allure.attach(str(e), "免登录失败", allure.attachment_type.TEXT)
            return False

    def do_login(self, page: Page, base_url: str, username: str, password: str) -> GqktLoginPage:
        """
        执行登录操作

        Args:
            page: Playwright 页面对象
            base_url: 基础URL
            username: 登录用户名
            password: 登录密码

        Returns:
            GqktLoginPage: 登录页对象

        Raises:
            AssertionError: 如果登录失败
        """
        login_page = GqktLoginPage(page, base_url)
        login_page.goto().login(username, password)
        assert login_page.is_login_success(), "登录失败"
        return login_page

    def switch_school(self, page: Page, school_name: str) -> TopMenuPage:
        """
        切换学校

        Args:
            page: Playwright 页面对象
            school_name: 学校名称

        Returns:
            TopMenuPage: 顶部菜单页对象
        """
        menu_page = TopMenuPage(page)
        menu_page.switch_school(school_name)
        return menu_page

    def switch_role(self, page: Page, role_name: str) -> TopMenuPage:
        """
        切换角色

        Args:
            page: Playwright 页面对象
            role_name: 角色名称

        Returns:
            TopMenuPage: 顶部菜单页对象
        """
        menu_page = TopMenuPage(page)
        menu_page.switch_role(role_name)
        return menu_page

    def click_left_menu_item(self, page: Page, menu_name: str) -> LeftMenuPage:
        """
        点击左侧菜单项
        """
        left_menu_page = LeftMenuPage(page)
        left_menu_page.click_left_menu_item(menu_name)
        return page
