# ========================================
# 部门列表管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class DeptListManagePage(BasePage):
    """
    部门列表管理页面

    提供部门列表管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-3004")

        # ========== 头部按钮/搜索框 ==========
        # 新建院系按钮
        self.new_dept_button = self.iframe.get_by_role("button", name="新建院系")

        # ========== 部门列表 ==========

        # ========== 新增/编辑部门 ==========
        # 院系名称输入框
        self.dept_name_input = self.iframe.get_by_role("textbox", name="院系名称")
        # 院系代码输入框
        self.dept_code_input = self.iframe.get_by_role("textbox", name="院系代码")
        # 确认创建按钮
        self.confirm_new_dept_button = self.iframe.get_by_role("button", name="确定")
        # 创建成功提示
        self.new_dept_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建成功')]")

    # ==================== 动态定位器生成方法 ====================

    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================

    def create_dept(self, dept_name: str, dept_code: str):
        """创建院系"""
        self.click_element(self.new_dept_button)
        self.fill_element(self.dept_name_input, dept_name)
        self.fill_element(self.dept_code_input, dept_code)
        self.click_element(self.confirm_new_dept_button)

    # ==================== 断言方法 ====================

    def is_create_dept_success(self) -> bool:
        """检查是否创建院系成功"""
        try:
            self.wait_for_element_visible(self.new_dept_success_message)
            self.logger.info("✓ 创建院系成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建院系失败: {e}")
            return False
