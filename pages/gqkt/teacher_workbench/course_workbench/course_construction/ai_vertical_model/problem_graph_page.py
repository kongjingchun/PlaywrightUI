# ========================================
# 问题图谱页面（课程建设 - AI 纵线模型）
# ========================================
# 问题图谱支持多级嵌套：一级问题 -> 子问题 -> 孙问题
# 每个问题可配置：名称、描述、标签、关联知识点
# ========================================

from playwright.sync_api import Page

from pages.gqkt.teacher_workbench.course_workbench import CourseWorkbenchPage


class ProblemGraphPage(CourseWorkbenchPage):
    """
    问题图谱页面

    提供课程工作台下问题图谱相关操作方法，继承课程工作台公共 iframe 与能力。
    支持创建图谱、添加一级问题、添加子问题、关联知识点等操作。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # iframe：课程工作台内容区域
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # ----- 图谱操作 -----
        # 创建图谱按钮
        self.create_graph_button = self.iframe.get_by_role("button", name="创建问题图谱")
        # 创建图谱成功提示
        self.create_graph_success_message = self.iframe.locator("xpath=//p[contains(text(),'图谱创建成功')]")
        # -------- 添加层级---------
        # 添加层级按钮
        self.add_level_button = self.iframe.get_by_role("button", name="添加层级")
        # 层级标题输入框
        self.level_title_input = self.iframe.get_by_role("textbox", name="层级标题")
        # 层级描述输入框
        self.level_description_input = self.iframe.get_by_role("textbox", name="层级描述")
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # -------- 添加问题---------
        # 问题标题输入框
        self.problem_title_input = self.iframe.get_by_role("textbox", name="请输入问题（必填）")
        # 问题答案输入框
        self.problem_answer_input = self.iframe.locator("#w-e-textarea-1")
        # 标签输入框
        self.tag_input = self.iframe.locator("xpath=//div[text()='标签']/following-sibling :: div//input")
        # 关闭标签下拉框按钮
        self.close_tag_dropdown_button = self.iframe.locator("xpath=//div[text()='标签']/following-sibling :: div//i[contains(@class,'select')]")
        # 添加关联问题按钮
        self.add_related_problem_button = self.iframe.get_by_role("button", name="添加关联问题")
        # 关联问题确定按钮
        self.confirm_related_problem_button = self.iframe.get_by_label("选择关联问题").get_by_role("button", name="确定")
        # 添加关联知识点按钮
        self.add_related_knowledge_button = self.iframe.get_by_role("button", name="添加关联知识点")
        # 搜索知识点输入框
        self.search_knowledge_input = self.iframe.get_by_role("textbox", name="搜索知识点")
        # 选择关联知识点洗的选择关联按钮
        self.select_related_knowledge_button = self.iframe.get_by_label("选择关联知识点").get_by_role("button", name="选择关联")
        # 关联知识点确定按钮
        self.confirm_related_knowledge_button = self.iframe.get_by_label("选择关联知识点").get_by_role("button", name="确定")
        # 添加问题确定按钮
        self.confirm_add_problem_button = self.iframe.get_by_label("添加问题").get_by_role("button", name="确定")

    # ------------------动态定位器生成方法------------------
    def get_add_problem_button_by_level_title(self, level_title: str):
        """
        根据问题层级标题，返回对应的添加问题按钮

        :param level_title: 问题层级标题
        :return: 对应层级下的“添加问题”按钮定位器
        """
        return self.iframe.get_by_text(f"{level_title} 添加问题").get_by_role("button", name="添加问题")
    def get_tag_option_locator_by_name(self, tag_name: str):
        """
        根据标签名称返回标签下拉选项的定位器

        :param tag_name: 标签名称
        :return: 标签下拉选项定位器
        """
        return self.iframe.get_by_role("option", name=tag_name)
    def get_knowledge_point_locator_by_name(self, knowledge_name: str):
        """
        根据知识点名称返回知识点的定位器

        :param knowledge_name: 知识点名称
        :return: knowledge point locator
        """
        return self.iframe.get_by_title(knowledge_name)

    def get_problem_locator_by_name(self, problem_name: str):
        """
        根据问题名称返回问题的定位器（用于主页面图谱节点）

        :param problem_name: 问题名称
        :return: 问题定位器
        """
        return self.iframe.get_by_text(problem_name)

    def get_related_problem_option_locator_by_name(self, problem_name: str):
        """
        选择关联问题弹窗内，根据问题名称返回问题选项的定位器（仅匹配弹窗内列表项，避免与图谱节点重复匹配）

        :param problem_name: 问题名称
        :return: 弹窗内问题选项定位器
        """
        return self.iframe.get_by_label("选择关联问题").locator(f"xpath=//div[./div[@class ='relation-node-title' and contains(.,'{problem_name}')]]")
    def get_select_related_problem_button_by_name(self, problem_name: str):
        """
        根据问题名称返回对应问题的“选择关联”按钮定位器

        :param problem_name: 问题名称
        :return: “选择关联”按钮定位器
        """
        return self.iframe.get_by_label("选择关联问题").locator(f"xpath=//div[./div[@class ='relation-node-title' and contains(.,'{problem_name}')]]//button")

    # ==================== 操作方法 ====================
    def click_create_problem_graph_button(self):
        """
        点击“创建问题图谱”按钮
        """
        self.click_element(self.create_graph_button)



    # ==================== 业务方法 ====================
    def create_problem_graph_level(self, level_title: str, level_description: str):
        """
        创建图谱层级
        """
        self.click_element(self.add_level_button) # 点击添加层级按钮
        self.fill_element(self.level_title_input, level_title) # 填写层级标题
        if level_description:  # 层级描述可能为空
            self.fill_element(self.level_description_input, level_description) # 填写层级描述
        self.click_element(self.confirm_button) # 点击确定按钮

    def add_problem_to_level(self, level_title: str, problem_title: str, answer: str = None, tags: list = None, related_problems: list = None, knowledge_points: list = None):
        """
        在指定层级下添加问题

        :param level_title: 层级名称
        :param problem_title: 问题标题
        :param answer: 答案（可选）
        :param tags: 标签列表（可选）
        :param related_problems: 关联问题名称列表（可选）
        :param knowledge_points: 关联知识点名称列表（可选）
        """
        # 1. 点击层级下的"添加问题"按钮
        add_problem_btn = self.get_add_problem_button_by_level_title(level_title)
        self.click_element(add_problem_btn)

        # 2. 输入问题标题
        self.fill_element(self.problem_title_input, problem_title)

        # 3. 输入答案（如果有）
        if answer is not None:
            self.fill_element(self.problem_answer_input, answer)

        # 4. 标签
        if tags:
            for tag in tags:
                self.fill_element(self.tag_input, tag) 
                self.click_element(self.get_tag_option_locator_by_name(tag))
            # 点击关闭下拉框按钮
            self.click_element(self.close_tag_dropdown_button)

        # 5. 关联问题（在「选择关联问题」弹窗内定位选项与按钮，避免与图谱/其他弹窗重复匹配）
        if related_problems:
            self.click_element(self.add_related_problem_button)
            for rel_problem in related_problems:
                self.hover_element(self.get_related_problem_option_locator_by_name(rel_problem))
                self.click_element(self.get_select_related_problem_button_by_name(rel_problem))
            self.click_element(self.confirm_related_problem_button)

        # 6. 关联知识点
        if knowledge_points:
            self.click_element(self.add_related_knowledge_button)
            for kp in knowledge_points:
                self.fill_element(self.search_knowledge_input, kp)
                kp_locator = self.get_knowledge_point_locator_by_name(kp)
                self.hover_element(kp_locator)
                self.click_element(self.select_related_knowledge_button)
            self.click_element(self.confirm_related_knowledge_button)

        # 7. 点击确定按钮提交
        self.click_element(self.confirm_add_problem_button)

    # ---------------------- 断言方法 ----------------------
    def is_create_graph_success(self) -> bool:
        """检查是否创建图谱成功"""
        try:
            self.wait_for_element_visible(self.create_graph_success_message)
            self.logger.info("✓ 创建图谱成功")
            return True
        except Exception as e: 
            self.logger.error(f"✗ 创建图谱失败: {e}")
            return False