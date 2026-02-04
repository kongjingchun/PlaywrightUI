# ========================================
# 顶部菜单页面（优化版本）
# ========================================
# 符合 Playwright 最佳实践：
# 1. 使用私有方法消除代码重复
# 2. 充分利用 Locator 懒加载特性
# 3. 保持代码简洁清晰
# ========================================

from playwright.sync_api import Page
from typing import Optional
import allure

from base.base_page import BasePage
from config.env_config import EnvConfig


URL_PATH = "/console"


class TopMenuPage(BasePage):
    """
    顶部菜单页面

    提供学校切换相关的操作方法。
    符合 Playwright 最佳实践的极简设计。
    """

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page)
        self._base_url = base_url or EnvConfig().base_url or "https://www.gqkt.cn"
        self._top_menu_url = self._base_url.rstrip("/") + URL_PATH

        # ========== 元素定位器 ==========
        # Playwright 的 Locator 是懒加载的，这里只是定义"查询计划"
        # 学校下拉框按钮
        self.school_dropdown_button = page.locator("xpath=//div[@class='el-dropdown org-dropdown']")
        # 角色下拉框按钮
        self.role_dropdown_button = page.locator("xpath=//div[@class='role-tag']")

    # ==================== 动态定位器生成方法 ====================
    def _get_school_menuitem(self, school_name: str):
        """
        获取学校菜单项定位器

        Playwright 最佳实践：
        - Locator 是懒加载的，创建成本极低
        - 可以重复调用，不会影响性能
        """
        return self.page.get_by_role("menuitem", name=school_name)

    def _get_role_menuitem(self, role_name: str):
        """
        获取角色菜单项定位器
        """
        return self.page.get_by_role("menuitem", name=role_name)

    # ==================== 页面导航 ====================

    @allure.step("打开顶部菜单页面")
    def goto(self) -> "TopMenuPage":
        """
        打开顶部菜单页面

        Returns:
            self，支持链式调用
        """
        self.navigate_to(self._top_menu_url)
        return self

    # ==================== 业务操作 ====================

    @allure.step("切换学校: {school_name}")
    def switch_school(self, school_name: str) -> "TopMenuPage":
        """
        切换学校

        Args:
            school_name: 学校名称

        Returns:
            self，支持链式调用

        使用示例：
            menu_page.switch_school("测试学校")
        """
        self.click_element(self.school_dropdown_button)
        self.click_element(self._get_school_menuitem(school_name))
        return self

    @allure.step("切换角色: {role_name}")
    def switch_role(self, role_name: str) -> "TopMenuPage":
        """
        切换角色
        """
        self.click_element(self.role_dropdown_button)
        self.click_element(self._get_role_menuitem(role_name))
        return self
