# ========================================
# 创建问题图谱
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import ProblemGraphPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建问题图谱")
class TestCreateProblemGraph:
    """
    创建问题图谱测试类
    """

    @pytest.mark.run(order=400)
    @allure.title("创建问题图谱并添加层级与问题")
    def test_create_problem_graph(self, page: Page, screenshot_helper, base_url):
        """
        创建问题图谱，按配置添加层级（高级思维、中级思维、初级思维），
        在各层级下添加问题（标题、答案、标签、关联知识点、关联问题）。
        """
        prof_cms = DATA["user"]["prof_cms"]
        course_name = DATA["course"]["课程名称"]

        helper = TestContextHelper()
        problem_graph_config = DATA["problem_graph"]

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, prof_cms["username"], prof_cms["password"],
                DATA["school_name"], "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入问题图谱"):
            problem_graph_page = ProblemGraphPage(page)
            problem_graph_page.click_left_menu_by_name("AI垂直模型")
            problem_graph_page.click_left_menu_by_name("问题图谱")

        with allure.step("创建问题图谱"):
            problem_graph_page.click_create_problem_graph_button()
            assert problem_graph_page.is_create_graph_success(), "创建问题图谱失败"
            screenshot_helper.capture_full_page("创建问题图谱完成")

        for level_block in problem_graph_config:
            level_title = level_block["层级"]
            problems = level_block.get("问题", [])

            with allure.step(f"添加层级: {level_title}"):
                problem_graph_page.create_problem_graph_level(level_title, "")

            with allure.step(f"在层级【{level_title}】下添加问题"):
                for prob in problems:
                    title = prob["标题"]
                    answer = prob.get("答案", "")
                    tags = prob.get("标签")
                    knowledge = prob.get("关联知识点")
                    related = prob.get("关联问题")
                    problem_graph_page.add_problem_to_level(
                        level_title,
                        problem_title=title,
                        answer=answer or None,
                        tags=tags,
                        related_problems=related,
                        knowledge_points=knowledge,
                    )

        screenshot_helper.capture_full_page("问题图谱添加完成")
