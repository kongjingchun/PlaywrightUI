# ========================================
# 用户管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class UserManagePage(BasePage):
    """
    用户管理页面

    提供用户管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-2006")

        # ========== 头部按钮/搜索框 ==========
        # 手动创建按钮
        self.create_button = self.iframe.get_by_role("button", name="手动创建")
        # ========== 新增页面 ==========
        # 姓名输入框
        self.name_input = self.iframe.get_by_role("textbox", name="* 姓名")
        # 工号输入框
        self.code_input = self.iframe.get_by_role("textbox", name="学号/工号")
        # 创建用户按钮
        self.create_user_button = self.iframe.get_by_role("button", name="创建用户")
        # 创建成功提示
        self.success_message = self.iframe.get_by_text("创建成功")
    # ==================== 动态定位器生成方法 ====================

    def _get_add_user_role_select_locator(self, role_name: str):
        """角色名称（如：创建教务管理员、创建教师）→ 下拉中该角色选项定位器。"""
        menu_name = role_name if role_name.startswith("创建") else f"创建{role_name}"
        return self.iframe.get_by_role("menuitem", name=menu_name)

    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================
    # 创建用户
    def create_user(self, role_name: str, name: str, code: str):
        """创建用户"""
        self.hover_element(self.create_button)  # hover到手动创建按钮
        self.click_element(self._get_add_user_role_select_locator(role_name))  # 点击角色选择框
        self.fill_input(self.name_input, name)  # 输入姓名
        self.fill_input(self.code_input, code)  # 输入工号
        self.click_element(self.create_user_button)  # 点击创建用户按钮
        result = self.wait_for_element_visible(self.success_message)
        self.logger.info("创建用户成功")
        return result
