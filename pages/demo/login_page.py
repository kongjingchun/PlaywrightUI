# ========================================
# 登录页面 - LoginPage
# ========================================
# 这是一个示例页面类，展示了如何使用 Page Object Model。
# 封装了登录页面的所有元素定位和操作方法。
# ========================================

from playwright.sync_api import Page
import allure
from base.base_page import BasePage


class LoginPage(BasePage):
    """
    登录页面类

    封装登录页面的元素定位和操作方法。

    使用方法：
        # 在测试用例中
        login_page = LoginPage(page)
        login_page.navigate_to_login()
        login_page.login("admin", "password")

        # 验证登录结果
        assert login_page.is_login_successful()

    页面元素：
        - 用户名输入框
        - 密码输入框
        - 登录按钮
        - 记住我复选框
        - 错误提示信息
    """

    # ==================== 页面 URL ====================
    # 定义为类属性，方便复用和修改
    LOGIN_PATH = "/login"

    def __init__(self, page: Page):
        """
        初始化登录页面

        Args:
            page: Playwright 的 Page 对象
        """
        # 调用父类构造函数
        super().__init__(page)

        # ==================== 元素定位器 ====================
        # 使用描述性的变量名，便于理解和维护
        # 推荐使用 data-testid 属性进行定位，这是最稳定的方式

        # 用户名输入框 - 支持多种定位方式
        self.username_input = page.locator(
            "[data-testid='username'], #username, input[name='username']"
        )

        # 密码输入框
        self.password_input = page.locator(
            "[data-testid='password'], #password, input[name='password']"
        )

        # 登录按钮
        self.login_button = page.locator(
            "[data-testid='login-button'], #login-btn, button[type='submit']"
        )

        # 记住我复选框
        self.remember_me_checkbox = page.locator(
            "[data-testid='remember-me'], #remember-me, input[name='remember']"
        )

        # 错误提示信息
        self.error_message = page.locator(
            "[data-testid='error-message'], .error-message, .alert-danger"
        )

        # 登录成功后的元素（用于验证登录状态）
        self.user_avatar = page.locator(
            "[data-testid='user-avatar'], .user-avatar, .avatar"
        )

        # 登出按钮
        self.logout_button = page.locator(
            "[data-testid='logout'], #logout, button:has-text('退出')"
        )

    # ==================== 页面操作方法 ====================

    @allure.step("导航到登录页面")
    def navigate_to_login(self, base_url: str) -> "LoginPage":
        """
        导航到登录页面

        Args:
            base_url: 网站的基础 URL

        Returns:
            返回 self 以支持链式调用

        使用方法：
            login_page.navigate_to_login("https://example.com")
        """
        login_url = f"{base_url}{self.LOGIN_PATH}"
        self.navigate_to(login_url)
        return self

    @allure.step("执行登录操作")
    def login(self, username: str, password: str, remember_me: bool = False) -> "LoginPage":
        """
        执行登录操作

        这是登录页面的核心方法，封装了完整的登录流程。

        Args:
            username: 用户名
            password: 密码
            remember_me: 是否勾选"记住我"

        Returns:
            返回 self 以支持链式调用

        使用方法：
            login_page.login("admin", "password123")
            login_page.login("admin", "password123", remember_me=True)
        """
        self.logger.info(f"开始登录，用户名: {username}")

        # 步骤1：输入用户名
        with allure.step(f"输入用户名: {username}"):
            self.fill_element(self.username_input, username)

        # 步骤2：输入密码（日志中隐藏密码）
        with allure.step("输入密码"):
            self.logger.info("输入密码: ******")
            self.fill_element(self.password_input, password)

        # 步骤3：处理"记住我"复选框
        if remember_me:
            with allure.step("勾选'记住我'"):
                self.check_checkbox(self.remember_me_checkbox, True)

        # 步骤4：点击登录按钮
        with allure.step("点击登录按钮"):
            self.click_element(self.login_button)

        # 等待页面响应
        self.wait_for_load_state("networkidle")

        return self

    @allure.step("检查是否登录成功")
    def is_login_successful(self) -> bool:
        """
        检查登录是否成功

        通过检查用户头像或其他登录后才显示的元素来判断。

        Returns:
            True 如果登录成功，False 如果登录失败
        """
        try:
            # 等待用户头像出现，作为登录成功的标志
            self.user_avatar.wait_for(state="visible", timeout=5000)
            self.logger.info("登录成功：检测到用户头像")
            return True
        except BaseException:
            self.logger.info("登录失败：未检测到用户头像")
            return False

    @allure.step("获取错误提示信息")
    def get_error_message(self) -> str:
        """
        获取登录失败时的错误提示信息

        Returns:
            错误提示文本，如果没有错误提示则返回空字符串
        """
        try:
            if self.error_message.is_visible():
                error_text = self.error_message.inner_text()
                self.logger.info(f"错误提示: {error_text}")
                return error_text
        except BaseException:
            pass
        return ""

    @allure.step("检查错误提示是否显示")
    def is_error_displayed(self) -> bool:
        """
        检查是否显示了错误提示

        Returns:
            True 如果显示了错误提示
        """
        return self.is_visible(self.error_message, timeout=3000)

    @allure.step("执行登出操作")
    def logout(self) -> "LoginPage":
        """
        执行登出操作

        Returns:
            返回 self 以支持链式调用
        """
        self.logger.info("执行登出操作")
        self.click_element(self.logout_button)
        self.wait_for_load_state("networkidle")
        return self

    # ==================== 快捷方法 ====================

    @allure.step("快速登录并验证")
    def login_and_verify(self, username: str, password: str) -> bool:
        """
        执行登录并验证是否成功

        这是一个便捷方法，组合了登录和验证操作。

        Args:
            username: 用户名
            password: 密码

        Returns:
            True 如果登录成功

        Raises:
            AssertionError: 如果登录失败
        """
        self.login(username, password)

        if self.is_login_successful():
            self.logger.info(f"用户 {username} 登录成功")
            return True
        else:
            error = self.get_error_message()
            self.logger.error(f"用户 {username} 登录失败: {error}")
            self.take_screenshot("login_failed")
            raise AssertionError(f"登录失败: {error}")

    @allure.step("输入用户名")
    def enter_username(self, username: str) -> "LoginPage":
        """
        单独输入用户名（不提交）

        Args:
            username: 用户名

        Returns:
            返回 self 以支持链式调用
        """
        self.fill_element(self.username_input, username)
        return self

    @allure.step("输入密码")
    def enter_password(self, password: str) -> "LoginPage":
        """
        单独输入密码（不提交）

        Args:
            password: 密码

        Returns:
            返回 self 以支持链式调用
        """
        self.fill_element(self.password_input, password)
        return self

    @allure.step("点击登录按钮")
    def click_login_button(self) -> "LoginPage":
        """
        点击登录按钮

        Returns:
            返回 self 以支持链式调用
        """
        self.click_element(self.login_button)
        return self
