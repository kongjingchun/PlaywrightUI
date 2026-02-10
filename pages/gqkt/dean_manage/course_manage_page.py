# ========================================
# 课程管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class CourseManagePage(BasePage):
    """
    课程管理页面

    提供课程管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-2001")

        # ========== 头部按钮/搜索框 ==========
        # 新建课程
        self.new_course_button = self.iframe.get_by_role("button", name="新建课程")
        # ========== 课程列表 ==========

        # ========== 新增/编辑课程 ==========
        # 课程代码输入框
        self.course_code_input = self.iframe.get_by_role("textbox", name="课程代码")
        # 课程名称输入框
        self.course_name_input = self.iframe.get_by_role("textbox", name="课程名称")
        # 课程封面图片输入框
        self.course_cover_input = self.iframe.get_by_label("新建课程").locator(".el-upload, [class*='upload']").first
        # 选择学院下拉框
        self.course_dept_select = self.iframe.get_by_label("新建课程").get_by_text("请选择学院")
        # 课程描述输入框
        self.course_description_input = self.iframe.get_by_role("textbox", name="课程描述")
        # 是否一流课程开关（el-switch 的 input 被隐藏，点可见的 .el-switch）
        self.is_first_class_course_switch = self.iframe.get_by_label("新建课程").locator(".el-switch")
        # 课程负责人下拉框
        self.course_prof_select = self.iframe.get_by_label("新建课程").get_by_role("combobox", name="课程负责人")
        # 创建提交按钮
        self.confirm_create_button = self.iframe.get_by_role("button", name="确定")
        # 创建成功提示
        self.create_success_message = self.iframe.locator("xpath=//p[contains(text(),'新建成功')]")
        # ========== 课程详情 ==========

    # ==================== 动态定位器生成方法 ====================
    def get_dept_option_locator(self, dept_name: str):
        """
        根据学院名称返回下拉框中对应的定位器

        Args:
            dept_name: 学院名称

        Returns:
            对应学院下拉选项的元素定位器
        """
        return self.iframe.get_by_role("option", name=dept_name)

    def get_prof_option_locator(self, prof_name: str):
        """
        根据课程负责人名称返回下拉框中对应的定位器（用 option 避免与页面上其他同名文案冲突）
        """
        return self.iframe.get_by_role("option", name=prof_name)

    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================
    def create_course(self, course_code: str, course_name: str, image_path: str, dept_name: str, course_description: str, prof_name: str, is_first_class_course: bool = False):
        """新建课程"""
        self.click_element(self.new_course_button)  # 点击新建课程按钮
        self.fill_element(self.course_code_input, course_code)  # 输入课程代码
        self.fill_element(self.course_name_input, course_name)  # 输入课程名称
        self.upload_file_via_chooser(self.course_cover_input, image_path)  # 上传课程封面图片
        self.click_element(self.course_dept_select)  # 点击选择学院下拉框
        self.click_element(self.get_dept_option_locator(dept_name))  # 选择学院
        self.fill_element(self.course_description_input, course_description)  # 输入课程描述
        if is_first_class_course:  # 如果是一流课程，则勾选是否一流课程开关
            self.click_element(self.is_first_class_course_switch)
        self.click_element(self.course_prof_select)  # 点击选择课程负责人下拉框
        self.click_element(self.get_prof_option_locator(prof_name))  # 选择课程负责人
        self.click_element(self.course_prof_select)  # 关闭下拉框
        self.click_element(self.confirm_create_button)  # 点击确定创建按钮

    # ==================== 断言方法 ====================

    def is_create_course_success(self) -> bool:
        """检查是否创建课程成功"""
        try:
            self.wait_for_element_visible(self.create_success_message)
            self.logger.info("✓ 创建课程成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建课程失败: {e}")
            return False
