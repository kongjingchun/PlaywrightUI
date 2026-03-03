# ========================================
# 能力 group graph 页面（课程建设 - AI 纵线模型）
# ========================================
# 能力图谱支持多级嵌套：一级能力 -> 子能力 -> 孙能力
# 每个能力可配置：名称、描述、标签、关联知识点
# ========================================

from playwright.sync_api import Page

from pages.gqkt.teacher_workbench.course_workbench import CourseWorkbenchPage


class CapabilityGroupGraphPage(CourseWorkbenchPage):
    """
    能力图谱页面

    提供课程工作台下能力图谱相关操作方法，继承课程工作台公共 iframe 与能力。
    支持创建图谱、添加一级能力、添加子能力、关联知识点等操作。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # iframe：课程工作台内容区域
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # ----- 图谱操作 -----
        # 创建图谱按钮
        self.create_graph_button = self.iframe.get_by_role("button", name="创建图谱")
        # 创建图谱成功提示
        self.create_graph_success_message = self.iframe.locator("xpath=//p[contains(text(),'图谱创建成功')]")
        # 编辑按钮
        self.edit_button = self.iframe.get_by_role("button", name="编辑")
        # 根节点定位器
        self.root_node_locator = self.iframe.get_by_role("heading").nth(1)
        # 修改根节点按钮
        self.modify_root_node_button = self.iframe.locator("xpath=//div[@class = 'root-node-actions']//button[1]")
        # 根节点下添加能力按钮（添加一级能力）
        self.add_ability_button = self.iframe.locator(".root-node-actions > button:nth-child(2)")
        # 确定按钮（弹窗内通用）
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 确认按钮（modal内的“确认”按钮）
        self.submit_button = self.iframe.get_by_role("button", name="确认")

        # ----- 能力表单（主表单 / 弹窗共用） -----
        # 能力名称输入框
        self.ability_name_input = self.iframe.get_by_role("textbox", name="请输入能力（必填）")
        # 能力描述输入框
        self.ability_description_input = self.iframe.locator("#w-e-textarea-1")
        # 标签输入框
        self.tag_input = self.iframe.locator("xpath=//div[text()='标签']/following-sibling :: div//input")
        # 关闭标签下拉框按钮
        self.close_tag_dropdown_button = self.iframe.locator("xpath=//div[text()='标签']/following-sibling :: div//i[contains(@class,'select')]")
        # 添加关联知识点按钮
        self.add_related_knowledge_button = self.iframe.get_by_role("button", name="添加关联知识点")
        # 搜索知识点输入框
        self.search_knowledge_input = self.iframe.get_by_role("textbox", name="搜索知识点")
        # 选择关联按钮（知识点选择弹窗内）
        self.select_related_button = self.iframe.get_by_role("button", name="选择关联")
        self.save_button = self.iframe.get_by_role("button", name="保存")
        # 能力创建成功提示（一级/子能力创建后均显示）
        self.create_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建成功')]")

    # --------------------- 动态定位器生成方法 ---------------------
    def get_knowledge_point_locator_by_name(self, knowledge_name: str):
        """
        根据知识点名称返回知识点的定位器

        :param knowledge_name: 知识点名称
        :return: knowledge point locator
        """
        return self.iframe.get_by_title(knowledge_name)

    def get_ability_locator_by_name(self, ability_name: str):
        """
        根据能力名称返回能力的定位器，用于 hover 操作

        :param ability_name: 能力名称
        :return: 能力定位器
        """
        return self.iframe.get_by_role("heading", name=ability_name)
    def get_add_ability_button_by_name(self, ability_name: str):
        """
        根据能力名称返回新增能力按钮的定位器

        :param ability_name: 能力名称
        :return: 新增能力按钮定位器
        """
        return self.iframe.locator(f"xpath=//div[./div/h5[text() = '{ability_name}']]/div/button[3]")
    def get_tag_option_locator_by_name(self, tag_name: str):
        """
        根据标签名称返回标签下拉选项的定位器

        :param tag_name: 标签名称
        :return: 标签下拉选项定位器
        """
        # 假设标签下拉选项为 role="option"，并且名称为 tag_name
        return self.iframe.get_by_role("option", name=tag_name)

    # ---------------------- 操作方法 ----------------------

    def click_create_graph_button(self):
        """点击创建图谱按钮"""
        self.click_element(self.create_graph_button)
    
    def click_edit_button(self):
        """点击编辑按钮"""
        self.click_element(self.edit_button)

    def add_related_knowledge_points(self, knowledge_names: list):
        """
        关联知识点到当前正在新增/编辑的能力
        步骤：
            1. 点击添加关联知识点按钮
            2. 输入知识点名称（支持多次）
            3. 鼠标hover到知识点
            4. 点击选择关联
            5. 最后点击确定按钮

        :param knowledge_names: 需要关联的知识点名称列表
        """
        if not knowledge_names:
            return
        # 1. 点击添加关联知识点按钮
        self.click_element(self.add_related_knowledge_button)

        for knowledge_name in knowledge_names:
            # 2. 输入知识点名称，等待下拉展示
            self.fill_element(self.search_knowledge_input, knowledge_name)
            # 3. hover 到知识点行以高亮/激活
            self.hover_element(self.get_knowledge_point_locator_by_name(knowledge_name))
            # 4. 点击选择关联（行内按钮或直接点击行）
            self.click_element(self.select_related_button)
        # 5. 点击确定按钮
        self.click_element(self.confirm_button)

    def fill_sub_ability_form_and_save(
        self,
        ability_name: str,
        ability_desc: str = "",
        tags: list = None,
        knowledge_names: list = None
    ):
        """
        填写子能力表单并保存（弹窗已打开时调用）
        一级能力和子能力共用此表单结构。

        :param ability_name: 能力名称
        :param ability_desc: 能力描述，可选
        :param tags: 标签列表，可选
        :param knowledge_names: 关联知识点列表，可选
        """
        # 填写能力名称（必填）
        self.fill_element(self.ability_name_input, ability_name)
        # 填写能力描述（可选）
        if ability_desc:
            self.fill_element(self.ability_description_input, ability_desc)
        # 填写标签（可选，每个标签输入后按回车）
        for tag in tags:
            self.fill_element(self.tag_input, tag)
            self.click_element(self.get_tag_option_locator_by_name(tag))
            self.click_element(self.close_tag_dropdown_button)
        # 关联知识点（可选，打开弹窗搜索并选择）
        if knowledge_names:
            self.add_related_knowledge_points(knowledge_names)
        # 点击确定
        self.click_element(self.submit_button)

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

    # ---------------------- 业务方法 ----------------------
    def add_main_ability(self, ability_name: str, ability_desc: str = "", tags: list = None, knowledge_names: list = None):
        """
        添加一级能力（根节点下的直接子能力）

        :param ability_name: 能力名称
        :param ability_desc: 能力描述，可选
        :param tags: 标签列表，可选
        :param knowledge_names: 关联知识点列表，可选
        """
        # hover 到根节点以显示添加能力按钮
        self.hover_element(self.root_node_locator)
        # 点击添加一级能力按钮，打开表单弹窗
        self.click_element(self.add_ability_button)
        # 填写表单并保存
        self.fill_sub_ability_form_and_save(ability_name, ability_desc, tags, knowledge_names)

    def add_sub_ability(self, parent_ability: str, sub_ability_name: str, sub_ability_desc: str = "", tags: list = None, knowledge_names: list = None):
        """
        给指定父能力下添加子能力（支持多级嵌套）

        :param parent_ability: 父能力名称（需先 hover 才能看到添加按钮）
        :param sub_ability_name: 子能力名称
        :param sub_ability_desc: 子能力描述，可选
        :param tags: 子能力标签列表，可选
        :param knowledge_names: 子能力关联知识点列表，可选
        """
        # hover 到父能力卡片以显示操作按钮
        self.hover_element(self.get_ability_locator_by_name(parent_ability))
        # 点击添加子能力按钮，打开表单弹窗
        self.click_element(self.get_add_ability_button_by_name(parent_ability))
        # 填写表单并保存
        self.fill_sub_ability_form_and_save(sub_ability_name, sub_ability_desc, tags, knowledge_names)

    # ---------------------- 断言方法 ----------------------
    def is_add_sub_ability_success(self) -> bool:
        """检查是否添加能力成功（等待创建成功提示出现）"""
        try:
            self.wait_for_element_visible(self.create_success_message)
            self.logger.info("✓ 添加能力成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加能力失败: {e}")
            return False