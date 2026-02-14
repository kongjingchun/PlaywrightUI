# ========================================
# 教学班管理页面（课程教学 - 教学班管理）
# ========================================

from playwright.sync_api import Page

from .. import CourseWorkbenchPage


class TeachingClassManagePage(CourseWorkbenchPage):
    """
    教学班管理页面

    提供教学班管理相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # ========== 头部按钮 / 搜索框 ==========
        # 创建教学班按钮
        self.create_teaching_class_button = self.iframe.get_by_role("button", name="创建教学班")
        # ========== 教学班列表 ==========
        # ========== 新增/编辑教学班 ==========
        # 名称输入框
        self.new_teaching_class_name_input = self.iframe.get_by_role("textbox", name="* 教学班名称")
        # 编号输入框
        self.new_teaching_class_id_input = self.iframe.get_by_role("textbox", name="* 教学班编号")
        # 开课时间输入框
        self.new_teaching_class_start_time_input = self.iframe.get_by_placeholder("开课时间")
        # 结课时间输入框
        self.new_teaching_class_end_time_input = self.iframe.get_by_placeholder("结课时间")
        # 无结课时间勾选框
        self.new_teaching_class_no_end_time_checkbox = self.iframe.locator("xpath=//span[text()=' 无结课时间 ']/preceding-sibling::span")
        # 班级人数无限制元素
        self.new_teaching_class_class_size_unlimited_element = self.iframe.get_by_text("无限制")
        # 班级人数输入框
        self.new_teaching_class_class_size_input = self.iframe.locator("xpath=//div[./span[@aria-label='减少数值']]/div/div/input")
        # 选课开始时间
        self.new_teaching_class_select_start_time_input = self.iframe.get_by_role("combobox", name="选课开始时间")
        # 选课结束时间
        self.new_teaching_class_select_end_time_input = self.iframe.get_by_role("combobox", name="选课结束时间")
        # 确定按钮
        self.new_teaching_class_confirm_button = self.iframe.get_by_role("button", name="确定")

        # ========== 成员管理 ==========
        # 设置主讲教师按钮
        self.set_main_teacher_button = self.iframe.get_by_text("设置主讲教师")
        # 设置成功
        self.set_main_teacher_success_message = self.iframe.locator("xpath=//p[contains(text(),'设置成功')]")
        # 确认按钮
        self.set_main_teacher_confirm_button = self.iframe.get_by_role("button", name="确认")
    # =================== 动态定位器生成方法 ===================

    def get_student_self_selection_checkbox(self, allow: bool):
        """
        根据允许学生自选的值返回对应的勾选框定位器。

        :param allow: 是否允许学生自选
        :return: 定位器
        """
        if allow:
            # 允许学生自选
            return self.iframe.get_by_label("是否允许学生自选").get_by_text("是")
        else:
            # 不允许学生自选
            return self.iframe.get_by_label("是否允许学生自选").get_by_text("否")

    def get_student_self_withdraw_checkbox(self, allow: bool):
        """
        根据允许学生自主退课的值返回对应的勾选框定位器。

        :param allow: 是否允许学生自主退课
        :return: 定位器
        """
        if allow:
            # 允许学生自主退课
            return self.iframe.get_by_label("是否允许学生自主退课").get_by_text("是")
        else:
            # 不允许学生自主退课
            return self.iframe.get_by_label("是否允许学生自主退课").get_by_text("否")

    def get_manage_member_button_by_teaching_class_name(self, teaching_class_name: str):
        """
        根据教学班名称返回对应行的成员管理按钮定位器

        :param teaching_class_name: 教学班名称
        :return: 成员管理按钮定位器
        """
        return self.iframe.get_by_role("row", name=teaching_class_name).get_by_role("button", name="成员管理")

    def get_replace_main_teacher_button_by_teacher_info(self, teacher_info: str):
        """
        根据主讲教师信息返回对应的“替换为主讲教师”按钮定位器。

        :param teacher_name: 主讲教师姓名
        :return: 替换为主讲教师按钮定位器
        """
        # 假设有一行显示教师信息, 该行有“替换为主讲教师”按钮
        return self.iframe.get_by_role("row", name=teacher_info).get_by_text("替换为主讲教师")

    # =================== 业务方法 ===================

    def create_teaching_class(
        self,
        teaching_class_name: str,
        teaching_class_id: str,
        teaching_class_start_time: str,
        teaching_class_end_time: str = "",
        teaching_class_class_size: int = 1000,
        teaching_class_select_start_time: str = None,
        teaching_class_select_end_time: str = None,
        allow_student_self_selection: bool = False,
        allow_student_self_withdraw: bool = False,
        use_class_size_unlimited: bool = False
    ):
        """
        创建教学班

        :param teaching_class_name: 教学班名称
        :param teaching_class_id: 教学班编号
        :param teaching_class_start_time: 开课时间 例子：2026-02-14 11:51:48
        :param teaching_class_end_time: 结课时间（可为空） 例子：2026-02-14 11:51:48
        :param teaching_class_class_size: 班级人数（默认1000）
        :param teaching_class_select_start_time: 选课开始时间 例子：2026-02-14 11:51:48
        :param teaching_class_select_end_time: 选课结束时间 例子：2026-02-14 11:51:48
        :param allow_student_self_selection: 是否允许学生自选（默认False）
        :param allow_student_self_withdraw: 是否允许学生自主退课（默认False）
        :param use_class_size_unlimited: 是否点击班级人数无限制（默认False）
        """
        self.click_element(self.create_teaching_class_button)  # 点击创建教学班按钮
        self.fill_element(self.new_teaching_class_name_input, teaching_class_name)  # 输入教学班名称
        self.fill_element(self.new_teaching_class_id_input, teaching_class_id)  # 输入教学班编号
        self.fill_element(self.new_teaching_class_start_time_input, teaching_class_start_time)  # 输入开课时间

        # 结课时间可能为空，若为空则点击无结课时间勾选框，否则输入结课时间
        if teaching_class_end_time:
            self.fill_element(self.new_teaching_class_end_time_input, teaching_class_end_time)
        else:
            self.click_element(self.new_teaching_class_no_end_time_checkbox)

        # 根据 use_class_size_unlimited 是否点击“无限制”,若为True则点击“无限制”,否则输入班级人数
        if use_class_size_unlimited:
            self.click_element(self.new_teaching_class_class_size_unlimited_element)
        else:
            self.fill_element(self.new_teaching_class_class_size_input, teaching_class_class_size)

        self.click_element(self.get_student_self_selection_checkbox(allow_student_self_selection))  # 点击是否允许学生自选勾选框

        # allow_student_self_selection为False时不输入选课起止时间
        if allow_student_self_selection:
            self.fill_element(self.new_teaching_class_select_start_time_input, teaching_class_select_start_time)
            self.fill_element(self.new_teaching_class_select_end_time_input, teaching_class_select_end_time)

        self.click_element(self.get_student_self_withdraw_checkbox(allow_student_self_withdraw))  # 点击是否允许学生自主退课勾选框
        self.click_element(self.new_teaching_class_confirm_button)  # 点击确定按钮

    def set_main_teacher_for_class(self, teaching_class_name: str, teacher_name: str):
        """
        给指定教学班设置指定主讲教师的操作

        :param teaching_class_name: 教学班名称
        :param teacher_name: 主讲教师姓名
        """
        # 根据班级名称点击对应成员管理按钮
        self.click_element(self.get_manage_member_button_by_teaching_class_name(teaching_class_name))
        # 点击“设置主讲教师”按钮
        self.click_element(self.set_main_teacher_button)
        # 根据主讲教师信息点击对应的“替换为主讲教师”按钮
        self.click_element(self.get_replace_main_teacher_button_by_teacher_info(teacher_name))
        # 点击确认按钮
        self.click_element(self.set_main_teacher_confirm_button)
    # =================== 断言方法 ===================

    def is_create_teaching_class_success(self, teaching_class_name: str) -> bool:
        """
        断言是否创建教学班成功

        :return: 是否创建教学班成功
        """
        result = self.has_text(teaching_class_name, scope=self.iframe)
        if result:
            self.logger.info("✓ 创建教学班成功")
            return True
        else:
            self.logger.error(f"✗ 创建教学班失败: {teaching_class_name} 不存在")
            return False

    def is_set_main_teacher_success(self) -> bool:
        """
        断言是否设置主讲教师成功

        :return: 是否设置主讲教师成功
        """
        try:
            self.wait_for_element_visible(self.set_main_teacher_success_message)
            self.logger.info("✓ 设置主讲教师成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 设置主讲教师失败: {e}")
            return False
