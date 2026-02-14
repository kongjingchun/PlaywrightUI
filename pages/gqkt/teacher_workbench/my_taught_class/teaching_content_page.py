# ========================================
# 教学内容页面（我教的班 - 教学内容）
# ========================================

from playwright.sync_api import Page

from .my_taught_class_page import MyTaughtClassPage


class TeachingContentPage(MyTaughtClassPage):
    """
    教学内容页面

    提供我教的班下教学内容相关操作方法，继承我教的班页面公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== 教学内容区域 ==========
        # 引用课程内容按钮
        self.reference_course_content_button = self.iframe.get_by_role("button", name="引用课程内容")
        # 确定引用按钮
        self.confirm_reference_button = self.iframe.get_by_role("button", name="确定引用")
        # 成功引用
        self.success_reference_message = self.iframe.locator("xpath=//p[contains(text(),'成功引用')]").last
        # 添加章按钮
        self.add_chapter_button = self.iframe.get_by_role("button", name="添加章")
        # 章节标题输入框
        self.chapter_title_input = self.iframe.get_by_role("textbox", name="章节标题")
        # 章节描述输入框
        self.chapter_description_input = self.iframe.get_by_role("textbox", name="章节描述")
        # 创建按钮
        self.create_button = self.iframe.get_by_role("button", name="创建")
        # 创建章节成功提示框
        self.success_create_chapter_message = self.iframe.locator("xpath=//p[contains(text(),'创建') and contains(text(),'章节成功')]").last
        # 添加节菜单
        self.add_section_menu = self.iframe.get_by_role("menuitem", name="添加节")
        # 添加学习单元菜单
        self.add_learning_unit_menu = self.iframe.get_by_role("menuitem", name="添加学习单元")
        # 添加知识图谱菜单
        self.add_knowledge_graph_menu = self.iframe.get_by_role("menuitem", name="添加知识图谱")
        # 学习单元全选按钮
        self.learning_unit_all_select_button = self.iframe.get_by_role("row", name="标题 类型 创建人 创建时间 状态").locator("span").first
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 成功添加学习单元提示框
        self.success_add_learning_unit_message = self.iframe.locator("xpath=//p[contains(text(),'成功添加')]").last
        # 成功为章节添加
        self.success_add_knowledge_graph_message = self.iframe.locator("xpath=//p[contains(text(),'成功为章节') and contains(text(),'添加知识点章节')]").last
    # ==================== 操作方法 ====================

    def click_operation_button_by_version_name(self, version_name: str):
        """
        根据版本名称，点击版本所在行的操作按钮

        :param version_name: 版本名称字符串
        """
        self.click_element(self.iframe.get_by_role("row", name=version_name).get_by_text("选择", exact=True))

    def click_operation_plus_button_by_chapter_name(self, chapter_name: str):
        """
        根据章节名称点击操作+按钮

        :param chapter_name: 章节名称
        """
        self.click_element(self.iframe.locator(f"xpath=//div[./div/span[text()='{chapter_name}']]/div/div[1]"))

    def click_knowledge_graph_checkbox_by_name(self, knowledge_graph_name: str):
        """
        根据图谱节点名称点击勾选对应节点

        :param knowledge_graph_name: 知识图谱节点名称
        """
        self.click_element(self.iframe.get_by_label("选择知识点").get_by_text(knowledge_graph_name))
    # =================== 业务方法 ===================

    def reference_course_content(self, version_name: str):
        """
        引用教学内容

        :param version_name: 版本名称字符串
        """
        self.click_element(self.reference_course_content_button)  # 点击引用课程内容按钮
        self.click_element(self.iframe.get_by_role("row", name=version_name).get_by_text("选择", exact=True))  # 点击版本所在行的选择按钮
        self.click_element(self.confirm_reference_button)  # 点击确定引用按钮

    def add_chapter(self, chapter_name: str, chapter_description: str = ""):
        """
        添加章节

        :param chapter_name: 章节名称
        :param chapter_description: 章节描述
        """
        self.click_element(self.add_chapter_button)  # 点击添加章按钮
        self.fill_element(self.chapter_title_input, chapter_name)  # 填写章节标题
        self.fill_element(self.chapter_description_input, chapter_description)  # 填写章节描述
        self.click_element(self.create_button)  # 点击创建按钮

    def add_section_to_chapter(self, chapter_name: str, section_name: str, section_description: str = ""):
        """
        添加节

        :param chapter_name: 章节名称
        :param section_name: 节名称
        :param section_description: 节描述
        """
        self.click_operation_plus_button_by_chapter_name(chapter_name)  # 点击操作+按钮
        self.click_element(self.add_section_menu)  # 点击添加节菜单
        self.fill_element(self.chapter_title_input, section_name)  # 填写节标题
        self.fill_element(self.chapter_description_input, section_description)  # 填写节描述
        self.click_element(self.create_button)  # 点击创建按钮

    def add_learning_units_to_chapter(self, chapter_name: str):
        """
        添加学习单元

        :param chapter_name: 章节名称
        """
        self.click_operation_plus_button_by_chapter_name(chapter_name)  # 点击操作+按钮
        self.click_element(self.add_learning_unit_menu)  # 点击添加学习单元菜单
        self.click_element(self.learning_unit_all_select_button)  # 点击学习单元全选按钮
        self.click_element(self.confirm_button)  # 点击确定按钮进行添加

    def add_knowledge_graph_to_chapter(self, chapter_name: str, knowledge_graph_name: str):
        """
        添加知识图谱

        :param chapter_name: 章节名称
        :param knowledge_graph_name: 知识图谱名称
        """
        self.click_operation_plus_button_by_chapter_name(chapter_name)  # 点击操作+按钮
        self.click_element(self.add_knowledge_graph_menu)  # 点击添加知识图谱菜单
        self.click_knowledge_graph_checkbox_by_name(knowledge_graph_name)  # 点击知识图谱勾选框
        self.click_element(self.confirm_button)  # 点击确定按钮进行添加
    # =================== 断言方法 ===================

    def is_reference_course_content_success(self) -> bool:
        """
        断言是否成功引用课程内容

        :return: 是否成功引用课程内容
        """
        try:
            self.wait_for_element_visible(self.success_reference_message)
            self.logger.info("✓ 成功引用课程内容")
            return True
        except Exception as e:
            self.logger.error(f"✗ 成功引用课程内容失败: {e}")
            return False

    def is_create_chapter_success(self) -> bool:
        """
        断言是否成功创建章节

        :return: 是否成功创建章节
        """
        try:
            self.wait_for_element_visible(self.success_create_chapter_message)
            self.logger.info("✓ 成功创建章节")
            return True
        except Exception as e:
            self.logger.error(f"✗ 成功创建章节失败: {e}")
            return False

    def is_add_learning_units_to_chapter_success(self) -> bool:
        """
        断言是否成功添加学习单元

        :return: 是否成功添加学习单元
        """
        try:
            self.wait_for_element_visible(self.success_add_learning_unit_message)
            self.logger.info("✓ 成功添加学习单元")
            return True
        except Exception as e:
            self.logger.error(f"✗ 成功添加学习单元失败: {e}")
            return False

    def is_add_knowledge_graph_to_chapter_success(self) -> bool:
        """
        断言是否成功为章节添加知识图谱

        :return: 是否成功为章节添加知识图谱
        """
        try:
            self.wait_for_element_visible(self.success_add_knowledge_graph_message)
            self.logger.info("✓ 成功为章节添加知识图谱")
            return True
        except Exception as e:
            self.logger.error(f"✗ 成功为章节添加知识图谱失败: {e}")
            return False
