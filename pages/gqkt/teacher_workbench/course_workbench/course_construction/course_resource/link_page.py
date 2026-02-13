# ========================================
# 链接页面（课程建设 - 课程资源 - 链接）
# ========================================

from playwright.sync_api import Page

from .course_resource_page import CourseResourcePage


class LinkPage(CourseResourcePage):
    """
    链接页面

    提供链接相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")
        # 新建链接按钮
        self.new_link_button = self.iframe.get_by_role("button", name="新建链接")
        # 链接地址输入框
        self.link_url_input = self.iframe.get_by_role("textbox", name="链接地址")
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 链接创建成功提示
        self.link_create_success_message = self.iframe.locator("xpath=//p[contains(text(),'链接创建成功')]")

    # ==================== 业务方法 ====================
    def create_link(self, link_url: str):
        """新建链接"""
        self.click_element(self.new_link_button)
        self.fill_element(self.link_url_input, link_url)
        self.click_element(self.confirm_button)

    # ==================== 断言方法 ====================
    def is_link_create_success(self) -> bool:
        """检查是否创建链接成功"""
        try:
            self.wait_for_element_visible(self.link_create_success_message)
            self.logger.info("✓ 创建链接成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建链接失败: {e}")
            return False
