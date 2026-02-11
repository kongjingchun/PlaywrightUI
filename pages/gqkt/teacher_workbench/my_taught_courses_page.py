# ========================================
# 我教的课 页面
# ========================================

from playwright.sync_api import Page

from base.base_page import BasePage


class MyTaughtCoursesPage(BasePage):
    """
    我教的课 页面

    提供教师工作台「我教的课」相关操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        # 我教的课页内容在 iframe 内，选择器按实际页面 id 修改
        self.iframe = page.frame_locator("iframe#app-iframe-4003")

        # ========== 头部按钮 / 搜索 ==========
        # 课程搜索框
        self.course_search_input = self.iframe.get_by_role("textbox", name="搜索课程代码或名称")
        # ========== 课程列表区域 ==========

        # ========== 弹窗 / 表单 ==========
    # ==================== 动态定位器生成方法 ====================
    def get_course_card_by_name(self, course_name: str):
        """
        根据课程名称返回课程卡片点击的定位器

        :param course_name: 课程名称
        :return: Playwright 定位器（Locator）表示该课程卡片
        """
        # 假设课程卡片的 aria-label 或文本内容中包含课程名称
        return self.iframe.get_by_text(course_name, exact=True)
    # ==================== 操作方法 ====================

    def click_course_card_by_name(self, course_name: str):
        """
        根据课程名称点击课程卡片

        :param course_name: 课程名称
        """
        self.click_element(self.get_course_card_by_name(course_name))
