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
        # ========== 培养方案详情 ==========

    # ==================== 动态定位器生成方法 ====================
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
