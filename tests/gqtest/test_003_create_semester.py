# ========================================
# 创建学期
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.dean_manage import SemesterManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建学期")
class TestCreateSemester:
    """
    创建学期测试类
    """

    @pytest.mark.run(order=160)
    @allure.title("创建学期")
    def test_003_create_semester(self, page: Page, screenshot_helper, base_url):
        """
        创建学期
        """
        # CMS 教务管理员用户信息
        cms_dean_info = DATA["user"]["dean_cms"]
        # 学期信息
        semester_info = DATA["semester"]

        helper = TestContextHelper()

        with allure.step("登录教务管理员"):
            helper.login_and_init(
                page, base_url, cms_dean_info["username"], cms_dean_info["password"],
                "智慧大学", "教务管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击学期管理"):
            helper.click_left_menu_item(page, "学期管理")

        with allure.step("创建学期"):
            semester_manage_page = SemesterManagePage(page)
            semester_manage_page.create_semester("2035")
            assert semester_manage_page.is_create_semester_success(), "创建学期失败"
            screenshot_helper.capture_full_page("创建学期成功")
            page.pause()
