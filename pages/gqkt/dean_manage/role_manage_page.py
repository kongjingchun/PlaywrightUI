# ========================================
# 角色管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class RoleManagePage(BasePage):
    """
    角色管理页面

    提供角色管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-2008")

        # ========== 头部按钮/搜索框 ==========

        # ========== 角色列表 ==========

        # ========== 分配用户列表页 ==========
        # 用户搜索输入框
        self.user_search_input = self.iframe.get_by_role("textbox", name="搜索：")
        # 确定分配按钮
        self.confirm_assign_button = self.iframe.get_by_role("button", name="确定分配")
        # 分配成功提示框
        self.assign_success_message = self.iframe.locator("xpath=//p[contains(text(),'成功')]")

        # ========== 新增角色页面 ==========

        # ========== 权限配置 ==========

    # ==================== 动态定位器生成方法 ====================
    def get_assign_button_by_role_name(self, role_name: str):
        """
        根据角色名称返回该角色对应的分配按钮定位器

        :param role_name: 角色名称
        :return: 分配按钮的定位器
        """
        return self.iframe.locator("tr", has_text=role_name).get_by_role("button", name="分配")

    def get_user_checkbox_by_name(self, user_name: str):
        """
        根据用户名称返回复选框定位器

        Element UI 的 el-checkbox 将原生 input 隐藏，需点击可见的 .el-checkbox 或 .el-checkbox__inner。

        :param user_name: 用户名称
        :return: 该用户的复选框定位器（可见的 checkbox 包装元素）
        """
        return self.iframe.get_by_role("row", name=user_name).locator(".el-checkbox")

    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================

    def assign_role_to_user(self, role_name: str, user_name: str):
        """
        给某用户分配某角色

        :param role_name: 角色名称
        :param user_name: 用户名称
        """
        # 点击对应角色的“分配”按钮
        self.click_element(self.get_assign_button_by_role_name(role_name))
        # 在弹出的分配用户页面搜索用户
        self.fill_element(self.user_search_input, user_name)
        # 选择用户
        self.click_element(self.get_user_checkbox_by_name(user_name))
        # 点击确定分配按钮
        self.click_element(self.confirm_assign_button)

    # ==================== 断言方法 ====================
    def is_assign_role_success(self) -> bool:
        """
        断言是否分配角色成功

        :return: 是否分配角色成功
        """
        return self.is_visible(self.assign_success_message)
