# ========================================
# 创建部门
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.department_manage import DeptListManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建部门")
class TestCreateDept:
    """
    创建部门测试类
    """

    @pytest.mark.run(order=150)
    @allure.title("创建院系")
    def test_001_create_dept(self, page: Page, screenshot_helper, base_url):
        """
        创建部门
        """
        # CMS 教务管理员用户信息
        cms_dean_info = DATA["user"]["dean_cms"]
        # 部门信息
        dept_info = DATA["department"]

        helper = TestContextHelper()

        with allure.step("登录教务管理员"):
            helper.login_and_init(
                page, base_url, cms_dean_info["username"], cms_dean_info["password"],
                "智慧大学", "教务管理员",
                use_saved_auth=True,
                save_auth=True
            )
        with allure.step("点击院系列表管理"):
            helper.click_left_menu_item(page, "院系列表管理")

        with allure.step("创建院系"):
            dept_list_manage_page = DeptListManagePage(page)
            dept_list_manage_page.create_dept(dept_info["院系名称"], dept_info["院系代码"])
            assert dept_list_manage_page.is_create_dept_success(), "创建院系失败"
            screenshot_helper.capture_full_page("创建院系成功")
