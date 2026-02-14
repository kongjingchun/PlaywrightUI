# ========================================
# 创建教学班
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖课程创建流程
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_teaching import TeachingClassManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建教学班")
class TestCreateTeachingClass:
    """
    创建教学班测试类
    """

    @pytest.mark.run(order=330)
    @allure.title("创建教学班并设置主讲教师")
    def test_create_teaching_class(self, page: Page, screenshot_helper, base_url):
        """
        创建教学班并给教学班设置主讲教师
        """
        teacher_cms = DATA["user"]["prof_cms"]
        course_name = DATA["course"]["课程名称"]
        tc_config = DATA["teaching_class"]

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

        with allure.step("进入教学班管理"):
            workbench_page = TeachingClassManagePage(page)
            workbench_page.click_left_menu_by_name("教学班管理")

        with allure.step("创建教学班"):
            workbench_page.create_teaching_class(
                teaching_class_name=tc_config["教学班名称"],
                teaching_class_id=tc_config["教学班编号"],
                teaching_class_start_time=tc_config["开课时间"],
                teaching_class_end_time=tc_config.get("结课时间", ""),
                teaching_class_class_size=tc_config.get("班级人数", 100),
                allow_student_self_selection=tc_config.get("是否允许学生自选", False),
                allow_student_self_withdraw=tc_config.get("是否允许学生自主退课", False),
                use_class_size_unlimited=tc_config.get("班级人数无限制", False)
            )
            assert workbench_page.is_create_teaching_class_success(tc_config["教学班名称"]), "创建教学班失败"
            screenshot_helper.capture_full_page("教学班创建完成")

        with allure.step("给教学班设置主讲教师"):
            workbench_page.set_main_teacher_for_class(
                teaching_class_name=tc_config["教学班名称"],
                teacher_name=tc_config["主讲教师"]
            )
            assert workbench_page.is_set_main_teacher_success(), "设置主讲教师失败"
            screenshot_helper.capture_full_page("主讲教师设置完成")
