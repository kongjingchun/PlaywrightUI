# ========================================
# 专业 AI 模型基类页面
# ========================================

from playwright.sync_api import Page

from base.base_page import BasePage


class MajorAiModelPage(BasePage):
    """
    专业 AI 模型基类页面

    提供专业 AI 模型相关页面的公共 iframe 及基础能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        # 专业 AI 模型页内容在 iframe 内
        self.iframe = page.frame_locator("iframe#app-iframe-2110")

        # ========== 头部按钮 / 搜索 ==========

        # ========== 列表区域 ==========

        # ========== 弹窗 / 表单 ==========
    # ==================== 动态定位器生成方法 ====================
    def get_menu_item_locator(self, menu_name: str):
        """
        通过菜单名称返回菜单的定位器

        Args:
            menu_name (str): 菜单名称

        Returns:
            Locator: 对应菜单项的 Playwright 定位器
        """
        return self.iframe.get_by_role("menuitem", name=menu_name)
    # ==================== 页面操作 ====================

    def click_menu_item(self, menu_name: str):
        """
        根据菜单名称点击菜单
        """
        self.click_element(self.get_menu_item_locator(menu_name))
    # ==================== 业务方法 ====================

    # ==================== 断言方法 ====================
