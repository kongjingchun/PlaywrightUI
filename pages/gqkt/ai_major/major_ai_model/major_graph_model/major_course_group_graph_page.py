# ========================================
# 专业课程群图谱页面
# ========================================

from playwright.sync_api import Page

from ..major_ai_model_page import MajorAiModelPage


class MajorCourseGroupGraphPage(MajorAiModelPage):
    """
    专业课程群图谱页面

    提供专业课程群图谱相关操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        # 专业课程群图谱与专业 AI 模型共用同一 iframe（已在 MajorAiModelPage 中初始化 self.iframe）

        # ========== 头部按钮 / 搜索 ==========
        # 编辑图谱按钮
        self.edit_graph_button = self.iframe.get_by_role("button", name="编辑图谱")
        # 关联图谱按钮
        self.associate_graph_button = self.iframe.get_by_role("button", name="关联图谱")
        # 确定关联按钮
        self.confirm_associate_button = self.iframe.get_by_role("button", name="确定关联")
        # 关联图谱成功
        self.success_associate_message = self.iframe.locator("xpath=//p[contains(text(),'关联图谱成功')]")
        # ========== 列表 / 图谱区域 ==========

        # ==========关联图谱界面 ==========

        # ========== 弹窗 / 表单 ==========

    # ==================== 动态定位器生成方法 ====================
    def get_graph_checkbox_by_name(self, graph_name: str):
        """
        根据图谱名称返回图谱对应的复选框定位器

        :param graph_name: 图谱名称
        :return: 对应复选框的Playwright定位器
        """
        return self.iframe.locator("tr", has_text=graph_name).locator("span").nth(0)
    # ==================== 操作方法 ====================

    # ==================== 业务方法 ====================
    def associate_graph(self, graph_name: str):
        """
        关联图谱

        :param graph_name: 图谱名称
        """
        self.click_element(self.edit_graph_button)  # 点击编辑图谱按钮
        self.click_element(self.associate_graph_button)  # 点击关联图谱按钮
        self.click_element(self.get_graph_checkbox_by_name(graph_name))  # 点击图谱对应的复选框
        self.click_element(self.confirm_associate_button)  # 点击确定关联按钮
    # ==================== 断言方法 ====================

    def is_associate_graph_success(self) -> bool:
        """检查是否关联图谱成功"""
        try:
            self.wait_for_element_visible(self.success_associate_message)
            self.logger.info("✓ 关联图谱成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 关联图谱失败: {e}")
            return False
