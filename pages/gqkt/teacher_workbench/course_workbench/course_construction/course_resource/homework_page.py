# ========================================
# 作业页面（课程建设 - 课程资源 - 作业）
# ========================================

from playwright.sync_api import Page

from .course_resource_page import CourseResourcePage


class HomeworkPage(CourseResourcePage):
    """
    作业页面

    提供作业相关操作方法，继承课程资源页面公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # 新建作业按钮
        self.new_homework_button = self.iframe.get_by_role("button", name="新建作业")
        # 新建作业标题输入框
        self.new_homework_title_input = self.iframe.get_by_placeholder("请输入作业标题")
        # 创建并编辑按钮
        self.create_and_edit_button = self.iframe.get_by_role("button", name="创建并编辑")
        # 选择题目按钮
        self.select_question_button = self.iframe.get_by_role("button", name="选择题目")
        # 当前页全选复选框
        self.current_page_all_select_checkbox = self.iframe.get_by_role("row", name="题目内容 题目类型 分数 最后修改时间").locator("span")
        # 确定选择按钮
        self.confirm_select_button = self.iframe.get_by_role("button", name="确定选择")
        # 保存按钮
        self.save_button = self.iframe.get_by_role("button", name="保存")
        # 保存成功提示
        self.save_success_message = self.iframe.locator("xpath=//p[contains(text(),'保存成功')]")
    # ==================== 动态定位器生成方法 ====================

    # ==================== 操作方法 ====================

    # ==================== 业务方法 ====================

    def create_homework(self, homework_title: str):
        """
        新建作业

        :param homework_title: 作业标题
        """
        self.click_element(self.new_homework_button, multi="last")  # 点击新建作业按钮
        self.fill_element(self.new_homework_title_input, homework_title)  # 输入作业标题
        self.click_element(self.create_and_edit_button)  # 点击创建并编辑按钮
        self.click_element(self.select_question_button, multi="last")  # 点击选择题目按钮
        self.click_element(self.current_page_all_select_checkbox, multi="last")  # 点击当前页全选复选框
        self.click_element(self.confirm_select_button)  # 点击确定选择按钮
        self.click_element(self.save_button)  # 点击保存按钮

    # ==================== 断言方法 ====================

    def is_homework_save_success(self) -> bool:
        """检查是否保存作业成功"""
        try:
            self.wait_for_element_visible(self.save_success_message)
            self.logger.info("✓ 保存作业成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 保存作业失败: {e}")
            return False
