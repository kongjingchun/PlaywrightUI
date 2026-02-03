# ========================================
# 光穹课堂登录测试 - 简化版
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt_login_page import GqktLoginPage
from utils.data_loader import load_yaml


# ========== 直接加载数据（不用 fixture）==========
DATA = load_yaml("gqkt_data.yaml")


@allure.feature("光穹课堂")
class TestGqktLogin:
    """光穹课堂登录测试"""
    
    @allure.title("登录成功")
    @pytest.mark.smoke
    def test_login_success(self, page: Page):
        """
        测试登录成功
        
        简化写法：
        - 数据直接从模块级变量读取
        - Page 对象在测试中直接创建
        """
        # 获取测试数据
        username = DATA["login"]["username"]
        password = DATA["login"]["password"]
        
        # 创建页面对象
        login_page = GqktLoginPage(page)
        
        # 执行测试
        login_page.goto()
        login_page.login(username, password)
        
        # 断言
        assert login_page.is_login_success(), "登录失败"
        print(f"✓ 登录成功，跳转到: {page.url}")


# ==================== 运行命令 ====================
"""
pytest tests/test_gqkt_login.py -v --headed
"""
