# ========================================
# 成员管理页面（我教的班 - 成员管理）
# ========================================

from playwright.sync_api import Page

from .my_taught_class_page import MyTaughtClassPage


class MemberManagementPage(MyTaughtClassPage):
    """
    成员管理页面

    提供我教的班下成员管理相关操作方法，继承我教的班页面公共 iframe 与能力。
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ========== iframe ==========
        self.iframe = page.frame_locator("iframe#app-iframe-4009")
        # 添加学成按钮
        self.add_student_button = self.iframe.get_by_role("button", name="添加学生")
        # 添加学生搜索框
        self.add_student_search_input = self.iframe.get_by_role("textbox", name="请输入工号或姓名")
        # 确认添加弹窗内的确定按钮
        self.confirm_add_student_button = self.iframe.get_by_text("确定")
        # 添加成功提示框
        self.add_student_success_message = self.iframe.locator("xpath=//p[contains(text(),'添加成功')]")
    # ==================== 动态定位器生成方法 ====================
    # 根据学生名称返回学生对应添加按钮的定位器
    def get_add_student_button_by_name(self, student_name: str):
        """
        根据学生名称返回学生对应添加按钮的定位器

        :param student_name: 学生名称
        :return: 添加按钮的定位器
        """
        return self.iframe.get_by_role("row", name=student_name).get_by_text("添加", exact=True)
    # ==================== 业务方法 ====================
    def add_student(self, student_name: str):
        """
        添加学生

        :param student_name: 学生名称
        """
        self.click_element(self.add_student_button) # 点击添加学生按钮
        self.fill_element(self.add_student_search_input, student_name) # 输入学生名称
        self.click_element(self.get_add_student_button_by_name(student_name)) # 点击添加按钮
        self.click_element(self.confirm_add_student_button) # 点击确认添加按钮
    # ==================== 断言方法 ====================
    def is_add_student_success(self) -> bool:
        """
        断言是否添加学生成功

        :return: 是否添加学生成功
        """
        try:
            self.wait_for_element_visible(self.add_student_success_message)
            self.logger.info("✓ 添加学生成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ 添加学生失败: {e}")
            return False