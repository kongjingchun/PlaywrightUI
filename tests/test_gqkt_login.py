# ========================================
# 光穹课堂登录测试
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt_login_page import GqktLoginPage
from utils.data_loader import load_yaml


# ========== 模块级加载数据 ==========
DATA = load_yaml("gqkt_data.yaml")


@allure.feature("光穹课堂")
@allure.story("用户登录")
class TestGqktLogin:
    """
    光穹课堂登录测试类
    
    测试用例按照 Page Object Model 规范编写：
    1. 页面对象在测试用例中创建，page 通过 pytest fixture 注入
    2. 页面对象方法返回 self，支持链式调用
    3. 断言在测试用例中，不在页面对象中
    """
    
    @pytest.mark.run(order=100)
    @pytest.mark.smoke
    @allure.title("登录成功")
    def test_001_login_success(self, page: Page):
        """
        测试登录成功流程
        
        Args:
            page: Playwright Page 实例（通过 pytest-playwright 注入）
        """
        # 获取测试数据
        username = DATA["login"]["username"]
        password = DATA["login"]["password"]
        
        with allure.step("打开登录页面并执行登录"):
            login_page = GqktLoginPage(page)
            # 链式调用
            login_page.goto().login(username, password)
        
        with allure.step("断言登录成功"):
            assert login_page.is_login_success(), "登录失败，未跳转到首页"
    
    @pytest.mark.run(order=101)
    @pytest.mark.smoke
    @allure.title("登录成功 - 分步操作")
    def test_002_login_success_step_by_step(self, page: Page):
        """
        测试登录成功流程（分步操作演示链式调用）
        
        Args:
            page: Playwright Page 实例
        """
        # 获取测试数据
        username = DATA["login"]["username"]
        password = DATA["login"]["password"]
        
        with allure.step("创建页面对象并打开登录页"):
            login_page = GqktLoginPage(page)
            login_page.goto()
        
        with allure.step("输入账号密码并点击登录"):
            # 演示链式调用
            login_page.enter_username(username).enter_password(password).click_login()
        
        with allure.step("断言登录成功"):
            assert login_page.is_login_success(), "登录失败"
            # 断言跳转到了控制台页面
            assert "/console" in page.url or "/login" not in page.url, "未跳转到正确页面"


# ==================== 运行命令 ====================
"""
# 有界面运行
pytest tests/test_gqkt_login.py -v --headed

# 无界面运行
pytest tests/test_gqkt_login.py -v

# 生成 Allure 报告
pytest tests/test_gqkt_login.py -v --headed --alluredir=reports/allure-results
allure serve reports/allure-results
"""
