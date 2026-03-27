# ========================================
# 课程门户管理
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import CoursePortalPage
from tests.gqtest import TestContextHelper

@allure.feature("光穹课堂")
@allure.story("课程门户管理")
class TestCoursePortalManage:
    """
    课程门户管理测试类
    """

    @pytest.mark.run(order=410)
    @allure.title("进入课程门户管理并编辑页面")
    def test_course_portal_manage(self, page: Page, screenshot_helper, base_url, gqkt_data: dict):
        """
        登录教师账号，进入课程工作台，进入课程门户管理页面并执行编辑页面操作。
        """
        teacher_cms = gqkt_data["user"]["teacher_cms"]
        course_name = gqkt_data["course"]["课程名称"]

        helper = TestContextHelper()

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, teacher_cms["username"], teacher_cms["password"],
                gqkt_data["school_name"], "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入课程门户管理"):
            portal_page = CoursePortalPage(page)
            portal_page.click_course_portal_edit_button()
        with allure.step("点击编辑页面"):
            portal_page.click_edit_page_button()
        with allure.step("删除所有已使用的组件"):
            portal_page.delete_all_used_components()
        with allure.step("添加第一个组件"):
            portal_page.add_component("课程门户Header")
        with allure.step("添加课程门户首页"):
            portal_page.add_component(component_name="课程门户首页", component_index=1, position=(0.8, 0.8))
        with allure.step("确认发布"):
            portal_page.confirm_publish()
            screenshot_helper.capture_full_page("发布课程门户")
