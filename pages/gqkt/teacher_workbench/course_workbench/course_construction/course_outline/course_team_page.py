# ========================================
# 课程团队页面（课程建设 - 课程大纲）
# ========================================

from playwright.sync_api import Page

from ... import CourseWorkbenchPage


class CourseTeamPage(CourseWorkbenchPage):
    """
    课程团队页面

    提供课程大纲下课程团队相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # 课程负责人编辑按钮
        self.edit_course_leader_button = self.iframe.locator("xpath=//div[@class='section' and contains(.,'课程负责人')]//button")
        # 课程教师编辑按钮
        self.edit_course_teacher_button = self.iframe.locator("xpath=//div[@class='section' and contains(.,'课程教师')]//button")
        # 添加负责人按钮
        self.add_course_leader_button = self.iframe.get_by_text("添加负责人")
        # 添加教师按钮
        self.add_course_teacher_button = self.iframe.get_by_text("添加教师")
        # 教师搜索输入框
        self.teacher_search_input = self.iframe.get_by_role("textbox", name="请输入教师工号或姓名")
        # 二次确认按钮
        self.confirm_button = self.iframe.get_by_label("确认添加").get_by_role("button", name="确认")
        # 二次确认删除按钮
        self.confirm_delete_button = self.iframe.get_by_label("确认删除").get_by_role("button", name="确认")
        # 退出编辑按钮
        self.exit_edit_button = self.iframe.get_by_role("button", name="退出编辑")
        # 添加成功
        self.add_success_message = self.iframe.locator("xpath=//p[contains(.,'添加成功')]")
        # 删除成功
        self.delete_success_message = self.iframe.locator("xpath=//p[contains(.,'删除成功')]")
    # ========================动态定位器生成方法=======================

    def get_add_teacher_button_by_name_or_id(self, name_or_id: str):
        """
        根据教师名字或工号返回该教师添加按钮的定位器

        :param name_or_id: 教师名字或工号
        :return: 添加按钮的locator
        """
        # 假设每个教师行包含教师姓名或工号文本，并有“添加”按钮
        return self.iframe.get_by_role("row", name=name_or_id).get_by_role("button")
    # 根据教师名称或工号返回该教师的删除按钮的定位器

    def get_delete_teacher_button_by_name_or_id(self, name_or_id: str):
        """
        根据教师名字或工号返回该教师删除按钮的定位器

        :param name_or_id: 教师名字或工号
        :return: 删除按钮的locator
        """
        return self.iframe.locator(f"xpath=//div[@class='member-info' and contains(.,'{name_or_id}')]/following-sibling::div/i")
    # ========================操作方法=======================

    # ========================业务方法=======================
    def add_course_leader(self, name_or_id: str):
        """
        添加课程负责人

        :param name_or_id: 教师名字或工号
        """
        self.click_element(self.edit_course_leader_button)  # 点击编辑课程负责人按钮
        self.click_element(self.add_course_leader_button)  # 点击添加课程负责人按钮
        self.fill_element(self.teacher_search_input, name_or_id)  # 填写教师名字或工号
        self.click_element(self.get_add_teacher_button_by_name_or_id(name_or_id))  # 点击添加教师按钮
        self.click_element(self.confirm_button)  # 点击二次确认按钮
        self.click_element(self.exit_edit_button)  # 点击退出编辑按钮

    def delete_course_leader(self, name_or_id: str):
        """
        删除课程负责人

        :param name_or_id: 教师名字或工号
        """
        self.click_element(self.edit_course_leader_button)  # 点击编辑课程负责人按钮
        self.click_element(self.get_delete_teacher_button_by_name_or_id(name_or_id))  # 点击对应教师的删除按钮
        self.click_element(self.confirm_delete_button)  # 点击二次确认删除按钮
        self.click_element(self.exit_edit_button)  # 点击退出编辑按钮

    def add_course_teacher(self, name_or_id: str):
        """
        添加课程教师

        :param name_or_id: 教师名字或工号
        """
        self.click_element(self.edit_course_teacher_button)  # 点击编辑课程教师按钮
        self.click_element(self.add_course_teacher_button)  # 点击添加课程教师按钮
        self.fill_element(self.teacher_search_input, name_or_id)  # 填写教师名字或工号
        self.click_element(self.get_add_teacher_button_by_name_or_id(name_or_id))  # 点击添加教师按钮
        self.click_element(self.confirm_button)  # 点击二次确认按钮
        self.click_element(self.exit_edit_button)  # 点击退出编辑按钮

    def delete_course_teacher(self, name_or_id: str):
        """
        删除课程教师

        :param name_or_id: 教师名字或工号
        """
        self.click_element(self.edit_course_teacher_button)  # 点击编辑课程教师按钮
        self.click_element(self.get_delete_teacher_button_by_name_or_id(name_or_id))  # 点击对应教师的删除按钮
        self.click_element(self.confirm_delete_button)  # 点击二次确认删除按钮
        self.click_element(self.exit_edit_button)  # 点击退出编辑按钮
    # ========================断言方法=======================

    def is_add_success(self) -> bool:
        """检查是否添加成功提示出现"""
        try:
            self.wait_for_element_visible(self.add_success_message)
            self.logger.info("✓ 添加成功提示出现")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加成功提示未出现: {e}")
            return False

    def is_delete_success(self) -> bool:
        """检查是否删除成功提示出现"""
        try:
            self.wait_for_element_visible(self.delete_success_message)
            self.logger.info("✓ 删除成功提示出现")
            return True
        except Exception as e:
            self.logger.error(f"✗ 删除成功提示未出现: {e}")
            return False
