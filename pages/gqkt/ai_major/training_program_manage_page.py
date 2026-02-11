# ========================================
# 培养方案管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class TrainingProgramManagePage(BasePage):
    """
    培养方案管理页面

    提供培养方案管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-2102")

        # ========== 头部按钮/搜索框 ==========
        # 新建培养方案
        self.new_training_program_button = self.iframe.get_by_role("button", name="新建培养方案")
        # ========== 培养方案列表 ==========

        # ========== 新增/编辑培养方案 ==========
        # 培养方案名称输入框
        self.training_program_name_input = self.iframe.get_by_role("textbox", name="方案名称")
        # 关联专业下拉框
        self.training_program_major_select = self.iframe.get_by_label("新建培养方案").get_by_text("请选择专业")
        # 培养类型下拉框
        self.training_program_type_select = self.iframe.get_by_label("新建培养方案").get_by_text("请选择培养类型")
        # 培养层次下拉框
        self.training_program_level_select = self.iframe.get_by_label("新建培养方案").get_by_text("请选择培养层次")
        # 学制下拉框
        self.training_program_duration_select = self.iframe.get_by_label("新建培养方案").get_by_text("请选择学制")
        # 学分要求
        self.training_program_credit_requirement_input = self.iframe.get_by_role("spinbutton", name="* 学分要求")
        # 学位选择下拉框
        self.training_program_degree_select = self.iframe.get_by_label("新建培养方案").get_by_text("请选择授予学位")
        # 版本年份
        self.training_program_version_year_input = self.iframe.get_by_role("spinbutton", name="* 版本年份")
        # 创建提交按钮
        self.confirm_create_button = self.iframe.get_by_role("button", name="创建")
        # 创建培养方案成功提示
        self.create_training_program_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建培养方案成功')]")

        # ========== 培养方案修订 ==========
        # 保存按钮
        self.confirm_edit_button = self.iframe.get_by_role("button", name="保存").last
        # # 局部保存按钮
        # self.confirm_partial_edit_button = self.iframe.get_by_role("button", name="保存").nth(1)  # 第2个保存按钮是局部保存按钮
        # 修订/保存成功提示（多次保存会存在多条，取最后一条 .last 避免 strict mode 多元素）
        self.edit_training_program_success_message = self.iframe.locator("xpath=//p[contains(text(),'保存成功')]").last

        # ====专业信息====
        # 专业概述输入框
        self.training_program_major_overview_input = self.iframe.get_by_role("textbox", name="专业概述")
        # 专业概述成功提示
        self.training_program_major_overview_success_message = self.iframe.locator("xpath=//p[contains(text(),'更新培养方案成功')]").last

        # ====培养目标====
        # 培养目标概述输入框
        self.training_program_major_training_goal_input = self.iframe.get_by_role("textbox", name="请输入培养目标概述")
        # 添加目标按钮
        self.add_training_goal_button = self.iframe.get_by_role("button", name="添加目标")
        # 培养目标描述输入框（添加目标后可能有多条，取最后一条即本次新增的空输入框，避免 strict mode 多元素）
        self.training_program_major_training_goal_description_input = self.iframe.get_by_placeholder("请输入培养目标描述")

        # ====毕业要求====
        # 毕业要求概述输入框
        self.training_program_major_graduation_requirement_input = self.iframe.get_by_role("textbox", name="请输入毕业要求概述")
        # 添加指标点按钮
        self.add_graduation_requirement_button = self.iframe.get_by_role("button", name="添加指标点").last
        # 指标点名称/描述（用 placeholder 精确匹配，避免与“分解指标点”混淆；.last 取当前新增行）
        self.graduation_requirement_name_input = self.iframe.get_by_placeholder("指标点名称").last
        self.graduation_requirement_description_input = self.iframe.get_by_placeholder("请输入指标点描述").last
        # 指标点展开按钮 / 添加分解指标点按钮
        self.graduation_requirement_expand_button = self.iframe.get_by_role("button", name="展开", exact=True).last
        self.add_decomposition_graduation_requirement_button = self.iframe.get_by_role("button", name="添加分解指标点").last
        # 分解指标点名称/描述
        self.decomposition_graduation_requirement_name_input = self.iframe.get_by_placeholder("分解指标点名称").last
        self.decomposition_graduation_requirement_description_input = self.iframe.get_by_placeholder("请输入分解指标点描述").last
        # ====目标支撑====
        # 目标支撑选择下拉框
        self.target_support_select = self.iframe.get_by_text("选择")
        # 支撑关系保存成功提示
        self.success_target_support_message = self.iframe.locator("xpath=//p[contains(text(),'支撑关系保存成功')]")
        # ====课程体系====
        # 添加课程按钮
        self.add_course_button = self.iframe.get_by_role("button", name="添加课程")
        # 课程搜索框
        self.course_search_input = self.iframe.get_by_label("选择课程").get_by_placeholder("搜索课程名称或代码")
        # 确认添加课程按钮
        self.confirm_add_course_button = self.iframe.get_by_role("button", name="确认添加")
        # 成功添加提示框
        self.success_add_course_message = self.iframe.locator("xpath=//p[contains(text(),'成功添加')]")
        # ====课程支撑====
        # 关联课程按钮
        self.associate_course_button = self.iframe.get_by_role("button", name="+ 关联课程")
        # 课程搜索输入框
        self.associate_course_search_input = self.iframe.get_by_label("课程管理").get_by_role("textbox", name="请输入课程名字")
        # 确认关联课程按钮
        self.confirm_associate_course_button = self.iframe.get_by_role("button", name="确定")
        # 完成编辑按钮
        self.complete_edit_button = self.iframe.get_by_role("button", name="完成编辑")
        # 成功关联提示框
        self.success_associate_course_message = self.iframe.locator("xpath=//p[contains(text(),'成功添加')]")
        # 编辑完成提示框
        self.edit_complete_message = self.iframe.locator("xpath=//p[contains(text(),'编辑完成')]")
    # ==================== 动态定位器生成方法 ====================
    # ====新建培养方案====

    def get_major_option_locator(self, major_name: str):
        """
        根据专业名称返回下拉框中对应的定位器
        """
        return self.iframe.get_by_role("option", name=major_name)

    def get_type_option_locator(self, type_name="主修"):
        """
        根据培养类型名称返回下拉框中对应的定位器（用 option 避免与页面上其他同名文案冲突）
        """
        return self.iframe.get_by_role("option", name=type_name)

    def get_level_option_locator(self, level_name="本科"):
        """
        根据培养层次名称返回下拉框中对应的定位器。
        使用 exact=True 避免“本科”同时匹配到“高职本科”。
        """
        return self.iframe.get_by_role("option", name=level_name, exact=True)

    def get_duration_option_locator(self, duration_name="4年"):
        """
        根据学制名称返回下拉框中对应的定位器（用 option 避免与页面上其他同名文案冲突）
        如果duration_name后面没有“年”，则自动加上“年”
        """
        if not str(duration_name).endswith("年"):
            duration_name = f"{duration_name}年"
        return self.iframe.get_by_role("option", name=duration_name)

    def get_degree_option_locator(self, degree_name="理学学士"):
        """
        根据学位名称返回下拉框中对应的定位器（用 option 避免与页面上其他同名文案冲突）
        """
        return self.iframe.get_by_role("option", name=degree_name)

    # ====修订培养方案====
    def get_menu_locator(self, menu_name: str):
        """
        根据菜单名称返回对应菜单的定位器。
        修订页 tab 结构：.tab-list > .tab-item > .tab-label（如：专业信息、培养目标）。
        """
        return self.iframe.locator(".tab-item", has_text=menu_name)

    def get_edit_training_program_button_locator(self, training_program_name: str):
        """
        根据方案名称返回方案修订按钮的定位器
        """
        # 假设每行操作按钮是在包含方案名称的tr下有“修订”按钮
        return self.iframe.locator("tr", has_text=training_program_name).get_by_role("button", name="修订")

    # ====目标支撑====
    def get_target_support_option_locator(self, target_support: str):
        """
        根据目标支撑名称返回下拉框中对应的定位器
        """
        return self.iframe.get_by_role("option", name=target_support)

    # ====课程体系====
    def get_course_checkbox_locator(self, course_name: str):
        """
        根据课程名称返回对应复选框的定位器
        """
        # 假设每门课程是一行，复选框通常是 input[type=checkbox] 并在课程名称左侧
        # 可以用 has_text 或同一行定位
        return self.iframe.get_by_role("row", name=course_name).locator("span").nth(1)
    # ====课程支撑====

    def get_associate_course_checkbox_locator(self, course_name: str):
        """
        根据课程名称返回对应复选框的定位器
        """
        return self.iframe.get_by_role("row", name=course_name).locator("span").nth(1)

    def get_support_level_option_locator(self, index: int, support_level: str):
        """
        根据传入的index和支撑等级，获取设置支撑等级的定位器
        """
        return self.iframe.get_by_role("button", name=support_level).nth(index)
    # ==================== 页面操作 ====================

    def click_edit_training_program_menu(self, training_program_name: str):
        """点击方案修订菜单"""
        self.click_element(self.get_edit_training_program_button_locator(training_program_name))  # 点击方案修订按钮

    def click_menu(self, menu_name: str):
        """点击菜单"""
        self.click_element(self.get_menu_locator(menu_name))  # 点击菜单
        # 因为不等待经常报错，所以等待500ms
        self.wait_for_timeout(500)

    # ==================== 业务方法 ====================

    def create_training_program(self, training_program_name: str, training_program_major: str, training_program_type: str, training_program_level: str, training_program_duration: str, training_program_credit_requirement: str, training_program_degree: str, training_program_version_year: str):
        """新建培养方案"""
        self.click_element(self.new_training_program_button)  # 点击新建培养方案按钮
        self.fill_element(self.training_program_name_input, training_program_name)  # 输入培养方案名称
        self.click_element(self.training_program_major_select)  # 点击关联专业下拉框
        self.click_element(self.get_major_option_locator(training_program_major))  # 选择关联专业
        self.click_element(self.training_program_type_select)  # 点击培养类型下拉框
        self.click_element(self.get_type_option_locator(training_program_type))  # 选择培养类型
        self.click_element(self.training_program_level_select)  # 点击培养层次下拉框
        self.click_element(self.get_level_option_locator(training_program_level))  # 选择培养层次
        self.click_element(self.training_program_duration_select)  # 点击学制下拉框
        self.click_element(self.get_duration_option_locator(training_program_duration))  # 选择学制
        self.fill_element(self.training_program_credit_requirement_input, training_program_credit_requirement)  # 输入学分要求
        self.click_element(self.training_program_degree_select)  # 点击学位选择下拉框
        self.click_element(self.get_degree_option_locator(training_program_degree))  # 选择学位
        self.fill_element(self.training_program_version_year_input, training_program_version_year)  # 输入版本年份
        self.click_element(self.confirm_create_button)  # 点击创建提交按钮

    def edit_training_program_major_info(self, major_overview: str):
        """专业信息"""
        self.click_menu("专业信息")  # 点击专业信息菜单
        self.fill_element(self.training_program_major_overview_input, major_overview)  # 输入专业概述
        self.click_element(self.confirm_edit_button)  # 点击保存按钮

    def edit_training_program_major_training_goal(self, major_training_goal: str):
        """培养目标概述"""
        self.click_menu("培养目标")  # 点击培养目标菜单
        self.fill_element(self.training_program_major_training_goal_input, major_training_goal)  # 输入培养目标概述
        self.click_element(self.confirm_edit_button)  # 点击保存按钮

    def add_training_goal(self, training_goal: str):
        """添加培养目标"""
        self.click_menu("培养目标")  # 保证在“培养目标”tab
        self.wait_for_load_state("load")
        self.click_element(self.add_training_goal_button)     # 点击添加目标按钮
        self.fill_element(self.training_program_major_training_goal_description_input, training_goal)  # 输入培养目标描述
        self.click_element(self.confirm_edit_button)          # 点击局部保存按钮

    def edit_training_program_major_graduation_requirement(self, major_graduation_requirement: str):
        """毕业要求概述"""
        self.click_menu("毕业要求")  # 点击毕业要求菜单
        self.fill_element(self.training_program_major_graduation_requirement_input, major_graduation_requirement)  # 输入毕业要求概述
        self.click_element(self.confirm_edit_button)  # 点击保存按钮

    def add_graduation_requirement(self, graduation_requirement_name: str, graduation_requirement_description: str, indicator_name: str, indicator_description: str):
        """添加指标点"""
        self.click_menu("毕业要求")  # 点击毕业要求菜单
        self.click_element(self.add_graduation_requirement_button)  # 点击添加指标点按钮
        self.fill_element(self.graduation_requirement_name_input, graduation_requirement_name)  # 输入指标点名称
        self.fill_element(self.graduation_requirement_description_input, graduation_requirement_description)  # 输入指标点描述
        self.click_element(self.graduation_requirement_expand_button)  # 点击指标点展开按钮
        self.click_element(self.add_decomposition_graduation_requirement_button)  # 点击添加分解指标点按钮
        self.fill_element(self.decomposition_graduation_requirement_name_input, indicator_name)  # 输入分解指标点名称
        self.fill_element(self.decomposition_graduation_requirement_description_input, indicator_description)  # 输入分解指标点描述
        self.click_element(self.confirm_edit_button)  # 点击保存按钮

    def add_target_support(self, target_support="高支撑"):
        """添加目标支撑"""
        self.click_menu("目标支撑")  # 点击目标支撑菜单
        num = self.target_support_select.count()
        for i in range(num):
            self.click_element(self.target_support_select.first)  # 点击目标支撑选择下拉框
            self.click_element(self.get_target_support_option_locator(target_support))  # 选择目标支撑
            self.wait_for_timeout(500)
        self.click_element(self.confirm_edit_button)  # 点击保存按钮

    def add_course(self, course_name: str):
        """添加课程"""
        self.click_menu("课程体系")  # 点击课程体系菜单
        self.click_element(self.add_course_button)  # 点击添加课程按钮
        self.fill_element(self.course_search_input, course_name)  # 输入课程名称或代码
        self.click_element(self.get_course_checkbox_locator(course_name))  # 点击课程复选框
        self.click_element(self.confirm_add_course_button)  # 点击确认添加课程按钮

    def associate_course(self, course_name: str, support_level: str = "H"):
        """关联课程"""
        self.click_menu("课程支撑")  # 点击课程支撑菜单
        num = self.associate_course_button.count()
        for i in range(num):
            self.click_element(self.associate_course_button.first)  # 点击关联课程按钮
            self.fill_element(self.associate_course_search_input, course_name)  # 输入课程名称或代码
            self.click_element(self.get_associate_course_checkbox_locator(course_name))  # 点击课程复选框
            self.click_element(self.confirm_associate_course_button)  # 点击确认关联课程按钮
            self.click_element(self.get_support_level_option_locator(i, support_level))  # 点击支撑等级
            self.click_element(self.complete_edit_button)  # 点击完成编辑按钮
        self.click_element(self.confirm_edit_button)  # 点击保存按钮
    # ==================== 断言方法 ====================

    def is_create_training_program_success(self) -> bool:
        """检查是否新建培养方案成功"""
        try:
            self.wait_for_element_visible(self.create_training_program_success_message)
            self.logger.info("✓ 新建培养方案成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 新建培养方案失败: {e}")
            return False

    def is_edit_training_program_success(self) -> bool:
        """检查是否修订培养方案成功"""
        try:
            self.wait_for_element_visible(self.edit_training_program_success_message)
            self.logger.info("✓ 修订培养方案成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 修订培养方案失败: {e}")
            return False

    def is_add_target_support_success(self) -> bool:
        """检查是否添加目标支撑成功"""
        try:
            self.wait_for_element_visible(self.success_target_support_message)
            self.logger.info("✓ 添加目标支撑成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加目标支撑失败: {e}")
            return False

    def is_add_course_success(self) -> bool:
        """检查是否添加课程成功"""
        try:
            self.wait_for_element_visible(self.success_add_course_message)
            self.logger.info("✓ 添加课程成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加课程失败: {e}")
            return False

    def is_edit_complete(self) -> bool:
        """检查是否编辑完成"""
        try:
            self.wait_for_element_visible(self.edit_complete_message.last)
            self.logger.info("✓ 编辑完成")
            return True
        except Exception as e:
            self.logger.error(f"✗ 编辑完成失败: {e}")
            return False
