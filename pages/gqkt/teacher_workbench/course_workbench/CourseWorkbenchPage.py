# ========================================
# 课程工作台页面
# ========================================

from playwright.sync_api import Page

from base.base_page import BasePage


class CourseWorkbenchPage(BasePage):
    """
    课程工作台页面

    提供课程工作台相关操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        self.base_iframe = page.frame_locator("iframe#app-iframe-4002")

        # ========== 头部按钮 / 搜索 ==========

        # ========== 列表区域 ==========

        # ========== 弹窗 / 表单 ==========
    # ==================== 动态定位器生成方法 ====================
    def get_left_menu_locator_by_name(self, menu_name: str):
        """
        根据名称获取左侧菜单的定位器

        :param menu_name: 菜单名称
        :return: 对应菜单的定位器
        """
        # 假定菜单项有 aria-label 或 span 显示名称
        return self.base_iframe.get_by_role("treeitem", name=menu_name).locator("div").first
    # ==================== 操作方法 ====================

    def click_left_menu_by_name(self, menu_name: str):
        """
        根据名称点击左侧菜单

        :param menu_name: 菜单名称
        """
        self.click_element(self.get_left_menu_locator_by_name(menu_name))
