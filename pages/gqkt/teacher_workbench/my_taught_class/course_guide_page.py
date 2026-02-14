# ========================================
# 课程导读页面（我教的班 - 课程导读）
# ========================================

from playwright.sync_api import Page

from .my_taught_class_page import MyTaughtClassPage


class CourseGuidePage(MyTaughtClassPage):
    """
    课程导读页面

    提供我教的班下课程导读相关操作方法，继承我教的班页面公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== 课程导读区域 ==========
