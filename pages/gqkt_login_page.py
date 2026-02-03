# ========================================
# 光穹课堂登录页面 - 简化版
# ========================================

from playwright.sync_api import Page
import allure


class GqktLoginPage:
    """
    光穹课堂登录页面
    
    简化设计：
    - 直接暴露元素定位器，不为每个元素写方法
    - 只封装核心业务方法（如 login）
    """
    
    URL = "https://www.gqkt.cn/login"
    
    def __init__(self, page: Page):
        self.page = page
        
        # ========== 元素定位器（直接暴露，不用写 getter 方法）==========
        self.username_input = page.get_by_placeholder("请输入您的账户")
        self.password_input = page.get_by_placeholder("请输入您的密码")
        self.login_button = page.get_by_role("button", name="登录")
    
    def goto(self):
        """打开登录页面"""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("domcontentloaded")
    
    @allure.step("登录: {username}")
    def login(self, username: str, password: str):
        """
        执行登录（核心业务方法，值得封装）
        
        Args:
            username: 账号
            password: 密码
        """
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        self.page.wait_for_load_state("networkidle")
    
    def is_login_success(self) -> bool:
        """检查是否登录成功"""
        try:
            self.page.wait_for_url(lambda url: "/login" not in url, timeout=10000)
            return True
        except:
            return False
