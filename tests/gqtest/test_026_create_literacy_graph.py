# ========================================
# 创建素质图谱
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import LiteracyGraphPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建素质图谱")
class TestCreateLiteracyGraph:
    """
    创建素质图谱测试类
    """

    @pytest.mark.run(order=390)
    @allure.title("创建素质图谱并添加一级素质及子素质")
    def test_create_literacy_graph(self, page: Page, screenshot_helper, base_url):
        """
        创建素质图谱，添加一级素质节点，再递归添加二级、三级素质
        """
        teacher_cms = DATA["user"]["teacher_cms"]
        course_name = DATA["course"]["课程名称"]

        helper = TestContextHelper()
        literacy_graph = DATA["literacy_graph"]

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, teacher_cms["username"], teacher_cms["password"],
                DATA["school_name"], "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入素质图谱"):
            literacy_graph_page = LiteracyGraphPage(page)
            literacy_graph_page.click_left_menu_by_name("AI垂直模型")
            literacy_graph_page.click_left_menu_by_name("素质图谱")

        with allure.step("创建素质图谱"):
            literacy_graph_page.click_create_graph_button()
            assert literacy_graph_page.is_create_graph_success(), "创建素质图谱失败"
            screenshot_helper.capture_full_page("创建素质图谱完成")

        lg = literacy_graph
        level1 = lg.get("一级能力", [])
        level2 = lg.get("二级能力", [])
        level3 = lg.get("三级能力", [])

        with allure.step("添加一级素质"):
            for cap in level1:
                name = cap["能力名称"]
                desc = cap.get("描述", "")
                tags = cap.get("标签")
                knowledge = cap.get("关联知识点")
                literacy_graph_page.add_main_ability(name, desc, tags, knowledge)
                assert literacy_graph_page.is_add_sub_ability_success(), f"添加一级素质失败: {name}"

        with allure.step("添加二级素质"):
            for cap in level2:
                parent = cap["父级"]
                name = cap["能力名称"]
                desc = cap.get("描述", "")
                tags = cap.get("标签")
                knowledge = cap.get("关联知识点")
                literacy_graph_page.add_sub_ability(parent, name, desc, tags, knowledge)
                assert literacy_graph_page.is_add_sub_ability_success(), f"添加二级素质失败: {name}"

        with allure.step("添加三级素质"):
            for cap in level3:
                parent = cap["父级"]
                name = cap["能力名称"]
                desc = cap.get("描述", "")
                tags = cap.get("标签")
                knowledge = cap.get("关联知识点")
                literacy_graph_page.add_sub_ability(parent, name, desc, tags, knowledge)
                assert literacy_graph_page.is_add_sub_ability_success(), f"添加三级素质失败: {name}"

            screenshot_helper.capture_full_page("添加素质完成")
