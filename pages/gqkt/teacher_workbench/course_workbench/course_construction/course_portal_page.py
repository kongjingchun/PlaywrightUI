# ========================================
# 课程门户管理页面（课程建设）
# ========================================
# TODO: 待补充定位器与操作方法
# ========================================

from playwright.sync_api import Page

from pages.gqkt.teacher_workbench.course_workbench import CourseWorkbenchPage


class CoursePortalPage(CourseWorkbenchPage):
    """
    课程门户管理页面

    提供课程工作台下课程建设 - 课程门户管理相关操作方法。
    具体定位方法待后续补充。
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # iframe：课程工作台内容区域
        self.iframe = page.frame_locator("iframe#app-iframe-5004")
        # 编辑页面按钮
        self.edit_page_button = self.iframe.get_by_role("button", name="编辑页面")
        # 全部已使用的组件
        self.all_used_components = self.iframe.locator("div.canvas-widget")
        # 删除组件按钮
        self.delete_component_button = self.iframe.get_by_role(
            "button", name="删除组件")
        # 二次确定删除按钮
        self.confirm_delete_button = self.iframe.get_by_label(
            "删除确认").get_by_role("button", name="确定")
        # 发布按钮
        self.publish_button = self.iframe.get_by_role("button", name="发布")
        # 发布确认按钮
        self.publish_confirm_button = self.iframe.get_by_label("发布确认").get_by_role("button", name="确定")
        # ------- 拖拽 ----------
        # 画布第一个组件定位器（"拖拽组件到这里"）
        self.first_canvas_component = self.iframe.get_by_text("拖拽组件到这里")
        # 画布全部组件定位器（后面接 nth(0) 可以获取第一个组件）
        self.canvas_all_components = self.iframe.locator("xpath=//div[@class= 'canvas-widget']")
    # ==================== 动态定位器生成方法 ====================

    def get_component_by_name(self, component_name: str):
        """
        根据组件名称返回组件的定位器
        """
        return self.iframe.get_by_role("heading", name=component_name)
    # ==================== 操作方法 ====================

    def click_edit_page_button(self, timeout: int = 20000, force: bool = True):
        """
        点击编辑页面按钮。
        """
        self.click_element(self.edit_page_button, timeout=timeout, force=force)
    # ==================== 业务方法 ====================

    def delete_all_used_components(self):
        """
        循环删除所有已使用的组件：
        1. 获取已使用的组件数量
        2. 依次点击第一个组件，然后点击删除，再点击确认
        """
        count = self.all_used_components.count()
        for _ in range(count):
            if self.all_used_components.count() == 0:
                break
            # 点击第一个组件
            self.click_element(self.all_used_components.nth(0))
            # 点击删除组件按钮
            self.click_element(self.delete_component_button)
            # 点击二次确认删除按钮
            self.click_element(self.confirm_delete_button)

    # def add_first_component(self, component_name: str, timeout: int = 10000):
    #     """
    #     添加第一个组件到画布空白区域（“拖拽组件到这里”）。

    #     Args:
    #         component_name: 要添加的组件名称（在侧边栏/组件库中展示的标题文本）
    #         timeout: 拖拽操作的超时时间（毫秒）
    #     """
    #     self.drag_element_to(self.get_component_by_name(component_name), self.first_canvas_component, timeout=timeout)

    def add_component(
        self,
        component_name: str,
        component_index: int = 0,
        position: tuple = (0.5, 0.5),
        timeout: int = 10000,
    ):
        """
        向画布添加组件。
        Args:
            component_name: 要添加的组件名称（侧边栏/组件库中展示的标题文本，必传）
            component_index: 拖拽的目标画布上第几个组件（默认为第0个，即第一个组件）
            position: 拖拽到目标组件的位置 (x_ratio, y_ratio)，如(0.5, 0.5)，为None表示默认居中
            timeout: 拖拽操作的超时时间（毫秒）
        """
        # 取得侧栏待拖拽组件定位器
        source_component = self.get_component_by_name(component_name)

        # 获取当前画布已存在组件个数
        existing_count = self.canvas_all_components.count()

        # 画布为空，直接拖到first_canvas_component
        if existing_count == 0:
            self.drag_element_to(source_component, self.first_canvas_component, timeout=timeout)
        # 画布已有组件，拖到第component_index个组件的指定位置（默认中心）
        else:
            target = self.canvas_all_components.nth(component_index - 1)  # 第component_index个组件 从0开始
            target_position = self.get_position_in_element(target, x_ratio=position[0], y_ratio=position[1])  # 获取目标组件的相对位置
            self.drag_element_to(source_component, target, timeout=timeout, target_position=target_position)  # 拖拽到目标组件的相对位置

    def confirm_publish(self):
        """
        点击并确认发布操作的方法。
        """
        # 假设有发布按钮和确认发布按钮的定位器
        self.click_element(self.publish_button)
        self.click_element(self.publish_confirm_button)
