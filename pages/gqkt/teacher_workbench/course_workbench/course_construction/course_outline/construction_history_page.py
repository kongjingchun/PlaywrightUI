# ========================================
# 建设历程页面（课程建设 - 课程大纲）
# ========================================

from playwright.sync_api import Page

from ... import CourseWorkbenchPage


class ConstructionHistoryPage(CourseWorkbenchPage):
    """
    建设历程页面

    提供课程大纲下建设历程相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # ========== 头部按钮 / 搜索 ==========
        # 编辑按钮
        self.edit_button = self.iframe.get_by_role("button", name="编辑")
        # 建设时间输入框
        self.construction_time_input = self.iframe.get_by_placeholder("请选择建设时间")
        # 建设内容输入框
        self.construction_content_input = self.iframe.get_by_role("textbox", name="建设内容")
        # 获得荣誉输入框
        self.honor_input = self.iframe.get_by_role("textbox", name="获得荣誉")
        # 建设团队输入框
        self.team_input = self.iframe.get_by_role("textbox", name="建设团队")
        # 保存按钮
        self.save_button = self.iframe.get_by_role("button", name="保存")
        # 保存成功提示
        self.save_success_message = self.iframe.locator("xpath=//p[contains(text(),'保存成功')]")
        # ========== 弹窗 / 表单 ==========
    # ==================== 操作方法 ====================
    # ==================== 业务方法 ====================

    def set_construction_history(self, construction_time: str = None, content: str = None, honor: str = None, team: str = None):
        """
        设置建设历程内容

        :param construction_time: 建设时间，例如 "2023-09-01"
        :param content: 建设内容
        :param honor: 获得荣誉，可选
        :param team: 建设团队，可选
        """
        self.click_element(self.edit_button)  # 点击编辑按钮
        if construction_time:
            self.fill_element(self.construction_time_input, construction_time)  # 填写建设时间
        if content:
            self.fill_element(self.construction_content_input, content)  # 填写建设内容
        if honor:
            self.fill_element(self.honor_input, honor)  # 填写获得荣誉
        if team:
            self.fill_element(self.team_input, team)  # 填写建设团队
        self.click_element(self.save_button)  # 点击保存按钮
    # ==================== 断言方法 ====================

    def is_set_construction_history_success(self) -> bool:
        """检查是否设置建设历程成功"""
        try:
            self.wait_for_element_visible(self.save_success_message)
            self.logger.info("✓ 建设历程设置成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 建设历程设置失败: {e}")
            return False
