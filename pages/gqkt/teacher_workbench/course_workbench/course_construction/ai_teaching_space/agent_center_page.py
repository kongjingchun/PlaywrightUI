# ========================================
# 智能体中心页面（课程建设 - AI 教创空间）
# ========================================
# TODO: 待补充定位器与操作方法
# ========================================

from playwright.sync_api import Page

from pages.gqkt.teacher_workbench.course_workbench import CourseWorkbenchPage


class AgentCenterPage(CourseWorkbenchPage):
    """
    智能体中心页面

    提供课程工作台下 AI 教创空间 - 智能体中心相关操作方法。
    具体定位方法待后续补充。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # iframe：课程工作台内容区域
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")
        
        # 智能体广场按钮
        self.agent_square_button = self.iframe.get_by_role("button", name="智能体广场")
        # 添加成功提示
        self.add_success_toast = self.iframe.locator("xpath=//p[contains(text(),'已成功将') and contains(text(),'添加到课程智能体列表')]").last
    # ================== 动态定位器生成方法 ==================
    def get_join_agent_button_by_name(self, agent_name: str):
        """
        根据智能体名称返回对应加入按钮的定位器

        :param agent_name: 智能体名称
        :return: 加入按钮的定位器
        """
        return self.iframe.locator("div.agent-square-card").filter(has_text=agent_name).get_by_role("button", name="加入")

    # ================== 操作方法 ==================
    def click_agent_square_button(self):
        """点击智能体广场按钮"""
        self.click_element(self.agent_square_button)

    def click_join_agent_button_by_name(self, agent_name: str):
        """点击对应智能体名称的加入按钮"""
        self.click_element(self.get_join_agent_button_by_name(agent_name))

    # ================== 断言方法 ==================
    def is_add_agent_success(self) -> bool:
        """检查是否添加成功提示出现"""
        try:
            self.wait_for_element_visible(self.add_success_toast)
            self.logger.info("✓ 添加成功提示出现")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加成功提示未出现: {e}")
            return False