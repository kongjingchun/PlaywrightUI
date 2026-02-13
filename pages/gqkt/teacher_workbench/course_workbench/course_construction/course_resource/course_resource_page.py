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

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # 上传文件按钮
        self.upload_file_button = self.iframe.get_by_role("button", name="上传文件").first
        # 上传成功提示
        self.upload_success_message = self.iframe.locator("xpath=//p[contains(text(),'上传成功')]").last
    # ==================== 业务方法 ====================

    def upload_file(self, file_path: str):
        """上传文件"""
        self.upload_file_via_chooser(self.upload_file_button, file_path)
    # ==================== 断言方法 ====================

    def is_upload_file_success(self) -> bool:
        """检查是否上传文件成功"""
        try:
            self.wait_for_element_visible(self.upload_success_message)
            self.logger.info("✓ 上传文件成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 上传文件失败: {e}")
            return False
