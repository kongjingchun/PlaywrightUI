# ========================================
# 演示测试 - 展示框架所有功能
# ========================================
# 该文件是一个完整的演示测试，展示了框架的所有核心功能：
# 1. Page Object Model (POM) 使用
# 2. 数据驱动测试
# 3. Allure 报告集成
# 4. 日志记录
# 5. 截图功能
# 6. 等待机制
# 7. 断言方法
# 8. 测试分组和标记
# 
# 运行方法：
#   pytest tests/test_demo.py -v --headed
# ========================================

import pytest
import allure
from playwright.sync_api import Page, expect

# 项目模块导入
from base.base_page import BasePage, PageAssertions
from utils.logger import Logger
from utils.data_loader import DataLoader
from utils.wait_helper import WaitHelper
from utils.allure_helper import (
    AllureHelper, 
    allure_step, 
    allure_feature, 
    allure_story,
    allure_severity,
    allure_title,
    allure_description
)


# ==================== 创建日志实例 ====================
logger = Logger("TestDemo")


# ==================== 测试类：基础功能演示 ====================

@allure.feature("演示测试")
@allure.story("基础功能")
class TestBasicFeatures:
    """
    基础功能测试类
    
    演示框架的基本使用方法，包括：
    - 页面导航
    - 元素定位和交互
    - 断言
    - 日志记录
    """
    
    @allure.title("测试页面导航功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_page_navigation(self, page: Page, base_url: str):
        """
        测试页面导航功能
        
        步骤：
        1. 打开首页
        2. 验证页面标题
        3. 验证 URL
        
        Args:
            page: Playwright 页面对象（由 fixture 注入）
            base_url: 基础 URL（由 fixture 注入）
        """
        # ========== 步骤1：记录测试开始 ==========
        logger.step("开始测试页面导航")
        
        # ========== 步骤2：导航到页面 ==========
        with allure.step(f"打开页面: {base_url}"):
            page.goto(base_url)
            logger.info(f"已导航到: {base_url}")
        
        # ========== 步骤3：等待页面加载 ==========
        with allure.step("等待页面加载完成"):
            page.wait_for_load_state("domcontentloaded")
            logger.info("页面加载完成")
        
        # ========== 步骤4：验证 URL ==========
        with allure.step("验证当前 URL"):
            current_url = page.url
            logger.info(f"当前 URL: {current_url}")
            
            # 使用 Playwright 内置断言
            expect(page).to_have_url(f"{base_url}/**")
        
        # ========== 步骤5：记录测试完成 ==========
        logger.info("页面导航测试通过")
    
    @allure.title("测试元素等待和定位")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_element_waiting(self, page: Page, base_url: str):
        """
        测试元素等待功能
        
        演示如何使用等待助手等待各种条件。
        """
        logger.step("开始测试元素等待")
        
        # 创建等待助手
        wait_helper = WaitHelper(page)
        
        with allure.step("导航到页面"):
            page.goto(base_url)
        
        with allure.step("等待页面加载"):
            # 方法1：使用内置的 wait_for_load_state
            page.wait_for_load_state("networkidle")
            
            # 方法2：使用自定义条件等待
            wait_helper.wait_for_condition(
                lambda: page.locator("body").is_visible(),
                timeout=10000,
                message="等待 body 元素可见"
            )
        
        with allure.step("验证页面元素"):
            # 验证 body 元素存在
            body = page.locator("body")
            expect(body).to_be_visible()
            logger.info("body 元素可见")
        
        logger.info("元素等待测试通过")
    
    @allure.title("测试截图功能")
    @allure.severity(allure.severity_level.MINOR)
    def test_screenshot_feature(self, page: Page, base_url: str, screenshot_helper):
        """
        测试截图功能
        
        演示如何使用截图助手保存截图。
        
        Args:
            screenshot_helper: 截图助手（由 fixture 注入）
        """
        logger.step("开始测试截图功能")
        
        with allure.step("导航到页面"):
            page.goto(base_url)
            page.wait_for_load_state("domcontentloaded")
        
        with allure.step("截取完整页面"):
            # 截取完整页面（会自动滚动）
            filepath = screenshot_helper.capture_full_page("demo_full_page")
            logger.info(f"完整页面截图已保存: {filepath}")
        
        with allure.step("截取可视区域"):
            # 截取当前可视区域
            filepath = screenshot_helper.capture_viewport("demo_viewport")
            logger.info(f"可视区域截图已保存: {filepath}")
        
        logger.info("截图功能测试通过")


# ==================== 测试类：数据驱动演示 ====================

@allure.feature("演示测试")
@allure.story("数据驱动")
class TestDataDriven:
    """
    数据驱动测试类
    
    演示如何从 YAML 文件读取数据进行参数化测试。
    """
    
    @pytest.fixture(scope="class")
    def loader(self):
        """类级别的数据加载器"""
        return DataLoader()
    
    @allure.title("数据驱动测试演示 - {test_case[id]}")
    @pytest.mark.parametrize(
        "test_case",
        [
            {"id": "case_1", "input": "hello", "expected": True},
            {"id": "case_2", "input": "world", "expected": True},
            {"id": "case_3", "input": "", "expected": False},
        ],
        ids=lambda x: x["id"]  # 使用 id 字段作为测试ID
    )
    def test_parametrized_basic(self, page: Page, test_case: dict):
        """
        基本参数化测试
        
        使用 pytest.mark.parametrize 装饰器进行参数化。
        
        Args:
            test_case: 测试数据字典
        """
        logger.info(f"执行测试用例: {test_case['id']}")
        
        with allure.step(f"测试输入: {test_case['input']}"):
            # 这里可以添加实际的测试逻辑
            result = bool(test_case['input'])  # 简单的非空检查
        
        with allure.step("验证结果"):
            assert result == test_case['expected'], \
                f"预期 {test_case['expected']}, 实际 {result}"
        
        logger.info(f"测试用例 {test_case['id']} 通过")
    
    @allure.title("从 YAML 文件加载测试数据")
    def test_load_yaml_data(self, loader: DataLoader):
        """
        测试从 YAML 文件加载数据
        
        Args:
            loader: 数据加载器
        """
        logger.step("测试 YAML 数据加载")
        
        with allure.step("加载登录数据"):
            login_data = loader.load_yaml("login_data.yaml")
            
            # 验证数据加载成功
            assert "valid_credentials" in login_data
            assert "login_cases" in login_data
            
            logger.info(f"成功加载登录数据，包含 {len(login_data['login_cases'])} 个测试用例")
        
        with allure.step("获取嵌套数据"):
            username = loader.get("login_data.yaml", "valid_credentials.username")
            assert username is not None
            logger.info(f"获取到用户名: {username}")
        
        # 附加数据到 Allure 报告
        AllureHelper().attach_json("加载的登录数据", login_data)
        
        logger.info("YAML 数据加载测试通过")


# ==================== 测试类：httpbin.org 实战测试 ====================

@allure.feature("实战测试")
@allure.story("httpbin.org 测试")
class TestHttpbin:
    """
    httpbin.org 实战测试
    
    使用 httpbin.org 提供的测试页面进行实际的 UI 自动化测试。
    httpbin.org 是一个免费的 HTTP 测试服务，提供各种测试端点。
    """
    
    # httpbin.org 的表单页面 URL
    FORMS_URL = "https://www.httpbin.org/forms/post"
    
    @allure.title("测试表单填写和提交")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_form_submission(self, page: Page, screenshot_helper):
        """
        测试表单填写和提交功能
        
        步骤：
        1. 打开 httpbin 的表单页面
        2. 填写所有表单字段
        3. 提交表单
        4. 验证提交结果
        
        这是一个完整的端到端测试示例，展示了：
        - 页面导航
        - 元素定位（多种方式）
        - 表单填写
        - 下拉选择
        - 复选框操作
        - 表单提交
        - 结果验证
        """
        logger.step("开始表单提交测试")
        
        # ========== 步骤1：打开表单页面 ==========
        with allure.step("打开 httpbin 表单页面"):
            page.goto(self.FORMS_URL)
            page.wait_for_load_state("domcontentloaded")
            logger.info(f"已打开表单页面: {self.FORMS_URL}")
            
            # 截图记录初始状态
            screenshot_helper.capture_viewport("form_initial")
        
        # ========== 步骤2：填写客户名称 ==========
        with allure.step("填写客户名称"):
            # 使用 label 文本定位关联的输入框
            custname_input = page.locator("input[name='custname']")
            custname_input.fill("张三")
            logger.info("已填写客户名称: 张三")
        
        # ========== 步骤3：填写电话号码 ==========
        with allure.step("填写电话号码"):
            telephone_input = page.locator("input[name='custtel']")
            telephone_input.fill("13800138000")
            logger.info("已填写电话号码: 13800138000")
        
        # ========== 步骤4：填写邮箱 ==========
        with allure.step("填写邮箱"):
            email_input = page.locator("input[name='custemail']")
            email_input.fill("zhangsan@example.com")
            logger.info("已填写邮箱: zhangsan@example.com")
        
        # ========== 步骤5：选择披萨尺寸 ==========
        with allure.step("选择披萨尺寸"):
            # 选择 Medium 尺寸
            size_radio = page.locator("input[value='medium']")
            size_radio.check()
            logger.info("已选择尺寸: Medium")
        
        # ========== 步骤6：选择配料 ==========
        with allure.step("选择配料"):
            # 选择 Bacon 配料
            bacon_checkbox = page.locator("input[name='topping'][value='bacon']")
            bacon_checkbox.check()
            logger.info("已选择配料: Bacon")
            
            # 选择 Cheese 配料
            cheese_checkbox = page.locator("input[name='topping'][value='cheese']")
            cheese_checkbox.check()
            logger.info("已选择配料: Cheese")
        
        # ========== 步骤7：填写配送时间 ==========
        with allure.step("填写配送时间"):
            time_input = page.locator("input[name='delivery']")
            time_input.fill("18:00")
            logger.info("已填写配送时间: 18:00")
        
        # ========== 步骤8：填写特殊说明 ==========
        with allure.step("填写特殊说明"):
            comments_textarea = page.locator("textarea[name='comments']")
            comments_textarea.fill("请多放芝士，谢谢！这是自动化测试生成的订单。")
            logger.info("已填写特殊说明")
        
        # ========== 步骤9：截图记录填写后的状态 ==========
        with allure.step("截图记录表单填写状态"):
            screenshot_helper.capture_full_page("form_filled")
        
        # ========== 步骤10：提交表单 ==========
        with allure.step("提交表单"):
            submit_button = page.locator("button[type='submit']")
            submit_button.click()
            logger.info("已点击提交按钮")
        
        # ========== 步骤11：等待结果页面 ==========
        with allure.step("等待结果页面加载"):
            page.wait_for_load_state("networkidle")
            logger.info("结果页面已加载")
        
        # ========== 步骤12：验证提交结果 ==========
        with allure.step("验证提交结果"):
            # httpbin 会返回 JSON 格式的提交数据
            page_content = page.content()
            
            # 验证关键数据出现在响应中
            assert "张三" in page_content or "custname" in page_content, \
                "未找到客户名称"
            logger.info("验证通过：响应中包含提交的数据")
            
            # 截图记录结果
            screenshot_helper.capture_full_page("form_result")
        
        # ========== 步骤13：附加结果到报告 ==========
        with allure.step("记录测试结果"):
            AllureHelper().attach_html("提交结果页面", page_content)
        
        logger.info("表单提交测试完成")
    
    @allure.title("测试页面元素交互")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_element_interactions(self, page: Page):
        """
        测试各种元素交互方式
        
        演示 Playwright 的各种元素交互方法。
        """
        logger.step("开始元素交互测试")
        
        with allure.step("打开表单页面"):
            page.goto(self.FORMS_URL)
            page.wait_for_load_state("domcontentloaded")
        
        # ========== 演示各种定位方式 ==========
        with allure.step("演示多种元素定位方式"):
            # 1. 通过 CSS 选择器
            input_by_css = page.locator("input[name='custname']")
            assert input_by_css.is_visible()
            logger.info("CSS 选择器定位成功")
            
            # 2. 通过文本内容
            submit_by_text = page.locator("button:has-text('Submit')")
            assert submit_by_text.is_visible()
            logger.info("文本定位成功")
            
            # 3. 通过 XPath（不推荐，但有时候需要）
            # input_by_xpath = page.locator("//input[@name='custname']")
            
            # 4. 通过角色（role）
            button_by_role = page.get_by_role("button", name="Submit")
            assert button_by_role.is_visible()
            logger.info("角色定位成功")
            
            # 5. 通过 placeholder
            email_by_placeholder = page.get_by_placeholder("you@email.com")
            # 注意：httpbin 的表单可能没有 placeholder
        
        # ========== 演示元素属性获取 ==========
        with allure.step("获取元素属性"):
            input_element = page.locator("input[name='custname']")
            
            # 获取属性
            name_attr = input_element.get_attribute("name")
            logger.info(f"元素 name 属性: {name_attr}")
            
            # 获取输入值
            input_element.fill("测试值")
            input_value = input_element.input_value()
            logger.info(f"输入框的值: {input_value}")
            
            assert input_value == "测试值"
        
        logger.info("元素交互测试完成")
    
    @allure.title("测试等待机制")
    @allure.severity(allure.severity_level.NORMAL)
    def test_wait_mechanisms(self, page: Page):
        """
        测试各种等待机制
        
        演示 Playwright 和框架提供的等待功能。
        """
        logger.step("开始等待机制测试")
        
        wait_helper = WaitHelper(page)
        
        with allure.step("导航并等待"):
            page.goto(self.FORMS_URL)
        
        # ========== 方式1：等待加载状态 ==========
        with allure.step("等待加载状态"):
            # domcontentloaded: DOM 加载完成
            page.wait_for_load_state("domcontentloaded")
            logger.info("DOM 加载完成")
            
            # networkidle: 网络空闲（500ms 内无网络请求）
            page.wait_for_load_state("networkidle")
            logger.info("网络空闲")
        
        # ========== 方式2：等待元素 ==========
        with allure.step("等待元素可见"):
            form = page.locator("form")
            form.wait_for(state="visible")
            logger.info("表单元素可见")
        
        # ========== 方式3：自定义条件等待 ==========
        with allure.step("自定义条件等待"):
            wait_helper.wait_for_condition(
                lambda: page.locator("input").count() > 0,
                timeout=10000,
                message="等待输入框出现"
            )
            logger.info("自定义条件满足")
        
        # ========== 方式4：等待元素数量 ==========
        with allure.step("等待元素数量"):
            wait_helper.wait_for_element_count(
                page.locator("input"),
                expected_count=3,
                comparison=">=",
                timeout=5000
            )
            logger.info("元素数量满足条件")
        
        logger.info("等待机制测试完成")


# ==================== 测试类：断言演示 ====================

@allure.feature("演示测试")
@allure.story("断言方法")
class TestAssertions:
    """
    断言方法测试类
    
    演示 Playwright 的各种断言方法。
    """
    
    @allure.title("测试页面级断言")
    def test_page_assertions(self, page: Page, base_url: str):
        """
        测试页面级别的断言
        """
        logger.step("开始页面断言测试")
        
        with allure.step("导航到页面"):
            page.goto(base_url)
        
        with allure.step("断言 URL"):
            # URL 包含
            expect(page).to_have_url(f"{base_url}/**")
            logger.info("URL 断言通过")
        
        logger.info("页面断言测试完成")
    
    @allure.title("测试元素级断言")
    def test_element_assertions(self, page: Page):
        """
        测试元素级别的断言
        """
        logger.step("开始元素断言测试")
        
        with allure.step("导航到表单页面"):
            page.goto("https://www.httpbin.org/forms/post")
            page.wait_for_load_state("domcontentloaded")
        
        with allure.step("断言元素可见"):
            form = page.locator("form")
            expect(form).to_be_visible()
            logger.info("元素可见断言通过")
        
        with allure.step("断言元素启用"):
            submit_btn = page.locator("button[type='submit']")
            expect(submit_btn).to_be_enabled()
            logger.info("元素启用断言通过")
        
        with allure.step("断言元素数量"):
            inputs = page.locator("input")
            expect(inputs).to_have_count(9)  # 表单中有多个输入框
            logger.info("元素数量断言通过")
        
        with allure.step("断言输入框值"):
            name_input = page.locator("input[name='custname']")
            name_input.fill("测试用户")
            expect(name_input).to_have_value("测试用户")
            logger.info("输入框值断言通过")
        
        logger.info("元素断言测试完成")


# ==================== 标记过滤演示 ====================

@allure.feature("演示测试")
@allure.story("测试标记")
class TestMarkers:
    """
    测试标记演示
    
    演示如何使用 pytest 标记进行测试分组和过滤。
    
    运行方法：
        pytest -m smoke          # 只运行冒烟测试
        pytest -m regression     # 只运行回归测试
        pytest -m "not slow"     # 排除慢速测试
        pytest -m "smoke or regression"  # 运行冒烟或回归测试
    """
    
    @pytest.mark.smoke
    @allure.title("冒烟测试示例")
    def test_smoke_example(self, page: Page):
        """
        冒烟测试
        
        标记为 @pytest.mark.smoke
        用于快速验证核心功能是否正常。
        """
        logger.info("执行冒烟测试")
        page.goto("https://example.com")
        expect(page).to_have_url("https://example.com/")
        logger.info("冒烟测试通过")
    
    @pytest.mark.regression
    @allure.title("回归测试示例")
    def test_regression_example(self, page: Page):
        """
        回归测试
        
        标记为 @pytest.mark.regression
        用于完整的功能验证。
        """
        logger.info("执行回归测试")
        page.goto("https://example.com")
        expect(page.locator("body")).to_be_visible()
        logger.info("回归测试通过")
    
    @pytest.mark.slow
    @allure.title("慢速测试示例")
    def test_slow_example(self, page: Page):
        """
        慢速测试
        
        标记为 @pytest.mark.slow
        执行时间较长的测试。
        """
        logger.info("执行慢速测试")
        import time
        time.sleep(1)  # 模拟耗时操作
        logger.info("慢速测试通过")
    
    @pytest.mark.wip
    @pytest.mark.skip(reason="功能开发中")
    @allure.title("开发中的测试示例")
    def test_wip_example(self):
        """
        开发中的测试
        
        标记为 @pytest.mark.wip (Work In Progress)
        正在开发的功能测试。
        """
        pass


# ==================== 运行说明 ====================
"""
运行测试的命令示例：

1. 运行所有测试：
   pytest tests/test_demo.py -v

2. 运行特定测试类：
   pytest tests/test_demo.py::TestBasicFeatures -v

3. 运行特定测试方法：
   pytest tests/test_demo.py::TestBasicFeatures::test_page_navigation -v

4. 使用有头模式（显示浏览器）：
   pytest tests/test_demo.py -v --headed

5. 使用不同浏览器：
   pytest tests/test_demo.py -v --browser=firefox

6. 只运行冒烟测试：
   pytest tests/test_demo.py -v -m smoke

7. 生成 Allure 报告：
   pytest tests/test_demo.py -v --alluredir=UIreport
   allure serve UIreport

8. 使用慢动作模式调试：
   pytest tests/test_demo.py -v --headed --slow-mo=1000
"""
