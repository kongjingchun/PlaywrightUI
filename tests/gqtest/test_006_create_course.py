# ========================================
# 创建课程
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from common.tools import build_path
from pages.gqkt.dean_manage import CourseManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建课程")
class TestCreateCourse:
    """
    创建课程测试类
    """

    @pytest.mark.run(order=190)
    @allure.title("创建课程")
    def test_create_course(self, page: Page, screenshot_helper, base_url):
        """
        创建课程
        """
        # CMS 教务管理员用户信息
        cms_dean_info = DATA["user"]["dean_cms"]
        # 课程信息
        course_info = DATA["course"]

        helper = TestContextHelper()

        with allure.step("登录教务管理员"):
            helper.login_and_init(
                page, base_url, cms_dean_info["username"], cms_dean_info["password"],
                "智慧大学", "教务管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击课程管理"):
            helper.click_left_menu_item(page, "课程管理")

        with allure.step("创建课程"):
            course_manage_page = CourseManagePage(page)
            image_path = str(build_path("file", "gqkt", "course_manage", course_info["课程封面"]))
            course_manage_page.create_course(
                course_code=course_info["课程代码"],
                course_name=course_info["课程名称"],
                image_path=image_path,
                dept_name=course_info["所属学院"],
                course_description=course_info["课程描述"],
                prof_name=course_info["课程负责人"],
                is_first_class_course=course_info["是否一流课程"]
            )
            assert course_manage_page.is_create_course_success(), "创建课程失败"
            screenshot_helper.capture_full_page("创建课程成功")
