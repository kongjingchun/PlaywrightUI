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
        # 编辑按钮
        self.edit_button = self.iframe.get_by_role("button", name="编辑")
        # 保存按钮
        self.save_button = self.iframe.get_by_role("button", name="保存")
        # 保存成功提示
        self.save_success_message = self.iframe.locator("xpath=//p[contains(text(),'保存成功')]").last
    # ==================== 操作方法 ====================

    def click_edit_button(self):
        """点击编辑按钮"""
        self.click_element(self.edit_button)

    def click_save_button(self):
        """点击保存按钮"""
        self.click_element(self.save_button)

    # ==================== 断言方法 ====================
    def is_save_course_guide_success(self) -> bool:
        """检查是否保存课程导读成功"""
        try:
            self.wait_for_element_visible(self.save_success_message)
            self.logger.info("✓ 课程导读保存成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 课程导读保存失败: {e}")
            return False
