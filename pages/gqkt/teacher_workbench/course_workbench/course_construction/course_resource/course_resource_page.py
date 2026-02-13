# ========================================
# 课程资源页面（课程建设 - 课程资源）
# ========================================

from playwright.sync_api import Page

from ... import CourseWorkbenchPage


class CourseResourcePage(CourseWorkbenchPage):
    """
    课程资源页面基类

    提供课程资源相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # ========== 头部按钮 / 搜索 ==========

        # ========== 列表区域 ==========

        # ========== 弹窗 / 表单 ==========
