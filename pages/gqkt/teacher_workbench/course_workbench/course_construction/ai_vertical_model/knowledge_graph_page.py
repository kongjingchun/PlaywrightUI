# ========================================
# 知识图谱页面（课程建设 - AI 纵线模型）
# ========================================

from playwright.sync_api import Page

from common.tools import build_path
from pages.gqkt.teacher_workbench.course_workbench import CourseWorkbenchPage


class KnowledgeGraphPage(CourseWorkbenchPage):
    """
    知识图谱页面

    提供课程工作台下知识图谱相关操作方法，继承课程工作台公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # iframe
        self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")
        # ========== 头部按钮 / 搜索 ==========

        # 新建主图谱按钮
        self.new_main_graph_button = self.iframe.get_by_role("button", name="新建主图谱")
        # ========== 图谱 / 列表区域 ==========
        # 编辑数据按钮
        self.edit_data_button = self.iframe.get_by_role("button", name="编辑数据")
        # ========== 新建图谱页面 ==========
        # 图谱名称输入框
        self.graph_name_input = self.iframe.get_by_role("textbox", name="图谱名称")
        # 图谱描述输入框
        self.graph_description_input = self.iframe.get_by_role("textbox", name="图谱描述")
        # 点击上传
        self.click_upload_button = self.iframe.get_by_text("点击上传")
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 新建图谱成功提示框
        self.new_graph_success_message = self.iframe.locator("xpath=//p[contains(text(),'新建图谱成功')]")
        # ========= 编辑图谱页面 ==========
        # 模版导入更新按钮
        self.template_import_update_button = self.iframe.get_by_role("button", name="模板导入&更新")
        # 导入按钮
        self.import_button = self.iframe.get_by_role("dialog", name="模板导入&更新").get_by_role("img").nth(1)
        # 开始导入按钮
        self.start_import_button = self.iframe.get_by_role("button", name="开始导入")
        # 导入中状态
        self.importing_status = self.iframe.get_by_text("导入中")
        # 导入成功
        self.import_success_message = self.iframe.locator("xpath=//p[contains(text(),'导入成功')]").last
        # 添加数据按钮
        self.add_data_button = self.iframe.get_by_role("button", name="添加数据")
        # 标题输入框
        self.title_input = self.iframe.get_by_role("textbox", name="* 标题")
        # 描述输入框
        self.description_input = self.iframe.get_by_role("textbox", name="节点描述")
        # 确定按钮
        self.confirm_button = self.iframe.get_by_role("button", name="确定")
        # 创建成功提示框
        self.create_success_message = self.iframe.locator("xpath=//p[contains(text(),'创建成功')]").last
        # 新建子级按钮
        self.new_sub_node_button = self.iframe.get_by_role("button", name="子级")
        # ========== 弹窗 / 表单 ==========
    # ==================== 动态定位器生成方法 ====================

    def get_node_locator_by_name(self, node_name: str):
        """
        根据节点名称返回节点定位器

        :param node_name: 节点名称
        :return: 节点的定位器
        """
        # 假设节点显示为 role="treeitem" 或 span，名称为node_name
        return self.iframe.locator(f"xpath=//div[contains(@class,'node-item') and contains(.,'{node_name}')]")
    # ==================== 操作方法 ====================

    def click_edit_data_button(self):
        """点击第一个编辑数据按钮"""
        self.click_element(self.edit_data_button.first)

    def click_sub_node_create_button_by_name(self, node_name: str):
        """
        根据节点名称点击节点子级创建按钮

        :param node_name: 节点名称
        """
        node_locator = self.get_node_locator_by_name(node_name)
        self.hover_element(node_locator)
        self.click_element(self.new_sub_node_button)

    # ==================== 业务方法 ====================

    def create_knowledge_graph(self, graph_name: str, graph_description: str, background_image_path: str):
        """新建知识图谱：点击新建主图谱，填写名称与描述，确定"""
        self.click_element(self.new_main_graph_button)  # 点击新建主图谱按钮
        self.fill_element(self.graph_name_input, graph_name)  # 填写图谱名称
        self.fill_element(self.graph_description_input, graph_description)  # 填写图谱描述
        self.upload_file_via_chooser(self.click_upload_button, build_path(background_image_path))  # 上传背景图片
        self.click_element(self.confirm_button)  # 点击确定按钮

    def import_knowledge_graph(self, file_path: str):
        """
        导入知识图谱：点击导入按钮，上传文件，确认导入

        :param file_path: 待导入的文件路径
        """
        self.click_element(self.template_import_update_button)  # 点击模版导入更新按钮
        self.upload_file_via_chooser(self.import_button, build_path(file_path))  # 上传文件
        self.click_element(self.start_import_button)  # 点击开始导入按钮
        self.wait_for_element_hidden(self.importing_status, timeout=30000)  # 等待导入中状态消失（知识图谱导入可能较慢，30秒）

    def add_data(self, title: str, description: str):
        """添加数据：点击添加数据按钮，填写标题与描述，确定"""
        self.click_element(self.add_data_button)  # 点击添加数据按钮
        self.fill_element(self.title_input, title)  # 填写标题
        self.fill_element(self.description_input, description)  # 填写描述
        self.click_element(self.confirm_button)  # 点击确定按钮

    def add_sub_node(self, parent_node_name: str, sub_node_title: str, sub_node_description: str):
        """
        给指定父节点添加子节点

        :param parent_node_name: 父节点名称
        :param sub_node_title: 子节点标题
        :param sub_node_description: 子节点描述
        """
        self.click_sub_node_create_button_by_name(parent_node_name)  # 点击父节点的子级创建按钮
        self.fill_element(self.title_input, sub_node_title)  # 填写子节点标题
        self.fill_element(self.description_input, sub_node_description)  # 填写子节点描述
        self.click_element(self.confirm_button)  # 点击确定按钮
    # ==================== 断言方法 ====================

    def is_create_knowledge_graph_success(self) -> bool:
        """检查是否新建知识图谱成功"""
        try:
            self.wait_for_element_visible(self.new_graph_success_message)
            self.logger.info("✓ 新建知识图谱成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 新建知识图谱失败: {e}")
            return False

    def is_import_knowledge_graph_success(self) -> bool:
        """检查是否导入知识图谱成功"""
        try:
            self.wait_for_element_visible(self.import_success_message)
            self.logger.info("✓ 导入知识图谱成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 导入知识图谱失败: {e}")
            return False
