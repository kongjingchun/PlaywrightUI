# ========================================
# 概览页面（课程建设 - 课程资源 - 概览）
# ========================================

from playwright.sync_api import Page

from .course_resource_page import CourseResourcePage


class OverviewPage(CourseResourcePage):
    """
    概览页面

    提供概览相关操作方法，继承课程资源页面公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # 资源数量展示
        self.resource_count_display = self.iframe.locator("xpath=//div[./div[text()='资源数']]/div[@class='stat-number']")

    # =================== 操作方法 ===================
    def get_resource_count(self) -> int:
        """获取资源数量"""
        # 等待资源数量展示
        self.wait_for_timeout(1000)
        a = self.get_text(self.resource_count_display)
        return int(a)
