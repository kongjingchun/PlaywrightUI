# ========================================
# 左侧菜单页面
# ========================================

import allure
from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig

URL_PATH = "/console"


class LeftMenuPage(BasePage):
    """
    左侧菜单页面

    提供左侧导航菜单相关的操作方法。
    """

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page)
        self._base_url = base_url or EnvConfig().base_url or "https://www.gqkt.cn"
        self._left_menu_url = self._base_url.rstrip("/") + URL_PATH

        # ========== 元素定位器 ==========

    # ==================== 动态定位器生成方法 ====================
    def _get_left_menu_item(self, menu_name: str):
        """
        获取左侧菜单项定位器
        """
        return self.page.get_by_text(menu_name)

    # ==================== 页面导航 ====================

    @allure.step("打开左侧菜单页面")
    def goto(self) -> "LeftMenuPage":
        """打开左侧菜单页面"""
        self.navigate_to(self._left_menu_url)
        return self

    # ==================== 页面操作 ====================

    @allure.step("点击左侧菜单项: {menu_name}")
    def click_left_menu_item(self, menu_name: str) -> "LeftMenuPage":
        """点击左侧菜单项"""
        self.click_element(self._get_left_menu_item(menu_name))
        return self
