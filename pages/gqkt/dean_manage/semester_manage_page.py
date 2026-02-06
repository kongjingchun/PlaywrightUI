# ========================================
# 学期管理页面
# ========================================

from playwright.sync_api import Page
from typing import Optional

from base.base_page import BasePage
from config.env_config import EnvConfig


class SemesterManagePage(BasePage):
    """
    学期管理页面

    提供学期管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.iframe = page.frame_locator("iframe#app-iframe-1006")

        # ========== 头部按钮/搜索框 ==========
        # 新增学期按钮
        self.new_semester_button = self.iframe.get_by_role("button", name="新增")

        # ========== 学期列表 ==========

        # ========== 新增/编辑学期 ==========
        # 所属学年展开定位器
        self.academic_year_expand_locator = self.iframe.get_by_text("请选择所属学年")
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 确认新增按钮
        self.confirm_new_semester_button = self.iframe.get_by_label("确认新增").get_by_role("button", name="确定")
        # 创建成功提示
        self.create_semester_success_message = self.iframe.locator("xpath=//p[contains(text(),'新增学期成功')]")
        # ========== 学期详情 ==========

    # ==================== 动态定位器生成方法 ====================
    def _get_academic_year_option_locator(self, academic_year: str):
        """
        根据所属学年值返回下拉框中对应的定位器

        Args:
            academic_year: 学年名称（如 "2023-2024 学年"）

        Returns:
            Locator: 所属学年下拉选项的 Playwright 定位器
        """
        return self.iframe.get_by_role("option", name=academic_year)
    # ==================== 页面操作 ====================

    # ==================== 业务方法 ====================

    def create_semester(self, academic_year: str):
        """新建学期"""
        self.click_element(self.new_semester_button)
        self.click_element(self.academic_year_expand_locator)
        self.click_element(self._get_academic_year_option_locator(academic_year))
        self.click_element(self.confirm_button)
        self.click_element(self.confirm_new_semester_button)

    # ==================== 断言方法 ====================

    def is_create_semester_success(self) -> bool:
        """检查是否创建学期成功"""
        try:
            self.wait_for_element_visible(self.create_semester_success_message)
            self.logger.info("✓ 创建学期成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建学期失败: {e}")
            return False
