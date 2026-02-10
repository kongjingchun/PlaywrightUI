# ========================================
# 行政班管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class AdminClassManagePage(BasePage):
    """
    行政班管理页面

    提供行政班管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-2005")

        # ========== 头部按钮/搜索框 ==========
        # 新建行政班
        self.new_admin_class_button = self.iframe.get_by_role("button", name="新建行政班")

        # ========== 行政班列表 ==========

        # ========== 新增/编辑行政班 ==========
        # 行政班名称输入框
        self.admin_class_name_input = self.iframe.get_by_role("textbox", name="行政班名称")
        # 行政班编号输入框
        self.admin_class_id_input = self.iframe.get_by_role("textbox", name="行政班编号")
        # 选择学院下拉框
        self.admin_class_dept_select = self.iframe.get_by_label("新建行政班").get_by_text("请选择学院")
        # 选择专业下拉框
        self.admin_class_major_select = self.iframe.get_by_label("新建行政班").get_by_text("请先选择学院")
        # 选择年纪下拉框
        self.admin_class_grade_select = self.iframe.get_by_label("新建行政班").get_by_text("请选择年级")
        # 行政班描述
        self.admin_class_description_input = self.iframe.get_by_role("textbox", name="描述")
        # 创建提交按钮
        self.confirm_create_button = self.iframe.get_by_role("button", name="创建")
        # 创建成功提示框
        self.create_admin_class_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建成功')]")
        # ========== 行政班详情 ==========

    # ==================== 动态定位器生成方法 ====================
    def get_dept_option_locator(self, dept_name: str):
        """
        根据传入的学院名称，返回学院下拉框中对应学院选项的定位器

        :param dept_name: 学院名称
        :return: 对应学院选项的locator
        """
        return self.iframe.get_by_role("option", name=dept_name)

    def get_major_option_locator(self, major_name: str):
        """
        根据传入的专业名称，返回专业下拉框中对应专业选项的定位器
        """
        return self.iframe.get_by_role("option", name=major_name)

    def get_grade_option_locator(self, grade_name: str):
        """
        根据传入的年级名称，返回年级下拉框中对应年级选项的定位器
        """
        # 如果grade_name后面没有“级”，自动追加
        if not grade_name.endswith("级"):
            grade_name = f"{grade_name}级"
        return self.iframe.get_by_role("option", name=grade_name)

    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================
    def create_admin_class(self, admin_class_name: str, admin_class_id: str, admin_class_dept: str, admin_class_major: str, admin_class_grade: str, admin_class_description: str):
        """新建行政班"""
        self.click_element(self.new_admin_class_button)  # 点击新建行政班按钮
        self.fill_element(self.admin_class_name_input, admin_class_name)  # 输入行政班名称
        self.fill_element(self.admin_class_id_input, admin_class_id)  # 输入行政班编号
        self.click_element(self.admin_class_dept_select)  # 点击学院下拉框
        self.click_element(self.get_dept_option_locator(admin_class_dept))  # 选择学院
        self.click_element(self.admin_class_major_select)  # 点击专业下拉框
        self.click_element(self.get_major_option_locator(admin_class_major))  # 选择专业
        self.click_element(self.admin_class_grade_select)  # 点击年级下拉框
        self.click_element(self.get_grade_option_locator(admin_class_grade))  # 选择年级
        self.fill_element(self.admin_class_description_input, admin_class_description)  # 输入行政班描述
        self.click_element(self.confirm_create_button)  # 点击创建提交按钮

    # ==================== 断言方法 ====================
    def is_create_admin_class_success(self) -> bool:
        """检查是否新建行政班成功"""
        try:
            self.wait_for_element_visible(self.create_admin_class_success_message)
            self.logger.info("✓ 新建行政班成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 新建行政班失败: {e}")
            return False
