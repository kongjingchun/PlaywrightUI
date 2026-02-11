# ========================================
# 专业知识图谱模型页面
# ========================================

import re
from playwright.sync_api import Page

from pages.gqkt.ai_major.major_ai_model.major_ai_model_page import MajorAiModelPage


class MajorGraphModelPage(MajorAiModelPage):
    """
    专业知识图谱模型页面

    提供专业知识图谱/模型相关操作方法。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== 头部按钮 / 搜索 ==========
        # 创建专业图谱按钮
        self.create_major_graph_button = self.iframe.get_by_role("button", name="创建专业图谱")
        # 专业能力节点新增按钮
        self.add_major_ability_node_button = self.iframe.get_by_text(re.compile(r"专业能力节点\d+个节点")).get_by_role("button")
        # 专业知识节点新增按钮
        self.add_major_knowledge_node_button = self.iframe.get_by_text(re.compile(r"专业知识节点\d+个节点")).get_by_role("button")
        # 专业素质节点新增按钮
        self.add_major_quality_node_button = self.iframe.get_by_text(re.compile(r"专业素质节点\d+个节点")).get_by_role("button")
        # 专业问题节点新增按钮
        self.add_major_problem_node_button = self.iframe.get_by_text(re.compile(r"专业问题节点\d+个节点")).get_by_role("button")
        # 标题输入框
        self.title_input = self.iframe.get_by_role("textbox", name="标题")
        # 描述输入框
        self.description_input = self.iframe.get_by_role("textbox", name="描述")
        # 添加按钮
        self.add_button = self.iframe.get_by_role("button", name="添加")
        # 添加节点成功提示
        self.add_node_success_message = self.iframe.locator("xpath=//p[contains(text(),'添加节点成功')]").last
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 关系设置成功提示
        self.success_associate_message = self.iframe.locator("xpath=//p[contains(text(),'关系设置成功')]")
        # ========== 列表 / 图谱区域 ==========

        # ========== 弹窗 / 表单 ==========

    # ==================== 动态定位器生成方法 ====================
    def get_associate_button_by_node_name(self, node_name: str):
        """
        根据节点名称返回关联按钮的定位器

        :param node_name: 节点名称
        :return: 定位到的关联按钮（playwright Locator 对象）
        """
        # 假设：每个节点行包含节点名文本，且该行内有 "关联" 按钮
        return self.iframe.get_by_text(node_name).locator("..").get_by_role("button").nth(1)

    def get_node_type_button_by_type(self, node_type: str):
        """
        根据分类名称返回分类类型按钮的定位器
        :param node_type: 节点类型（如 "专业能力", "专业知识", "专业素质", "专业问题"）
        :return: 分类类型按钮的Playwright定位器
        """
        # 通过正则确保只有该类型按钮匹配，不受数量影响
        if "能力" in node_type:
            return self.iframe.get_by_role("button", name="专业能力节点")
        elif "知识" in node_type:
            return self.iframe.get_by_role("button", name="专业知识节点")
        elif "素质" in node_type:
            return self.iframe.get_by_role("button", name="专业素质节点")
        elif "问题" in node_type:
            return self.iframe.get_by_role("button", name="专业问题节点")
        else:
            raise ValueError(f"未知节点类型: {node_type}")

    def get_associate_checkbox_by_node_name(self, node_name: str):
        """
        根据节点名称返回关联节点的复选框
        :param node_name: 节点名称
        :return: 关联节点的复选框的Playwright定位器
        """
        return self.iframe.locator(f"xpath=//label[contains(.,'{node_name}')]/span[1]")

    # ==================== 操作方法 ====================

    def click_create_major_graph_button(self):
        """点击创建专业图谱按钮"""
        self.click_element(self.create_major_graph_button)

    def click_associate_button_by_node_name(self, node_name: str):
        """
        根据节点名称点击该节点行的关联按钮

        :param node_name: 节点名称
        """
        associate_button = self.get_associate_button_by_node_name(node_name)
        self.hover_element(associate_button)
        self.click_element(associate_button)
    # ==================== 业务方法 ====================

    def add_major_node(self, node_type: str, node_name: str):
        """根据节点类型和名称添加节点"""
        if "能力" in node_type:
            self.click_element(self.add_major_ability_node_button)
        elif "知识" in node_type:
            self.click_element(self.add_major_knowledge_node_button)
        elif "素质" in node_type:
            self.click_element(self.add_major_quality_node_button)
        elif "问题" in node_type:
            self.click_element(self.add_major_problem_node_button)
        self.fill_element(self.title_input, node_name)
        self.click_element(self.add_button)

    def associate_node_by_names(
        self,
        associate_node_name: str,
        target_node_type: str,
        target_node_name: str
    ):
        """
        关联节点操作方法

        :param associate_node_name: 作为发起关联的节点名称（左侧节点/主动方）
        :param target_node_type: 被关联节点类型
        :param target_node_name: 被关联节点名称（右侧节点/被动方）
        """
        # 1. 点击发起关联节点行的“关联”按钮
        self.click_associate_button_by_node_name(associate_node_name)
        # 2. 在弹窗中选择被关联节点类型tab
        if "能力" in target_node_type:
            self.click_element(self.get_node_type_button_by_type(target_node_type))
        elif "知识" in target_node_type:
            self.click_element(self.get_node_type_button_by_type(target_node_type))
        elif "素质" in target_node_type:
            self.click_element(self.get_node_type_button_by_type(target_node_type))
        elif "问题" in target_node_type:
            self.click_element(self.get_node_type_button_by_type(target_node_type))
        else:
            raise ValueError(f"未知被关联节点类型: {target_node_type}")
        # 3. 选择被关联节点名称的复选框
        self.click_element(self.get_associate_checkbox_by_node_name(target_node_name))
        # 4. 点击确定按钮执行关联
        self.click_element(self.confirm_button)
    # ==================== 断言方法 ====================

    def is_add_node_success(self) -> bool:
        """检查是否添加节点成功"""
        try:
            self.wait_for_element_visible(self.add_node_success_message)
            self.logger.info("✓ 添加节点成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加节点失败: {e}")
            return False

    def is_associate_success(self) -> bool:
        """检查是否关系设置成功"""
        try:
            self.wait_for_element_visible(self.success_associate_message)
            self.logger.info("✓ 关系设置成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 关系设置失败: {e}")
            return False

    def is_associate_node_success(self) -> bool:
        """检查是否关联节点成功"""
        try:
            self.wait_for_element_visible(self.success_associate_message)
            self.logger.info("✓ 关联节点成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 关联节点失败: {e}")
            return False
