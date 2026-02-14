# ========================================
# 课程内容页面（课程建设 - 课程设计 - 课程内容）
# ========================================

from playwright.sync_api import Page

from ... import CourseWorkbenchPage


class CourseContentPage(CourseWorkbenchPage):
    """
    课程内容页面

    提供课程设计下课程内容相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")
        # ====== 头部按钮 / 搜索框 ======
        # 管理学习单元按钮
        self.manage_learning_unit_button = self.iframe.get_by_role("button", name="管理学习单元")

        # ============================== 章节页面 ==============================
        # 创建章节按钮
        self.create_chapter_button = self.iframe.get_by_role("button", name="创建章节")
        # 章节标题输入框
        self.chapter_title_input = self.iframe.get_by_role("textbox", name="章节标题")
        # 章节描述输入框
        self.chapter_description_input = self.iframe.get_by_role("textbox", name="章节描述")
        # 创建按钮
        self.create_button = self.iframe.get_by_role("button", name="创建", exact=True)
        # 创建章节成功提示框（.last 取最新一条，用于断言）
        self.create_chapter_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建') and contains(text(),'章节成功')]").last
        # 关联学习单元全选按钮
        self.associate_learning_unit_all_select_button = self.iframe.get_by_role("row", name="标题 类型 创建人 创建时间 状态").locator("span").first
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 成功添加提示框
        self.success_add_learning_unit_message = self.iframe.locator("xpath=//p[contains(text(),'成功添加')]").last
        # 成功为章节添加知识点章节提示框
        self.success_add_knowledge_graph_message = self.iframe.locator("xpath=//p[contains(text(),'成功为章节') and contains(text(),'添加知识点章节')]").last
        # ============================版本管理页面===============================
        # 版本管理按钮
        self.version_management_button = self.iframe.get_by_role("button", name="版本管理")
        # 从其他版本复制按钮
        self.copy_from_other_version_button = self.iframe.get_by_role("menuitem", name="从其他版本复制")
        # 请选择要复制的版本下拉框
        self.select_version_dropdown = self.iframe.get_by_text("请选择要复制的版本")
        # 默认版本下拉框选项
        self.default_version_dropdown_option = self.iframe.get_by_role("option", name="默认版本")
        # 版本名称输入框
        self.version_name_input = self.iframe.get_by_role("textbox", name="版本名称")
        # 创建版本成功
        self.create_version_success_message = self.iframe.locator("xpath=//p[contains(text(),'版本成功')]").last
        # ===============================管理学习单元页面===============================
        # 创建学习单元按钮
        self.create_learning_unit_button = self.iframe.get_by_role("button", name="创建学习单元")
        # ======================新建学习单元页面===============================
        # 学习单元标题输入框
        self.new_learning_unit_title_input = self.iframe.get_by_role("textbox", name="* 学习单元标题")
        # 学习单元正文输入框
        self.new_learning_unit_content_input = self.iframe.locator("xpath=//div[@contenteditable='true']")
        # 第一个选择按钮（有可能是全选按钮，也有可能是第一个文件选择按钮）
        self.new_learning_unit_first_select_button = self.iframe.get_by_label("选择文件").get_by_role("row").locator("span").first

        # 是否允许评论切换按钮
        self.new_learning_unit_allow_comment_switch = self.iframe.get_by_text("允许", exact=True)
        # 是否计入成绩
        self.new_learning_unit_into_score_switch = self.iframe.get_by_text("计入", exact=True)

        # 创建按钮
        self.new_learning_unit_create_button = self.iframe.get_by_role("button", name="创建", exact=True)
        # 创建成功提示框
        self.new_learning_unit_create_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建成功')]").last
        # ============新建视频学习单元页面============
        # 请选择视频文件按钮
        self.new_learning_unit_video_file_button = self.iframe.get_by_role("button", name="请选择视频文件")
        # ============新建资料学习单元页面============
        # 请选择资料文件按钮
        self.new_learning_unit_material_file_button = self.iframe.get_by_role("button", name="请选择资料文件")
        # ============新建课件学习单元页面============
        # 请选择课件文件按钮
        self.new_learning_unit_courseware_file_button = self.iframe.get_by_role("button", name="请选择课件文件")
        # ============新建讨论学习单元页面============
        # 请选择讨论文件按钮
        self.new_learning_unit_discussion_file_button = self.iframe.get_by_role("button", name="请选择附件文件")
        # ============新建作业学习单元页面============
        # 请选择作业文件按钮
        self.new_learning_unit_homework_file_button = self.iframe.get_by_role("button", name="请选择作业")
        # 作业全选按钮
        self.new_learning_unit_homework_all_select_button = self.iframe.get_by_role("row", name="标题 组卷方式 创建时间").locator("span").first
        # ============新建考试学习单元页面============
        # 请选择考试文件按钮
        self.new_learning_unit_exam_file_button = self.iframe.get_by_role("button", name="请选择试卷")
        # 考试全选按钮
        self.new_learning_unit_exam_all_select_button = self.iframe.get_by_role("row", name="标题 组卷方式 创建时间").locator("span").first
        # ============新建链接学习单元页面============
        # 请选择链接文件按钮
        self.new_learning_unit_link_file_button = self.iframe.get_by_role("button", name="请选择链接")
        # ============新建音频学习单元页面============
        # 请选择音频文件按钮
        self.new_learning_unit_audio_file_button = self.iframe.get_by_role("button", name="请选择音频文件", exact=True)

    # ======================动态定位器生成方法======================

    def get_create_learning_unit_button_by_learning_unit_type(self, learning_unit_type: str):
        """
        根据学习单元类型返回创建学习单元对应类型按钮的定位器

        :param learning_unit_type: 学习单元类型
        :return: 创建学习单元对应类型按钮的定位器
        """
        return self.iframe.get_by_role("menuitem", name=learning_unit_type)

    def get_create_subsection_button_by_chapter_name(self, chapter_name: str):
        """
        根据章节名称返回创建子章节按钮的定位器

        :param chapter_name: 章节名称
        :return: 对应章节下"创建子章节"按钮的定位器
        """
        xpath = f"//div[./div/span[text()='{chapter_name}']]//button[contains(.,'子章节')]"
        return self.iframe.locator(f"xpath={xpath}")

    def get_create_learning_unit_button_by_chapter_name(self, chapter_name: str):
        """
        根据章节名称返回创建学习单元按钮的定位器

        :param chapter_name: 章节名称
        :return: 对应章节下"创建学习单元"按钮的定位器
        """
        xpath = f"//div[./div/span[text()='{chapter_name}']]//button[contains(.,'学习单元')]"
        return self.iframe.locator(f"xpath={xpath}")

    def get_associate_knowledge_graph_button_by_chapter_name(self, chapter_name: str):
        """
        根据章节名称返回关联知识图谱按钮的定位器

        :param chapter_name: 章节名称
        :return: 对应章节下"关联知识图谱"按钮的定位器
        """
        xpath = f"//div[./div/span[text()='{chapter_name}']]//button[contains(.,'知识图谱')]"
        return self.iframe.locator(f"xpath={xpath}")

    def get_edit_button_by_chapter_name(self, chapter_name: str):
        """
        根据章节名称返回编辑按钮的定位器

        :param chapter_name: 章节名称
        :return: 对应章节下"编辑"按钮的定位器
        """
        xpath = f"//div[./div/span[text()='{chapter_name}']]//button[contains(.,'编辑')]"
        return self.iframe.locator(f"xpath={xpath}")

    def get_delete_button_by_chapter_name(self, chapter_name: str):
        """
        根据章节名称返回删除按钮的定位器

        :param chapter_name: 章节名称
        :return: 对应章节下"删除"按钮的定位器
        """
        xpath = f"//div[./div/span[text()='{chapter_name}']]//button[contains(.,'删除')]"
        return self.iframe.locator(f"xpath={xpath}")

    def get_knowledge_graph_checkbox_by_name(self, knowledge_graph_name: str):
        """
        根据图谱节点名称返回对应勾选的定位器

        :param knowledge_graph_name: 图谱节点名称
        :return: 对应图谱节点的勾选框定位器
        """
        return self.iframe.get_by_text(knowledge_graph_name)
    # ==================== 操作方法 ====================

    def set_allow_comment_switch(self, allow: bool):
        """
        设置是否允许评论开关

        :param allow: True 表示允许评论，False 表示不允许评论
        """
        # 如果不需要允许评论，则点击允许评论切换按钮
        if not allow:
            self.click_element(self.new_learning_unit_allow_comment_switch)
            # 设置是否计入成绩，默认为false，如果为true需要点击

    def set_into_score_switch(self, into_score: bool):
        """
        设置是否计入成绩开关

        :param into_score: True 表示计入成绩，False 表示不计入成绩
        """
        if into_score:
            self.click_element(self.new_learning_unit_into_score_switch)

    def click_create_learning_unit_and_select_type(self, learning_unit_type: str):
        """
        点击创建学习单元按钮并选择学习单元类型

        :param learning_unit_type: 学习单元类型（如"视频"、"文档"等）
        """
        self.click_element(self.create_learning_unit_button)
        self.click_element(self.get_create_learning_unit_button_by_learning_unit_type(learning_unit_type))

    # ==================== 业务方法 ====================
    def _fill_learning_unit_form(
        self,
        learning_unit_title: str,
        learning_unit_content: str = "",
        count_grade: bool = False,
        allow_comment: bool = True
    ):
        """
        内部方法：填写学习单元的新建表单，包括类型、标题、正文及是否允许评论/计入成绩。
        调用前需已处于课程工作空间 iframe 内。
        """
        # 输入学习单元标题
        self.fill_element(self.new_learning_unit_title_input, learning_unit_title)
        # 输入学习单元正文（富文本框）
        self.fill_element(self.new_learning_unit_content_input, learning_unit_content)
        # 设置允许评论开关（默认为允许，如关闭则点击切换按钮）
        self.set_allow_comment_switch(allow=allow_comment)
        # 设置计入成绩开关
        self.set_into_score_switch(into_score=count_grade)

    def create_video_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建视频学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("视频")  # 点击创建学习单元按钮并选择视频学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_video_file_button)  # 点击请选择视频文件按钮
        self.click_element(self.new_learning_unit_first_select_button)  # 点击第一个文件选择按钮
        self.click_element(self.confirm_button)  # 点击确定按钮
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_material_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建资料学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("资料")  # 点击创建学习单元按钮并选择资料学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_material_file_button)  # 点击请选择资料文件按钮
        self.click_element(self.new_learning_unit_first_select_button)  # 点击第一个文件选择按钮
        self.click_element(self.confirm_button)  # 点击确定按钮
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_courseware_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建课件学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("课件")  # 点击创建学习单元按钮并选择课件学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_courseware_file_button)  # 点击请选择课件文件按钮
        self.click_element(self.new_learning_unit_first_select_button)  # 点击第一个文件选择按钮
        self.click_element(self.confirm_button)  # 点击确定按钮
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_discussion_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建讨论学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("讨论")  # 点击创建学习单元按钮并选择讨论学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_homework_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建作业学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("作业")  # 点击创建学习单元按钮并选择作业学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_homework_file_button)  # 点击请选择作业文件按钮
        self.click_element(self.new_learning_unit_homework_all_select_button)  # 点击第一个文件选择按钮
        self.click_element(self.confirm_button)  # 点击确定按钮
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_exam_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建考试学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("考试")  # 点击创建学习单元按钮并选择考试学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_exam_file_button)  # 点击请选择考试文件按钮
        self.click_element(self.new_learning_unit_exam_all_select_button)  # 点击考试全选按钮
        self.click_element(self.confirm_button)  # 点击确定按钮
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_link_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建链接学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("链接")  # 点击创建学习单元按钮并选择链接学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_link_file_button)  # 点击请选择链接文件按钮
        self.click_element(self.new_learning_unit_first_select_button)  # 点击第一个文件选择按钮
        self.click_element(self.confirm_button)  # 点击确定按钮
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_audio_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建音频学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("音频")  # 点击创建学习单元按钮并选择音频学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_audio_file_button)  # 点击请选择音频文件按钮
        self.click_element(self.new_learning_unit_first_select_button)  # 点击第一个文件选择按钮
        self.click_element(self.confirm_button)  # 点击确定按钮
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_classroom_learning_unit(self, learning_unit_title: str, learning_unit_content: str = ""):
        """
        创建课堂学习单元

        :param learning_unit_title: 学习单元标题
        :param learning_unit_content: 学习单元正文
        """
        self.click_create_learning_unit_and_select_type("课堂")  # 点击创建学习单元按钮并选择课堂学习单元类型
        self._fill_learning_unit_form(learning_unit_title=learning_unit_title, learning_unit_content=learning_unit_content)
        self.click_element(self.new_learning_unit_create_button)  # 点击创建按钮

    def create_chapter(self, chapter_name: str, chapter_description: str = ""):
        """
        创建章节

        :param chapter_name: 章节名称
        :param chapter_description: 章节描述
        """
        self.click_element(self.create_chapter_button)  # 点击创建章节按钮
        self.fill_element(self.chapter_title_input, chapter_name)  # 填写章节标题
        self.fill_element(self.chapter_description_input, chapter_description)  # 填写章节描述
        self.click_element(self.create_button)  # 点击创建按钮

    def add_subsection_to_chapter(self, chapter_name: str, subsection_name: str, subsection_description: str = ""):
        """
        给指定章节添加子章节

        :param chapter_name: 章节名称
        :param subsection_name: 子章节名称
        """
        self.click_element(self.get_create_subsection_button_by_chapter_name(chapter_name))  # 点击创建子章节按钮
        self.fill_element(self.chapter_title_input, subsection_name)  # 填写子章节标题
        self.fill_element(self.chapter_description_input, subsection_description)  # 填写子章节描述
        self.click_element(self.create_button)  # 点击创建按钮

    def add_all_learning_units_to_chapter(self, chapter_name: str):
        """
        给指定章节添加全部学习单元操作

        :param chapter_name: 章节名称
        """
        self.click_element(self.get_create_learning_unit_button_by_chapter_name(chapter_name))  # 点击创建学习单元按钮
        self.click_element(self.associate_learning_unit_all_select_button)  # 全选关联学习单元
        self.click_element(self.confirm_button)  # 点击确定按钮进行添加

    def add_knowledge_graph_to_chapter(self, chapter_name: str, knowledge_graph_name: str):
        """
        给指定章节添加关联指定知识图谱

        :param chapter_name: 章节名称
        :param knowledge_graph_name: 知识图谱名称
        """

        self.click_element(self.get_associate_knowledge_graph_button_by_chapter_name(chapter_name))  # 点击关联知识图谱按钮

        # 在弹出框查找知识图谱，假设有一个搜索框
        kg_search_input = self.iframe.get_by_placeholder("请输入知识图谱名称")
        self.fill_element(kg_search_input, knowledge_graph_name)

        # 选中目标知识图谱
        kg_row = self.iframe.get_by_role("row", name=knowledge_graph_name)
        kg_select_radio = kg_row.get_by_role("radio")
        self.click_element(kg_select_radio)

        # 点击确定按钮
        self.click_element(self.confirm_button)

    def associate_first_level_knowledge_graph_by_chapter(self, chapter_name: str, knowledge_graph_name: str):
        """
        根据章节名称，在关联图谱弹窗中勾选第一个一级节点进行关联

        :param chapter_name: 章节名称
        """
        self.click_element(self.get_associate_knowledge_graph_button_by_chapter_name(chapter_name))  # 点击关联知识图谱按钮
        self.click_element(self.get_knowledge_graph_checkbox_by_name(knowledge_graph_name))  # 选中目标知识图谱
        self.click_element(self.confirm_button)  # 点击确定按钮

    def create_version_from_default(self, version_name: str):
        """
        从“默认版本”复制并创建新版本

        :param version_name: 新版本名称
        """
        # 点击版本管理按钮
        self.click_element(self.version_management_button)
        # 点击“从其他版本复制”菜单项
        self.click_element(self.copy_from_other_version_button)
        # 点击版本选择下拉框
        self.click_element(self.select_version_dropdown)
        # 选择“默认版本”
        self.click_element(self.default_version_dropdown_option)
        # 填写新版本名称
        self.fill_element(self.version_name_input, version_name)
        # 点击确定按钮
        self.click_element(self.confirm_button)

    # ==================== 断言方法 ====================

    def is_create_learning_unit_success(self) -> bool:
        """检查是否创建学习单元成功"""
        try:
            self.wait_for_element_visible(self.new_learning_unit_create_success_message)
            self.logger.info("✓ 创建学习单元成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建学习单元失败: {e}")
            return False

    def is_create_chapter_success(self) -> bool:
        """检查是否创建章节成功"""
        try:
            self.wait_for_element_visible(self.create_chapter_success_message)
            self.logger.info("✓ 创建章节成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建章节失败: {e}")
            return False

    def is_add_learning_units_to_chapter_success(self) -> bool:
        """检查是否添加学习单元成功"""
        try:
            self.wait_for_element_visible(self.success_add_learning_unit_message)
            self.logger.info("✓ 添加学习单元成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加学习单元失败: {e}")
            return False

    def is_add_knowledge_graph_to_chapter_success(self) -> bool:
        """检查是否添加知识点章节成功"""
        try:
            self.wait_for_element_visible(self.success_add_knowledge_graph_message)
            self.logger.info("✓ 添加知识点章节成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加知识点章节失败: {e}")
            return False

    def is_create_version_success(self) -> bool:
        """检查是否创建版本成功"""
        try:
            self.wait_for_element_visible(self.create_version_success_message)
            self.logger.info("✓ 创建版本成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建版本失败: {e}")
            return False
