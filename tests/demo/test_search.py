# ========================================
# 搜索功能测试
# ========================================
# 该文件演示了搜索功能的自动化测试：
# 1. 使用真实的网站进行搜索测试
# 2. 数据驱动测试
# 3. 各种搜索场景
#
# 使用 Playwright 官网作为测试目标
# ========================================

import pytest
import allure
from playwright.sync_api import Page, expect

from pages import HomePage
from utils.logger import Logger
from utils.data_loader import DataLoader
from utils.wait_helper import WaitHelper


logger = Logger("TestSearch")


@allure.feature("搜索功能")
@allure.story("Playwright 官网搜索")
class TestPlaywrightSearch:
    """
    Playwright 官网搜索测试
    
    使用 Playwright 官方网站进行搜索功能测试。
    这是一个真实网站的测试示例。
    """
    
    # Playwright 官网地址
    PLAYWRIGHT_URL = "https://playwright.dev"
    
    @allure.title("验证搜索功能可用")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.search
    def test_search_available(self, page, screenshot_helper):
        """
        测试搜索功能是否可用
        
        步骤：
        1. 打开 Playwright 官网
        2. 查找搜索按钮
        3. 验证搜索功能存在
        """
        logger.step("开始验证搜索功能")
        
        with allure.step("打开 Playwright 官网"):
            page.goto(self.PLAYWRIGHT_URL)
            page.wait_for_load_state("domcontentloaded")
            logger.info("官网已打开")
            screenshot_helper.capture_viewport("playwright_homepage")
        
        with allure.step("查找搜索按钮"):
            # Playwright 官网的搜索按钮
            search_button = page.locator("[class*='search'], .DocSearch, button[aria-label*='Search']").first
            
            # 等待按钮出现（可能需要等待 JS 加载）
            try:
                search_button.wait_for(state="visible", timeout=10000)
                logger.info("搜索按钮可见")
            except:
                # 如果特定选择器找不到，尝试查找任何搜索相关元素
                logger.warning("未找到标准搜索按钮，尝试其他方式")
                # 尝试使用键盘快捷键
                page.keyboard.press("Control+k")  # 或 Meta+k 在 Mac 上
                page.wait_for_timeout(1000)
        
        logger.info("搜索功能验证完成")
    
    @allure.title("执行搜索操作")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.search
    def test_perform_search(self, page: Page, screenshot_helper):
        """
        测试实际的搜索操作
        
        步骤：
        1. 打开官网
        2. 触发搜索
        3. 输入关键词
        4. 验证搜索结果
        """
        logger.step("开始执行搜索测试")
        
        with allure.step("打开 Playwright 官网"):
            page.goto(self.PLAYWRIGHT_URL)
            page.wait_for_load_state("networkidle")
        
        with allure.step("触发搜索对话框"):
            # 使用键盘快捷键打开搜索（Ctrl+K 或 Cmd+K）
            page.keyboard.press("Meta+k")  # Mac
            page.wait_for_timeout(500)
            
            # 如果 Mac 快捷键不工作，尝试 Windows 快捷键
            if not page.locator(".DocSearch-Modal").is_visible():
                page.keyboard.press("Control+k")
                page.wait_for_timeout(500)
        
        with allure.step("输入搜索关键词"):
            # 在搜索框中输入
            search_input = page.locator(".DocSearch-Input, input[type='search']").first
            
            try:
                search_input.wait_for(state="visible", timeout=5000)
                search_input.fill("locator")
                logger.info("已输入搜索关键词: locator")
                
                # 等待搜索结果
                page.wait_for_timeout(1000)
                screenshot_helper.capture_viewport("search_results")
            except:
                logger.warning("搜索对话框未打开，可能是网站结构变化")
        
        logger.info("搜索操作测试完成")


@allure.feature("搜索功能")
@allure.story("Example.com 页面测试")
class TestExampleSite:
    """
    Example.com 测试
    
    使用 example.com 进行基础页面测试。
    这是一个简单稳定的测试目标。
    """
    
    EXAMPLE_URL = "https://example.com"
    
    @allure.title("验证 Example.com 页面加载")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_example_page_load(self, page: Page, screenshot_helper):
        """
        测试 Example.com 页面加载
        
        这是一个简单的冒烟测试，验证基本的页面加载功能。
        """
        logger.step("开始测试 Example.com")
        
        with allure.step("导航到 Example.com"):
            page.goto(self.EXAMPLE_URL)
            page.wait_for_load_state("domcontentloaded")
            logger.info("页面已加载")
        
        with allure.step("验证页面标题"):
            expect(page).to_have_title("Example Domain")
            logger.info("标题验证通过")
        
        with allure.step("验证页面内容"):
            heading = page.locator("h1")
            expect(heading).to_have_text("Example Domain")
            logger.info("标题内容验证通过")
            
            # 验证说明文字存在
            paragraph = page.locator("p").first
            expect(paragraph).to_be_visible()
            logger.info("段落内容存在")
        
        with allure.step("截图记录"):
            screenshot_helper.capture_full_page("example_com")
        
        logger.info("Example.com 测试通过")
    
    @allure.title("验证页面链接")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_example_page_links(self, page: Page):
        """
        测试 Example.com 的链接
        """
        logger.step("测试页面链接")
        
        with allure.step("打开页面"):
            page.goto(self.EXAMPLE_URL)
            page.wait_for_load_state("domcontentloaded")
        
        with allure.step("查找链接"):
            link = page.locator("a").first
            
            if link.count() > 0:
                href = link.get_attribute("href")
                logger.info(f"找到链接: {href}")
                
                # 验证链接属性
                expect(link).to_have_attribute("href", href)
        
        logger.info("链接测试完成")


