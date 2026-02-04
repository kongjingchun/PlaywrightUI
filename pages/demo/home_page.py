# ========================================
# 首页 - HomePage
# ========================================
# 这是网站首页的 Page Object，演示了更多元素交互方式。
# 包含搜索、导航、用户操作等功能。
# ========================================

from playwright.sync_api import Page
from typing import List
import allure
from base.base_page import BasePage


class HomePage(BasePage):
    """
    首页类
    
    封装首页的元素和操作方法，包括：
    - 搜索功能
    - 导航菜单
    - 用户信息展示
    - 常用快捷操作
    
    使用方法：
        home_page = HomePage(page)
        home_page.search("关键词")
        home_page.navigate_to_category("电子产品")
    """
    
    def __init__(self, page: Page):
        """
        初始化首页
        
        Args:
            page: Playwright 的 Page 对象
        """
        super().__init__(page)
        
        # ==================== 头部导航元素 ====================
        # Logo - 点击返回首页
        self.logo = page.locator("[data-testid='logo'], .logo, #logo")
        
        # 搜索相关元素
        self.search_input = page.locator(
            "[data-testid='search-input'], #search, input[name='search']"
        )
        self.search_button = page.locator(
            "[data-testid='search-button'], #search-btn, button[type='submit']"
        )
        self.search_suggestions = page.locator(".search-suggestions li")
        
        # 用户信息区域
        self.user_dropdown = page.locator(
            "[data-testid='user-dropdown'], .user-dropdown"
        )
        self.username_display = page.locator(
            "[data-testid='username-display'], .username"
        )
        
        # ==================== 主导航菜单 ====================
        self.nav_menu = page.locator("nav, .nav-menu, #main-nav")
        self.nav_items = page.locator("nav a, .nav-item")
        
        # ==================== 页面主体内容 ====================
        self.main_content = page.locator("main, .main-content, #content")
        
        # 商品/内容列表（通用）
        self.item_cards = page.locator(".item-card, .product-card, .card")
        
        # ==================== 页脚 ====================
        self.footer = page.locator("footer, .footer")
        
        # ==================== 通知/消息 ====================
        self.notification_badge = page.locator(
            "[data-testid='notification-badge'], .notification-badge"
        )
        self.notification_dropdown = page.locator(".notification-dropdown")
    
    # ==================== 搜索相关方法 ====================
    
    @allure.step("搜索: {keyword}")
    def search(self, keyword: str, press_enter: bool = True) -> "HomePage":
        """
        执行搜索操作
        
        Args:
            keyword: 搜索关键词
            press_enter: 是否按回车键提交搜索（默认True）
        
        Returns:
            返回 self 以支持链式调用
        
        使用方法：
            # 输入并搜索
            home_page.search("iPhone")
            
            # 仅输入，不提交
            home_page.search("iPhone", press_enter=False)
        """
        self.logger.info(f"搜索关键词: {keyword}")
        
        # 清空并输入搜索词
        self.fill_input(self.search_input, keyword)
        
        if press_enter:
            # 按回车键提交搜索
            self.search_input.press("Enter")
            self.wait_for_load_state("networkidle")
        
        return self
    
    @allure.step("点击搜索按钮")
    def click_search_button(self) -> "HomePage":
        """
        点击搜索按钮提交搜索
        
        Returns:
            返回 self 以支持链式调用
        """
        self.click_element(self.search_button)
        self.wait_for_load_state("networkidle")
        return self
    
    @allure.step("获取搜索建议")
    def get_search_suggestions(self) -> List[str]:
        """
        获取搜索建议列表
        
        在搜索框输入内容后，获取下拉显示的搜索建议。
        
        Returns:
            搜索建议文本列表
        """
        suggestions = []
        
        # 等待搜索建议出现
        if self.is_visible(self.search_suggestions, timeout=3000):
            count = self.search_suggestions.count()
            for i in range(count):
                text = self.search_suggestions.nth(i).inner_text()
                suggestions.append(text)
        
        self.logger.info(f"获取到 {len(suggestions)} 条搜索建议")
        return suggestions
    
    @allure.step("选择搜索建议: {index}")
    def select_search_suggestion(self, index: int = 0) -> "HomePage":
        """
        选择搜索建议
        
        Args:
            index: 建议项的索引（从0开始）
        
        Returns:
            返回 self 以支持链式调用
        """
        self.logger.info(f"选择第 {index + 1} 条搜索建议")
        self.search_suggestions.nth(index).click()
        self.wait_for_load_state("networkidle")
        return self
    
    # ==================== 导航相关方法 ====================
    
    @allure.step("点击Logo返回首页")
    def click_logo(self) -> "HomePage":
        """
        点击Logo返回首页
        
        Returns:
            返回 self 以支持链式调用
        """
        self.logger.info("点击Logo返回首页")
        self.click_element(self.logo)
        self.wait_for_load_state("networkidle")
        return self
    
    @allure.step("导航到分类: {category_name}")
    def navigate_to_category(self, category_name: str) -> "HomePage":
        """
        通过导航菜单进入指定分类
        
        Args:
            category_name: 分类名称
        
        Returns:
            返回 self 以支持链式调用
        """
        self.logger.info(f"导航到分类: {category_name}")
        
        # 查找包含指定文本的导航项并点击
        nav_item = self.page.locator(f"nav a:has-text('{category_name}')")
        self.click_element(nav_item)
        self.wait_for_load_state("networkidle")
        
        return self
    
    @allure.step("获取所有导航菜单项")
    def get_nav_items(self) -> List[str]:
        """
        获取所有导航菜单项的文本
        
        Returns:
            导航菜单项文本列表
        """
        items = []
        count = self.nav_items.count()
        
        for i in range(count):
            text = self.nav_items.nth(i).inner_text()
            if text.strip():  # 过滤空白项
                items.append(text.strip())
        
        self.logger.info(f"导航菜单项: {items}")
        return items
    
    # ==================== 用户相关方法 ====================
    
    @allure.step("获取当前登录用户名")
    def get_logged_in_username(self) -> str:
        """
        获取当前登录用户的用户名
        
        Returns:
            用户名字符串，未登录返回空字符串
        """
        try:
            if self.is_visible(self.username_display, timeout=3000):
                username = self.username_display.inner_text()
                self.logger.info(f"当前登录用户: {username}")
                return username
        except:
            pass
        return ""
    
    @allure.step("打开用户下拉菜单")
    def open_user_dropdown(self) -> "HomePage":
        """
        打开用户下拉菜单
        
        Returns:
            返回 self 以支持链式调用
        """
        self.logger.info("打开用户下拉菜单")
        self.click_element(self.user_dropdown)
        return self
    
    @allure.step("检查用户是否已登录")
    def is_user_logged_in(self) -> bool:
        """
        检查用户是否已登录
        
        Returns:
            True 如果已登录
        """
        return self.is_visible(self.username_display, timeout=3000)
    
    # ==================== 内容相关方法 ====================
    
    @allure.step("获取页面上的卡片数量")
    def get_item_count(self) -> int:
        """
        获取页面上显示的项目/商品数量
        
        Returns:
            项目数量
        """
        count = self.item_cards.count()
        self.logger.info(f"页面上共有 {count} 个项目卡片")
        return count
    
    @allure.step("点击第 {index} 个项目卡片")
    def click_item_card(self, index: int = 0) -> "HomePage":
        """
        点击指定的项目卡片
        
        Args:
            index: 卡片索引（从0开始）
        
        Returns:
            返回 self 以支持链式调用
        """
        self.logger.info(f"点击第 {index + 1} 个项目卡片")
        self.item_cards.nth(index).click()
        self.wait_for_load_state("networkidle")
        return self
    
    @allure.step("获取所有项目卡片标题")
    def get_item_titles(self) -> List[str]:
        """
        获取所有项目卡片的标题
        
        Returns:
            标题列表
        """
        titles = []
        count = self.item_cards.count()
        
        for i in range(count):
            # 尝试从卡片中获取标题元素
            title_locator = self.item_cards.nth(i).locator("h2, h3, .title, .card-title").first
            try:
                if title_locator.is_visible():
                    titles.append(title_locator.inner_text())
            except:
                pass
        
        self.logger.info(f"获取到 {len(titles)} 个项目标题")
        return titles
    
    # ==================== 通知相关方法 ====================
    
    @allure.step("获取未读通知数量")
    def get_notification_count(self) -> int:
        """
        获取未读通知数量
        
        Returns:
            未读通知数量，没有通知返回0
        """
        try:
            if self.is_visible(self.notification_badge, timeout=2000):
                badge_text = self.notification_badge.inner_text()
                count = int(badge_text) if badge_text.isdigit() else 0
                self.logger.info(f"未读通知数量: {count}")
                return count
        except:
            pass
        return 0
    
    @allure.step("打开通知面板")
    def open_notifications(self) -> "HomePage":
        """
        打开通知下拉面板
        
        Returns:
            返回 self 以支持链式调用
        """
        self.logger.info("打开通知面板")
        self.click_element(self.notification_badge)
        self.wait_for_element_visible(self.notification_dropdown)
        return self
    
    # ==================== 页面验证方法 ====================
    
    @allure.step("验证首页加载成功")
    def verify_page_loaded(self) -> bool:
        """
        验证首页是否成功加载
        
        检查关键元素是否存在来判断页面是否正常加载。
        
        Returns:
            True 如果页面加载成功
        """
        try:
            # 检查Logo是否可见
            self.wait_for_element_visible(self.logo, timeout=10000)
            
            # 检查搜索框是否可见
            self.wait_for_element_visible(self.search_input, timeout=5000)
            
            # 检查主内容区域是否可见
            self.wait_for_element_visible(self.main_content, timeout=5000)
            
            self.logger.info("首页加载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"首页加载失败: {str(e)}")
            self.take_screenshot("homepage_load_failed")
            return False
