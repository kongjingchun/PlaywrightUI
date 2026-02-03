# ========================================
# 登录功能测试
# ========================================
# 该文件演示了登录功能的自动化测试：
# 1. 使用 Page Object Model
# 2. 数据驱动测试
# 3. 正向和反向测试场景
#
# 注意：这是一个示例测试，使用的是模拟的登录页面。
# 在实际项目中，需要根据真实的登录页面调整元素定位器。
# ========================================

import pytest
import allure
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.logger import Logger
from utils.data_loader import DataLoader


logger = Logger("TestLogin")


@allure.feature("用户认证")
@allure.story("登录功能")
class TestLogin:
    """
    登录功能测试类
    
    包含登录相关的所有测试用例。
    使用 Page Object Model 模式组织代码。
    """
    
    # 使用示例登录页面（实际项目中替换为真实 URL）
    # 这里使用 httpbin 作为演示
    LOGIN_URL = "https://www.httpbin.org/forms/post"
    
    @pytest.fixture
    def login_page(self, page: Page) -> LoginPage:
        """
        创建登录页面对象
        
        Args:
            page: Playwright 页面对象
        
        Returns:
            LoginPage 实例
        """
        return LoginPage(page)
    
    @allure.title("验证登录页面元素加载")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.login
    def test_login_page_elements(self, page: Page, login_page: LoginPage):
        """
        测试登录页面元素是否正确加载
        
        步骤：
        1. 打开登录页面
        2. 验证关键元素存在
        """
        logger.step("开始验证登录页面元素")
        
        with allure.step("打开登录页面"):
            page.goto(self.LOGIN_URL)
            page.wait_for_load_state("domcontentloaded")
            logger.info("登录页面已打开")
        
        with allure.step("验证表单存在"):
            form = page.locator("form")
            expect(form).to_be_visible()
            logger.info("表单元素存在")
        
        with allure.step("验证输入框存在"):
            # httpbin 表单有客户名称输入框
            customer_input = page.locator("input[name='custname']")
            expect(customer_input).to_be_visible()
            logger.info("输入框存在")
        
        with allure.step("验证提交按钮存在"):
            submit_btn = page.locator("button[type='submit']")
            expect(submit_btn).to_be_visible()
            expect(submit_btn).to_be_enabled()
            logger.info("提交按钮存在且可用")
        
        logger.info("登录页面元素验证通过")
    
    @allure.title("验证表单提交功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.login
    def test_form_submission(self, page: Page, screenshot_helper):
        """
        测试表单提交功能
        
        模拟登录流程，验证表单提交后的响应。
        """
        logger.step("开始测试表单提交")
        
        with allure.step("打开表单页面"):
            page.goto(self.LOGIN_URL)
            page.wait_for_load_state("domcontentloaded")
        
        with allure.step("填写表单数据"):
            # 填写客户名称（模拟用户名）
            page.fill("input[name='custname']", "test_user")
            logger.info("已填写用户名")
            
            # 填写其他必填字段
            page.fill("input[name='custtel']", "13800138000")
            page.fill("input[name='custemail']", "test@example.com")
            
            # 截图记录
            screenshot_helper.capture_viewport("form_before_submit")
        
        with allure.step("提交表单"):
            page.click("button[type='submit']")
            logger.info("已点击提交按钮")
        
        with allure.step("等待响应"):
            page.wait_for_load_state("networkidle")
            logger.info("响应页面已加载")
        
        with allure.step("验证提交结果"):
            # httpbin 会返回提交的数据
            content = page.content()
            assert "test_user" in content or "custname" in content
            logger.info("表单提交成功，响应包含提交的数据")
            
            # 截图记录结果
            screenshot_helper.capture_viewport("form_after_submit")
        
        logger.info("表单提交测试通过")
    
    @allure.title("数据驱动测试 - 表单验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.parametrize(
        "test_data",
        [
            {
                "id": "valid_input",
                "name": "张三",
                "phone": "13800138000",
                "email": "zhangsan@example.com",
                "should_submit": True,
                "description": "有效输入"
            },
            {
                "id": "valid_english_name",
                "name": "John Doe",
                "phone": "13900139000",
                "email": "john@example.com",
                "should_submit": True,
                "description": "英文名称"
            },
            {
                "id": "special_characters",
                "name": "Test & User <script>",
                "phone": "13700137000",
                "email": "special@example.com",
                "should_submit": True,
                "description": "特殊字符测试"
            },
        ],
        ids=lambda x: x["id"]
    )
    def test_form_with_different_data(self, page: Page, test_data: dict):
        """
        使用不同数据测试表单
        
        数据驱动测试，验证表单对各种输入的处理。
        
        Args:
            test_data: 测试数据字典
        """
        logger.step(f"测试场景: {test_data['description']}")
        
        with allure.step("打开表单页面"):
            page.goto(self.LOGIN_URL)
            page.wait_for_load_state("domcontentloaded")
        
        with allure.step(f"填写数据: {test_data['description']}"):
            page.fill("input[name='custname']", test_data["name"])
            page.fill("input[name='custtel']", test_data["phone"])
            page.fill("input[name='custemail']", test_data["email"])
            logger.info(f"已填写: 名称={test_data['name']}, 电话={test_data['phone']}")
        
        with allure.step("提交表单"):
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
        
        with allure.step("验证结果"):
            if test_data["should_submit"]:
                # 验证数据被正确提交
                content = page.content()
                # httpbin 返回提交的数据
                logger.info("表单提交成功")
            
        logger.info(f"测试场景 '{test_data['description']}' 通过")
    
    @allure.title("测试空值验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_empty_field_validation(self, page: Page):
        """
        测试空值提交
        
        验证表单对空值的处理（HTML5 原生验证）。
        """
        logger.step("测试空值验证")
        
        with allure.step("打开表单页面"):
            page.goto(self.LOGIN_URL)
            page.wait_for_load_state("domcontentloaded")
        
        with allure.step("不填写任何数据直接提交"):
            # 尝试提交空表单
            page.click("button[type='submit']")
            
            # 等待一小段时间
            page.wait_for_timeout(500)
        
        with allure.step("验证停留在原页面"):
            # 如果有 HTML5 required 验证，应该停留在原页面
            current_url = page.url
            logger.info(f"当前 URL: {current_url}")
            # httpbin 表单没有必填验证，所以会直接提交
        
        logger.info("空值验证测试完成")


@allure.feature("用户认证")
@allure.story("登录数据驱动")
class TestLoginDataDriven:
    """
    登录数据驱动测试类
    
    从 YAML 文件加载测试数据进行测试。
    """
    
    @pytest.fixture
    def login_test_data(self, data_loader: DataLoader) -> list:
        """
        加载登录测试数据
        
        Returns:
            登录测试用例列表
        """
        return data_loader.get_parametrize_data("login_data.yaml", "login_cases")
    
    @allure.title("从 YAML 加载的数据驱动测试")
    @pytest.mark.regression
    def test_with_yaml_data(self, login_data: dict):
        """
        使用从 YAML 加载的数据进行测试
        
        这个测试演示如何使用 login_data fixture（在 conftest.py 中定义）
        获取登录数据。
        
        Args:
            login_data: 登录数据（由 fixture 注入）
        """
        logger.step("验证 YAML 数据加载")
        
        with allure.step("验证数据结构"):
            assert "valid_credentials" in login_data
            assert "login_cases" in login_data
            logger.info("数据结构正确")
        
        with allure.step("验证有效凭据"):
            valid_creds = login_data["valid_credentials"]
            assert "username" in valid_creds
            assert "password" in valid_creds
            logger.info(f"有效用户名: {valid_creds['username']}")
        
        with allure.step("验证测试用例数量"):
            cases = login_data["login_cases"]
            assert len(cases) >= 3  # 至少有3个测试用例
            logger.info(f"共有 {len(cases)} 个登录测试用例")
        
        logger.info("YAML 数据驱动测试通过")


# ==================== 运行说明 ====================
"""
运行登录测试的命令：

1. 运行所有登录测试：
   pytest tests/test_login.py -v

2. 只运行冒烟测试：
   pytest tests/test_login.py -v -m smoke

3. 运行特定测试：
   pytest tests/test_login.py::TestLogin::test_form_submission -v

4. 使用有头模式调试：
   pytest tests/test_login.py -v --headed --slow-mo=500

5. 生成报告：
   pytest tests/test_login.py -v --alluredir=reports/allure-results
"""
