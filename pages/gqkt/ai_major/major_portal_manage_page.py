# ========================================
# 专业门户管理页面
# ========================================

from playwright.sync_api import Page

from base.base_page import BasePage


class MajorPortalManagePage(BasePage):
    """
    专业门户管理页面

    提供专业门户管理相关的操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        # 专业门户列表页iframe
        self.iframe_2104 = page.frame_locator("iframe#app-iframe-2104")

        # 专业门户编辑页iframe
        self.iframe_3005 = page.frame_locator("iframe#app-iframe-3005")
        # ========== 头部按钮 / 搜索 ==========

        # ========== 列表区域 ==========

        # ========== 编辑页面 ==========
        # 编辑页面按钮
        self.edit_page_button = self.iframe_3005.get_by_role("button", name="编辑页面")
        # 头菜单栏定位
        self.header_menu_locator = self.iframe_3005.get_by_role("img", name="logo")
        # 标题输入框
        self.title_input = self.iframe_3005.locator("xpath=//div[./label[text()='标题']]//input")
        # 发布按钮
        self.publish_button = self.iframe_3005.get_by_role("button", name="发布")
        # 发布确定按钮
        self.publish_confirm_button = self.iframe_3005.get_by_label("发布确认").get_by_role("button", name="确定")
        # 打开专业门户按钮
        self.open_major_portal_button = self.iframe_3005.get_by_role("link", name="打开专业门户")
        # 发布成功提示
        self.publish_success_message = self.iframe_3005.locator("xpath=//p[contains(text(),'发布成功')]")
        # ========== 弹窗 / 表单 ==========

    # ==================== 动态定位器生成方法 ====================
    def _get_major_row_edit_button_locator(self, major_name: str):
        """
        根据专业名称返回对应专业行的编辑按钮的定位器

        Args:
            major_name (str): 专业名称

        Returns:
            Locator: 对应行的编辑按钮的 Playwright 定位器
        """
        # 假设表格行中，专业名称在某一列，编辑按钮为同一行的某一按钮（如 '编辑' 按钮）
        return self.iframe_2104.locator("tr", has_text=major_name).get_by_role("button", name="编辑")
    # ==================== 页面操作 ====================

    def click_edit_page_button(self, major_name: str):
        """
        根据专业名称点击对应的编辑按钮
        """
        self.click_element(self._get_major_row_edit_button_locator(major_name))
    # ==================== 业务方法 ====================

    def edit_page(self, title: str):
        """
        编辑专业门户页面
        """
        self.click_element(self.edit_page_button)
        self.click_element(self.header_menu_locator)
        self.fill_element(self.title_input, title)
        self.click_element(self.publish_button)
        self.click_element(self.publish_confirm_button)
    # ==================== 断言方法 ====================

    def is_publish_success(self) -> bool:
        """检查是否发布成功"""
        try:
            self.wait_for_element_visible(self.publish_success_message)
            self.logger.info("✓ 发布成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 发布失败: {e}")
            return False
