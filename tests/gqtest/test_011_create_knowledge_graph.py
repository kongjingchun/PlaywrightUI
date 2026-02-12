# ========================================
# 新建知识图谱
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import KnowledgeGraphPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("新建知识图谱")
class TestCreateKnowledgeGraph:
    """
    新建知识图谱测试类
    """

    @pytest.mark.run(order=240)
    @allure.title("新建知识图谱")
    def test_create_knowledge_graph(self, page: Page, screenshot_helper, base_url):
        """
        新建知识图谱：教师登录 -> 我教的课 -> 进入课程 -> 课程工作台知识图谱 -> 新建主图谱。
        """
        # 教师用户信息
        prof_cms = DATA["user"]["prof_cms"]
        # 课程名称（用于在我教的课中进入该课程）
        course_name = DATA["course"]["课程名称"]
        # 知识图谱名称、描述
        kg = DATA["knowledge_graph"]

        helper = TestContextHelper()

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, prof_cms["username"], prof_cms["password"],
                "智慧大学", "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入知识图谱"):
            kg_page = KnowledgeGraphPage(page)
            kg_page.click_left_menu_by_name("AI垂直模型")
            kg_page.click_left_menu_by_name("知识图谱")

        with allure.step("新建知识图谱"):
            kg_page.create_knowledge_graph(kg["图谱名称"], kg["图谱描述"])
            assert kg_page.is_create_knowledge_graph_success(), "新建知识图谱失败"
            screenshot_helper.capture_full_page("新建知识图谱完成")

        with allure.step("点击编辑数据按钮"):
            kg_page.click_edit_data_button()
            screenshot_helper.capture_full_page("进入编辑数据页")

        with allure.step("添加节点"):
            for node in kg["节点列表"]:
                kg_page.add_data(node["标题"], node["描述"])
                kg_page.wait_for_element_visible(kg_page.create_success_message)
            screenshot_helper.capture_full_page("添加节点完成")

        with allure.step("在两个节点下分别添加两个子节点"):
            for node in kg["节点列表"]:
                for sub in node["子节点"]:
                    kg_page.add_sub_node(node["标题"], sub["标题"], sub["描述"])
                    kg_page.wait_for_element_visible(kg_page.create_success_message)
            screenshot_helper.capture_full_page("添加子节点完成")
