# ========================================
# 课程信息页面（课程建设 - 课程大纲）
# ========================================

from playwright.sync_api import Page

from ... import CourseWorkbenchPage


class CourseInfoPage(CourseWorkbenchPage):
    """
    课程信息页面

    提供课程大纲下课程信息相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # ========== 头部按钮 / 搜索 ==========
        # 编辑按钮
        self.edit_button = self.iframe.get_by_role("button", name="编辑")
        # ========== 编辑页面 ==========
        # 课程详情介绍富文本输入
        self.course_detail_introduction_input = self.iframe.locator("#w-e-textarea-1")
        # 保存按钮
        self.save_button = self.iframe.get_by_role("button", name="保存")
        # 保存成功提示
        self.save_success_message = self.iframe.locator("xpath=//p[contains(.,'保存成功') or contains(.,'编辑完成')]")
        # ========== 弹窗 / 表单 ==========

    # ==================== 操作方法 ====================
    def click_edit_button(self):
        """点击编辑按钮"""
        self.click_element(self.edit_button)

    def fill_course_detail_introduction_input(self, course_detail_introduction: str):
        """填写课程详情介绍"""
        self.fill_element(self.course_detail_introduction_input, course_detail_introduction)
    # ==================== 业务方法 ====================

    def edit_course_detail_introduction(self, course_detail_introduction: str):
        """修改课程详情介绍"""
        self.click_element(self.edit_button)
        self.fill_course_detail_introduction_input(course_detail_introduction)
        self.click_element(self.save_button)

    # ==================== 断言方法 ====================
    def is_edit_course_info_success(self) -> bool:
        """检查是否编辑课程信息成功"""
        try:
            self.wait_for_element_visible(self.save_success_message)
            self.logger.info("✓ 课程信息保存成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 课程信息保存失败: {e}")
            return False
