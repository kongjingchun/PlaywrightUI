# ========================================
# 创建行政班
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.dean_manage import AdminClassManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建行政班")
class TestCreateAdminClass:
    """
    创建行政班测试类
    """

    @pytest.mark.run(order=180)
    @allure.title("创建行政班")
    def test_005_create_admin_class(self, page: Page, screenshot_helper, base_url):
        """
        创建行政班
        """
        # CMS 教务管理员用户信息
        cms_dean_info = DATA["user"]["dean_cms"]
        # 行政班信息
        admin_class_info = DATA["admin_class"]

        helper = TestContextHelper()

        with allure.step("登录教务管理员"):
            helper.login_and_init(
                page, base_url, cms_dean_info["username"], cms_dean_info["password"],
                "智慧大学", "教务管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击行政班管理"):
            helper.click_left_menu_item(page, "行政班管理")

        with allure.step("创建行政班"):
            admin_class_manage_page = AdminClassManagePage(page)
            admin_class_manage_page.create_admin_class(
                admin_class_name=admin_class_info["行政班名称"],
                admin_class_id=admin_class_info["行政班编号"],
                admin_class_dept=admin_class_info["学院"],
                admin_class_major=admin_class_info["专业"],
                admin_class_grade=admin_class_info["年级"],
                admin_class_description=admin_class_info["描述"]
            )
            assert admin_class_manage_page.is_create_admin_class_success(), "创建行政班失败"
            screenshot_helper.capture_full_page("创建行政班成功")
