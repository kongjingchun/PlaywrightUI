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
        # 工号筛选
        self.code_filter_input = self.iframe.get_by_role("textbox", name="工号筛选：")
        # 手动创建按钮
        self.create_button = self.iframe.get_by_role("button", name="手动创建")

        # ========== 用户行操作 ==========
        # 编辑按钮
        self.edit_button = self.iframe.get_by_role("menuitem", name="编辑")
        # 绑定按钮
        self.bind_button = self.iframe.get_by_role("menuitem", name="绑定")
        # ========== 新增页面 ==========
        # 姓名输入框
        self.name_input = self.iframe.get_by_role("textbox", name="* 姓名")
        # 工号输入框
        self.code_input = self.iframe.get_by_role("textbox", name="学号/工号")
        # 创建用户按钮
        self.create_user_button = self.iframe.get_by_role("button", name="创建用户")
        # 创建成功提示
        self.create_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建成功')]")
        # =========绑定页面=========
        # 平台用户ID输入框
        self.platform_user_id_input = self.iframe.get_by_role("textbox", name="平台用户ID")
        # 确认绑定按钮
        self.confirm_bind_button = self.iframe.get_by_role("button", name="确认绑定")
        # 绑定用户成功提示
        self.bind_success_message = self.iframe.locator("xpath=//p[contains(text(),'绑定用户成功')]")
    # ==================== 动态定位器生成方法 ====================

    def _get_add_user_role_select_locator(self, role_name: str):
        """角色名称（如：创建教务管理员、创建教师）→ 下拉中该角色选项定位器。"""
        menu_name = role_name if role_name.startswith("创建") else f"创建{role_name}"
        return self.iframe.get_by_role("menuitem", name=menu_name)

    def _get_user_row_operation_locator(self, code: str):
        """根据工号获取用户行操作定位器"""
        return self.iframe.locator("tr", has_text=code).locator("i")
    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================
    # 创建用户
    def create_user(self, role_name: str, name: str, code: str):
        """创建用户"""
        self.hover_element(self.create_button)  # hover到手动创建按钮
        self.click_element(self._get_add_user_role_select_locator(role_name))  # 点击角色选择框
        self.fill_element(self.name_input, name)  # 输入姓名
        self.fill_element(self.code_input, code)  # 输入工号
        self.click_element(self.create_user_button)  # 点击创建用户按钮

    def bind_user(self, code: str, platform_user_id: str):
        """绑定用户"""
        self.fill_element(self.code_filter_input, code)  # 输入工号筛选
        self.hover_element(self._get_user_row_operation_locator(code))  # 点击用户行操作按钮
        self.click_element(self.bind_button)  # 点击绑定按钮
        self.fill_element(self.platform_user_id_input, platform_user_id)  # 输入平台用户ID
        self.click_element(self.confirm_bind_button)  # 点击确认绑定按钮
    # ==================== 断言方法 ====================

    def is_create_user_success(self) -> bool:
        """检查是否创建用户成功"""
        try:
            self.wait_for_element_visible(self.create_success_message)
            self.logger.info("✓ 创建用户成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建用户失败: {e}")
            return False

    def is_bind_user_success(self) -> bool:
        """检查是否绑定用户成功"""
        try:
            self.wait_for_element_visible(self.bind_success_message)
            self.logger.info("✓ 绑定用户成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 绑定用户失败: {e}")
            return False
