# ========================================
# 专业管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class MajorManagePage(BasePage):
    """
    专业管理页面

    提供专业管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-2101")

        # ========== 头部按钮/搜索框 ==========
        # 新增专业按钮
        self.new_major_button = self.iframe.get_by_role("button", name="新建专业")
        # ========== 专业列表 ==========

        # ========== 新增/编辑专业 ==========
        # 专业名称输入框
        self.major_name_input = self.iframe.get_by_role("textbox", name="* 专业名称")
        # 专业代码（学校）输入框
        self.major_code_school_input = self.iframe.get_by_role("textbox", name="* 专业代码（学校）")
        # 专业代码（国家）输入框
        self.major_code_national_input = self.iframe.get_by_role("textbox", name="* 专业代码（国家）")
        # 所属院系选择框
        self.major_dept_select = self.iframe.get_by_text("请选择所属院系")
        # 专业负责人选择框
        self.major_prof_select = self.iframe.get_by_text("请选择专业负责人")
        # 专业负责人关闭下拉框
        self.major_prof_close_button = self.iframe.locator("xpath=(//label[text()='专业负责人']/following-sibling::div//i)[last()]")
        # 确定创建按钮
        self.confirm_create_button = self.iframe.get_by_role("button", name="确定")
        # 创建成功提示
        self.create_success_message = self.iframe.locator("xpath=//p[contains(text(),'新建成功')]")
        # ========== 专业详情 ==========

    # ==================== 动态定位器生成方法 ====================

    def _get_major_dept_select_locator(self, dept_name: str):
        """
        根据院系名称返回下拉框对应院系的定位器
        """
        return self.iframe.get_by_role("option", name=dept_name)

    def _get_major_prof_select_locator(self, prof_name: str):
        """
        根据专业负责人名称返回下拉框对应专业负责人的定位器
        """
        return self.iframe.get_by_role("option", name=prof_name)

    def _get_major_building_level_radio_locator(self, level: str):
        """
        根据专业建设层次返回单选框对应专业建设层次的定位器
        """
        if "国" in level:
            return self.iframe.get_by_label("专业建设层次").get_by_text("国家一流本科专业")
        if "省" in level:
            return self.iframe.get_by_label("专业建设层次").get_by_text("省级一流本科专业")
        if "校" in level:
            return self.iframe.get_by_label("专业建设层次").get_by_text("校级重点专业")
        if "普" in level:
            return self.iframe.get_by_label("专业建设层次").get_by_text("普通专业")
        return self.iframe.get_by_label("专业建设层次").get_by_text("国家一流本科专业")

    def _get_major_feature_checkbox_locator(self, feature_name: str):
        """
        根据专业特色标签返回多选框对应的定位器

        Args:
            feature_name: 特色标签名称（如 "交叉融合", "国际合作", 等）

        Returns:
            Locator: 专业特色标签多选框的 Playwright 定位器
        """
        if "国" in feature_name:
            return self.iframe.get_by_label("新建专业").get_by_text("国家级特色专业")
        if "省" in feature_name:
            return self.iframe.get_by_label("新建专业").get_by_text("省级特色专业")
        if "卓" in feature_name:
            return self.iframe.get_by_label("新建专业").get_by_text("卓越人才计划")
        if "新" in feature_name:
            return self.iframe.get_by_label("新建专业").get_by_text("新工科建设")
        return self.iframe.get_by_label("新建专业").get_by_text("国家级特色专业")
    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================

    def create_major(self, major_name: str, major_code_school: str, major_code_national: str, major_dept: str, major_prof: str, major_level: str, major_feature: list):
        """新建专业"""
        self.click_element(self.new_major_button)  # 点击新建专业按钮
        self.fill_element(self.major_name_input, major_name)  # 输入专业名称
        self.fill_element(self.major_code_school_input, major_code_school)  # 输入专业代码
        self.fill_element(self.major_code_national_input, major_code_national)  # 输入国家专业代码
        self.click_element(self.major_dept_select)  # 点击所属院系选择框
        self.click_element(self._get_major_dept_select_locator(major_dept))  # 选择所属院系
        self.click_element(self.major_prof_select)  # 点击专业负责人选择框
        self.click_element(self._get_major_prof_select_locator(major_prof))  # 选择专业负责人
        self.click_element(self.major_prof_close_button)  # 关闭专业负责人下拉框
        self.click_element(self._get_major_building_level_radio_locator(major_level))  # 选择专业建设层次
        for feature in major_feature:
            self.click_element(self._get_major_feature_checkbox_locator(feature))  # 选择专业特色标签
        self.click_element(self.confirm_create_button)  # 点击确定创建按钮
    # ==================== 断言方法 ====================

    def is_create_major_success(self) -> bool:
        """检查是否新建专业成功"""
        try:
            self.wait_for_element_visible(self.create_success_message)
            self.logger.info("✓ 新建专业成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 新建专业失败: {e}")
            return False
