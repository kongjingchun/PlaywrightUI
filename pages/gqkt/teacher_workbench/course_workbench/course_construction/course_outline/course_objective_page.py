# ========================================
# 课程目标页面（课程建设 - 课程大纲）
# ========================================

from playwright.sync_api import Page

from ... import CourseWorkbenchPage


class CourseObjectivePage(CourseWorkbenchPage):
    """
    课程目标页面

    提供课程大纲下课程目标相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")

        # ========== 课程目标概览 ==========
        # 编辑描述按钮
        self.edit_description_button = self.iframe.get_by_role("button", name="编辑描述")
        # 描述内容输入框
        self.description_input = self.iframe.get_by_role("textbox", name="描述内容")
        # 保存按钮
        self.save_button = self.iframe.get_by_role("button", name="保存")
        # 保存成功提示
        self.save_success_message = self.iframe.locator("xpath=//p[contains(.,'保存成功')]")
        # ========== 课程目标管理 ==========
        # 添加目标按钮
        self.add_goal_button = self.iframe.get_by_role("button", name="添加目标")
        # 目标标题输入框
        self.goal_title_input = self.iframe.get_by_role("textbox", name="目标标题")
        # 添加标签按钮
        self.add_tag_button = self.iframe.get_by_role("button", name="添加标签")
        # 标签输入框
        self.tag_input = self.iframe.get_by_role("textbox", name="标签")
        # 创建按钮
        self.create_button = self.iframe.get_by_role("button", name="创建")
        # 创建课程目标成功提示
        self.create_goal_success_message = self.iframe.locator("xpath=//p[contains(.,'创建课程目标成功')]")
        # ========== 关联毕业要求==========
        # 添加毕业要求
        self.add_graduate_requirement_button = self.iframe.get_by_role("button", name="添加毕业要求")
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 添加毕业要求关联成功
        self.add_graduate_requirement_success_message = self.iframe.locator("xpath=//p[contains(.,'添加毕业要求关联成功')]")
    # ==================== 动态定位器生成方法 ====================

    def get_associate_graduate_requirement_button_by_goal_title(self, goal_title: str):
        """
        根据目标标题返回对应行的关联毕业要求按钮
        """
        return self.iframe.locator("tr", has_text=goal_title).get_by_role("button", name="关联毕业要求")

    def get_indicator_locator_by_name(self, indicator_name: str):
        """
        根据指标名称返回指标点击区域的定位器
        :param indicator_name: 指标名称
        :return: 指标区域的locator
        """
        return self.iframe.get_by_text(indicator_name)
    # ==================== 操作方法 ====================

    # ==================== 业务方法 ====================

    def edit_description(self, description: str):
        """
        编辑课程目标描述信息，并保存
        """
        self.click_element(self.edit_description_button)  # 点击编辑描述按钮
        self.fill_element(self.description_input, description)  # 填写描述内容
        self.click_element(self.save_button)  # 点击保存按钮

    def create_goal(self, goal_title: str, goal_tags):
        """
        创建课程目标

        :param goal_title: 目标标题
        :param goal_tags: 标签，支持 str 或 list[str]
        """
        self.click_element(self.add_goal_button)  # 点击添加目标按钮
        self.fill_element(self.goal_title_input, goal_title)  # 填写目标标题
        self.click_element(self.add_tag_button)  # 点击添加标签按钮
        self.fill_element(self.tag_input, goal_tags)  # 填写标签
        self.click_element(self.create_button)  # 点击创建按钮

    def associate_goal_with_indicator(self, goal_title: str, indicator_name: str):
        """
        根据课程目标标题和指标名称进行关联操作

        :param goal_title: 课程目标标题
        :param indicator_name: 需要关联的指标名称
        """
        # 点击目标对应行的"关联毕业要求"按钮
        self.click_element(self.get_associate_graduate_requirement_button_by_goal_title(goal_title))  # 点击关联毕业要求按钮
        self.click_element(self.add_graduate_requirement_button)  # 点击添加毕业要求按钮
        self.click_element(self.get_indicator_locator_by_name(indicator_name))  # 点击弹窗里的对应指标进行关联
        self.click_element(self.confirm_button)  # 点击确定按钮
    # ==================== 断言方法 ====================

    def is_edit_description_success(self) -> bool:
        """检查是否编辑课程目标描述信息成功"""
        try:
            self.wait_for_element_visible(self.save_success_message)
            self.logger.info("✓ 课程目标描述信息保存成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 课程目标描述信息保存失败: {e}")
            return False

    def is_create_goal_success(self) -> bool:
        """检查是否创建课程目标成功"""
        try:
            self.wait_for_element_visible(self.create_goal_success_message)
            self.logger.info("✓ 创建课程目标成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 创建课程目标失败: {e}")
            return False

    def is_associate_goal_with_indicator_success(self) -> bool:
        """检查是否关联课程目标与指标成功"""
        try:
            self.wait_for_element_visible(self.add_graduate_requirement_success_message)
            self.logger.info("✓ 关联课程目标与指标成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 关联课程目标与指标失败: {e}")
            return False
