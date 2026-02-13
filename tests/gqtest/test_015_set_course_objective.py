# ========================================
# 设置课程目标
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖课程创建流程（我教的课中有课程）
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import CourseObjectivePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("设置课程目标")
class TestSetCourseObjective:
    """
    设置课程目标测试类
    """

    @pytest.mark.run(order=290)
    @allure.title("设置课程目标")
    def test_set_course_objective(self, page: Page, screenshot_helper, base_url):
        """
        设置课程目标：
        """
        # 教师用户信息（与 test_011 一致，使用有课程权限的教师/专业负责人）
        teacher_cms = DATA["user"]["prof_cms"]
        # 课程名称（用于在我教的课中进入该课程）
        course_name = DATA["course"]["课程名称"]
        # 课程目标配置
        course_objective = DATA["course_outline"]["课程目标"]

        helper = TestContextHelper()

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, teacher_cms["username"], teacher_cms["password"],
                "智慧大学", "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入课程目标"):
            objective_page = CourseObjectivePage(page)
            objective_page.click_left_menu_by_name("课程大纲")
            objective_page.click_left_menu_by_name("课程目标")

        with allure.step("编辑课程目标描述"):
            objective_page.edit_description(course_objective["描述"])
            assert objective_page.is_edit_description_success(), "编辑课程目标描述失败"
            screenshot_helper.capture_full_page("课程目标描述设置完成")

        with allure.step("添加课程目标"):
            for goal in course_objective["目标列表"]:
                objective_page.create_goal(
                    goal["标题"],
                    [goal["标签"]] if isinstance(goal["标签"], str) else goal["标签"]
                )
                assert objective_page.is_create_goal_success(), f"添加课程目标失败: {goal['标题']}"
            screenshot_helper.capture_full_page("课程目标设置完成")

        with allure.step("关联课程目标与指标"):
            # 使用培养方案中的分解指标点名称
            indicator_name = DATA["training_program"]["指标点"]["指标点1"]["分解指标点名称"]
            objective_page.associate_goal_with_indicator(goal["标题"], indicator_name)
            assert objective_page.is_associate_goal_with_indicator_success(), f"关联课程目标与指标失败: {goal['标题']}"
            screenshot_helper.capture_full_page("课程目标与指标关联完成")
