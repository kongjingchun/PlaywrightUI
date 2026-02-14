# ========================================
# 我教的班页面
# ========================================

from playwright.sync_api import Page

from base.base_page import BasePage


class MyTaughtClassPage(BasePage):
    """
    我教的班页面

    提供教师工作台「我教的班」相关操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        # 我教的班页内容在 iframe 内，选择器按实际页面 id 修改
        self.iframe = page.frame_locator("iframe#app-iframe-4009")

        # ========== 头部按钮 / 搜索 ==========
        # 班级搜索框
        self.class_search_input = self.iframe.get_by_role("textbox", name="搜索课程代码或名称")
        # ========== 班级列表区域 ==========

        # ========== 弹窗 / 表单 ==========

    # ==================== 动态定位器生成方法 ====================
    def get_class_card_by_name(self, class_name: str):
        """
        根据班级名称返回班级卡片点击的定位器

        :param class_name: 班级名称
        :return: Playwright 定位器（Locator）表示该班级卡片
        """
        return self.iframe.get_by_text(class_name, exact=True)

    # ==================== 操作方法 ====================
    def click_tab_by_name(self, tab_name: str):
        """
        根据TAB名称点击TAB

        :param tab_name: TAB的显示名称
        """
        self.click_element(self.iframe.get_by_role("tab", name=tab_name))
    # ==================== 业务方法 ====================

    def click_class_card_by_name(self, class_name: str):
        """
        根据班级名称点击班级卡片

        :param class_name: 班级名称
        """
        self.fill_element(self.class_search_input, class_name)
        self.click_element(self.get_class_card_by_name(class_name))