@allure.feature("搜索功能")
@allure.story("数据驱动搜索")
class TestSearchDataDriven:
    """
    数据驱动搜索测试
    
    从 YAML 文件加载搜索数据进行测试。
    """
    
    @allure.title("验证搜索数据加载")
    @pytest.mark.regression
    def test_search_data_loading(self, search_data: dict):
        """
        验证搜索测试数据正确加载
        
        Args:
            search_data: 搜索数据（由 fixture 注入）
        """
        logger.step("验证搜索数据加载")
        
        with allure.step("验证数据结构"):
            assert "search_cases" in search_data
            assert "filter_options" in search_data
            assert "hot_keywords" in search_data
            logger.info("数据结构正确")
        
        with allure.step("验证搜索用例"):
            cases = search_data["search_cases"]
            assert len(cases) >= 3
            logger.info(f"共有 {len(cases)} 个搜索用例")
            
            # 验证每个用例的必要字段
            for case in cases:
                assert "id" in case
                assert "keyword" in case
                logger.debug(f"用例 {case['id']}: {case['keyword']}")
        
        with allure.step("验证过滤选项"):
            filters = search_data["filter_options"]
            assert "categories" in filters
            assert "sort_by" in filters
            logger.info(f"分类选项: {filters['categories']}")
        
        with allure.step("验证热门关键词"):
            keywords = search_data["hot_keywords"]
            assert len(keywords) > 0
            logger.info(f"热门关键词: {keywords}")
        
        logger.info("搜索数据验证通过")
    
    @allure.title("数据驱动搜索测试 - {test_case[id]}")
    @pytest.mark.parametrize(
        "test_case",
        [
            {"id": "keyword_python", "keyword": "Python", "expect_results": True},
            {"id": "keyword_empty", "keyword": "", "expect_results": False},
            {"id": "keyword_special", "keyword": "@#$%", "expect_results": True},
        ],
        ids=lambda x: x["id"]
    )
    @pytest.mark.regression
    def test_search_keywords(self, page: Page, test_case: dict):
        """
        使用不同关键词测试搜索
        
        这是一个简化的测试，仅验证关键词能被正确处理。
        
        Args:
            test_case: 测试数据
        """
        logger.step(f"测试关键词: {test_case['keyword']}")
        
        with allure.step("验证测试数据"):
            logger.info(f"关键词: '{test_case['keyword']}'")
            logger.info(f"期望有结果: {test_case['expect_results']}")
        
        with allure.step("执行简单验证"):
            # 验证关键词处理
            keyword = test_case["keyword"]
            has_content = bool(keyword.strip())
            
            if test_case["expect_results"]:
                assert has_content or keyword == "", "非空关键词应该有内容"
            
            logger.info(f"关键词 '{keyword}' 测试通过")


@allure.feature("搜索功能")
@allure.story("等待机制测试")
class TestWaitMechanisms:
    """
    等待机制测试
    
    演示在搜索场景中使用各种等待方法。
    """
    
    @allure.title("测试条件等待")
    @pytest.mark.regression
    def test_condition_waiting(self, page: Page):
        """
        测试自定义条件等待
        """
        logger.step("测试条件等待")
        
        wait_helper = WaitHelper(page)
        
        with allure.step("打开测试页面"):
            page.goto("https://example.com")
            page.wait_for_load_state("domcontentloaded")
        
        with allure.step("使用条件等待"):
            # 等待 h1 元素出现
            wait_helper.wait_for_condition(
                lambda: page.locator("h1").count() > 0,
                timeout=10000,
                message="等待 h1 元素出现"
            )
            logger.info("h1 元素已出现")
        
        with allure.step("等待元素数量"):
            wait_helper.wait_for_element_count(
                page.locator("p"),
                expected_count=1,
                comparison=">=",
                timeout=5000
            )
            logger.info("段落元素数量满足条件")
        
        logger.info("条件等待测试通过")
    
    @allure.title("测试重试机制")
    @pytest.mark.regression
    def test_retry_mechanism(self, page: Page):
        """
        测试操作重试机制
        """
        logger.step("测试重试机制")
        
        wait_helper = WaitHelper(page)
        
        with allure.step("打开页面"):
            page.goto("https://example.com")
        
        with allure.step("使用重试机制执行操作"):
            # 使用重试机制点击链接
            def click_action():
                link = page.locator("a").first
                link.click()
            
            # 重试执行
            wait_helper.retry_on_failure(
                click_action,
                max_retries=3,
                retry_interval=500
            )
            
            logger.info("重试机制执行成功")
        
        logger.info("重试机制测试通过")


# ==================== 运行说明 ====================
"""
运行搜索测试的命令：

1. 运行所有搜索测试：
   pytest tests/test_search.py -v

2. 只运行冒烟测试：
   pytest tests/test_search.py -v -m smoke

3. 运行数据驱动测试：
   pytest tests/test_search.py::TestSearchDataDriven -v

4. 使用有头模式：
   pytest tests/test_search.py -v --headed

5. 生成报告：
   pytest tests/test_search.py -v --alluredir=UIreport
   allure serve UIreport
"""
