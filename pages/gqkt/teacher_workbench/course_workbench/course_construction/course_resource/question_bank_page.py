# ========================================
# 题库页面（课程建设 - 课程资源 - 题库）
# ========================================

from typing import List, Optional, Union

from playwright.sync_api import Page

from .course_resource_page import CourseResourcePage


class QuestionBankPage(CourseResourcePage):
    """
    题库页面

    提供题库相关操作方法，继承课程资源页面公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # 新建题目按钮
        self.new_question_button = self.iframe.get_by_role("button", name="新建题目")
        # 题目内容输入框
        self.question_content_input = self.iframe.locator("xpath=//div[text()='题目内容']/following-sibling::div//div[@contenteditable='true']")
        # 参考答案输入框
        self.reference_answer_input = self.iframe.locator("xpath=//div[text()='参考答案']/following-sibling::div//div[@contenteditable='true']")
        # 题目解析输入框
        self.question_analysis_input = self.iframe.locator("xpath=//div[text()='题目解析']/following-sibling::div//div[@contenteditable='true']")
        # 选择知识点按钮
        self.select_knowledge_button = self.iframe.get_by_role("button", name="选择知识点").last
        # 搜索知识点
        self.search_knowledge_input = self.iframe.get_by_role("textbox", name="搜索知识点")
        # 选择关联按钮
        self.select_related_button = self.iframe.get_by_role("button", name="选择关联").last
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 创建按钮
        self.create_button = self.iframe.get_by_role("button", name="创建")
        # 题目创建成功
        self.question_create_success_message = self.iframe.locator("xpath=//p[contains(text(),'题目创建成功')]")

    # ==================== 动态定位器生成方法 ====================

    def get_question_type_option_locator(self, question_type: str):
        """
        根据题目类型返回下拉框中对应类型的定位器

        :param question_type: 题目类型（如 "单选题", "多选题", "判断题" 等）
        :return: 题目类型选项的Locator对象
        """
        # 题型下拉选项假设通过 role="option" 且 name=question_type 唯一标识
        return self.iframe.get_by_role("menuitem", name=question_type)

    def get_knowledge_locator_by_name(self, knowledge_name: str):
        """
        根据知识点名称返回知识点定位器

        :param knowledge_name: 知识点名称
        :return: 知识点的定位器
        """
        return self.iframe.get_by_text(knowledge_name)

    def get_is_open_to_student_switch_locator(self, knowledge_name: str):
        """
        返回是开放给学生开关的定位器

        :param knowledge_name: 知识点名称
        :return: 是开放给学生开关的定位器
        """
        return self.iframe.locator(f"xpath=//span[text()='{knowledge_name}']/following-sibling::div/div/span[2]")

    # ==================== 操作方法 ====================

    def click_new_question_by_type(self, question_type: str):
        """
        根据题目类型点击对应的新建题目类型按钮

        :param question_type: 题目类型（如 "单选题", "多选题", "判断题" 等）
        """
        self.hover_element(self.new_question_button)  # 悬停新建题目按钮
        self.click_element(self.get_question_type_option_locator(question_type))  # 点击题目类型选项

    def click_select_related_by_knowledge_name(self, knowledge_name: str):
        """
        根据知识点名称点击选择关联按钮
        :param knowledge_name: 知识点名称
        """
        # 填写搜索框
        self.fill_element(self.search_knowledge_input, knowledge_name)
        # 点击对应的知识点（可适当等待）
        self.hover_element(self.get_knowledge_locator_by_name(knowledge_name))
        # 点击选择关联按钮
        self.click_element(self.select_related_button)
    # ==================== 业务方法 ====================

    def create_short_answer_question(
        self,
        question_content: str,
        reference_answer: str,
        question_analysis: Optional[str] = None,
        knowledge_info: Optional[Union[dict, List[dict]]] = None
    ):
        """
        新建简答题

        :param question_content: 题目内容
        :param reference_answer: 参考答案
        :param question_analysis: 题目解析（可选）
        :param knowledge_info: 知识点信息（可选），支持单个或多个：
            - 单个：{"name": "知识点名称", "open_to_student": True/False}
            - 多个：[{"name": "知识点1", "open_to_student": True}, {"name": "知识点2", "open_to_student": False}]
        """
        # 1. 点击新建简答题按钮
        self.click_new_question_by_type("简答题")

        # 2. 输入题目内容
        self.fill_element(self.question_content_input, question_content)

        # 3. 输入参考答案
        self.fill_element(self.reference_answer_input, reference_answer)

        # 4. 输入题目解析（如果传入参数有）
        if question_analysis is not None:
            self.fill_element(self.question_analysis_input, question_analysis)

        # 5. 关联知识点并设置是否开放给学生（支持多个知识点）
        if knowledge_info:
            knowledge_list = knowledge_info if isinstance(knowledge_info, list) else [knowledge_info]
            if knowledge_list:
                self.click_element(self.select_knowledge_button)
                for k in knowledge_list:
                    if "name" in k:
                        self.fill_element(self.search_knowledge_input, k["name"])
                        self.click_select_related_by_knowledge_name(k["name"])
                self.click_element(self.confirm_button)
                for k in knowledge_list:
                    if k.get("open_to_student"):
                        self.click_element(self.get_is_open_to_student_switch_locator(k["name"]))
        # 6. 点击创建按钮
        self.click_element(self.create_button)
    # ==================== 断言方法 ====================

    def is_question_create_success(self) -> bool:
        """检查是否创建题目成功"""
        try:
            self.wait_for_element_visible(self.question_create_success_message)
            self.logger.info("✓ 创建题目成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建题目失败: {e}")
            return False
