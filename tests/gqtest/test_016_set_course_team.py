# ========================================
# 设置课程团队
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖课程创建流程、test_013 创建教师
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import CourseTeamPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("设置课程团队")
class TestSetCourseTeam:
    """
    设置课程团队测试类
    """

    @pytest.mark.run(order=300)
    @allure.title("设置课程团队")
    def test_set_course_team(self, page: Page, screenshot_helper, base_url):
        """
        设置课程团队：
        1. 添加教师为课程负责人
        2. 删除教师从课程负责人
        3. 添加教师到课程教师
        4. 删除教师从课程教师
        """
        # 教师用户信息（有课程权限的专业负责人）
        teacher_cms = DATA["user"]["prof_cms"]
        # 课程名称（用于在我教的课中进入该课程）
        course_name = DATA["course"]["课程名称"]
        # 课程团队 - 要操作的教师（test_013 创建的教师）
        team_teacher_name = DATA["course_outline"]["课程团队"]["教师姓名"]

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

        with allure.step("进入课程团队"):
            team_page = CourseTeamPage(page)
            team_page.click_left_menu_by_name("课程大纲")
            team_page.click_left_menu_by_name("课程团队")

        with allure.step("添加教师为课程负责人"):
            team_page.add_course_leader(team_teacher_name)
            assert team_page.is_add_success(), "添加课程负责人失败"
            screenshot_helper.capture_full_page("添加课程负责人完成")

        with allure.step("删除教师从课程负责人"):
            team_page.delete_course_leader(team_teacher_name)
            assert team_page.is_delete_success(), "删除课程负责人失败"
            screenshot_helper.capture_full_page("删除课程负责人完成")

        with allure.step("添加教师到课程教师"):
            team_page.add_course_teacher(team_teacher_name)
            assert team_page.is_add_success(), "添加课程教师失败"
            screenshot_helper.capture_full_page("添加课程教师完成")

        with allure.step("删除教师从课程教师"):
            team_page.delete_course_teacher(team_teacher_name)
            assert team_page.is_delete_success(), "删除课程教师失败"
            screenshot_helper.capture_full_page("课程团队设置完成")
