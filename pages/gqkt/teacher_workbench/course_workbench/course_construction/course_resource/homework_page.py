# ========================================
# 作业页面（课程建设 - 课程资源 - 作业）
# ========================================

from playwright.sync_api import Page

from .course_resource_page import CourseResourcePage


class HomeworkPage(CourseResourcePage):
    """
    作业页面

    提供作业相关操作方法，继承课程资源页面公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")
