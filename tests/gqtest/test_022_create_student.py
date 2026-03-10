# ========================================
# 创建学生
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖 test_001 机构管理员、test_005 创建行政班
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages import GqktLoginPage
from pages.gqkt import CmsApiPage
from pages.gqkt.dean_manage import UserManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建学生")
class TestCreateStudent:
    """
    创建学生测试类
    """

    @pytest.mark.run(order=265)
    @allure.title("创建学生")
    def test_create_student(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        创建学生
        """
        # 学生用户信息
        student_info = DATA["user"]["student"]

        helper = TestContextHelper()

        with allure.step("登录机构管理员"):
            helper.login_and_init(
                page, base_url, initial_admin["username"], initial_admin["password"],
                DATA["school_name"], "机构管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击用户管理"):
            helper.click_left_menu_item(page, "用户管理")

        with allure.step("创建学生"):
            admin_class_info = DATA["admin_class"]
            user_manage_page = UserManagePage(page)
            user_manage_page.create_user(
                role_name="创建学生",
                name=student_info["姓名"],
                code=student_info["学号"],
                dept_name=student_info["学院"],
                major_name=student_info["专业"],
                grade_name=student_info["年级"],
                admin_class_name=admin_class_info["行政班名称"]
            )
            assert user_manage_page.is_create_user_success(), "创建学生失败"
            screenshot_helper.capture_full_page("创建学生成功")

    # TODO: 可能注册失败
    @pytest.mark.run(order=275)
    @pytest.mark.skip_local
    @allure.title("注册CMS账户并绑定学生")
    def test_bind_student(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        注册CMS账户并绑定学生
        """
        # CMS 学生用户信息
        student_cms_info = DATA["user"]["student_cms"]
        # 学生用户信息
        student_info = DATA["user"]["student"]
        helper = TestContextHelper()

        with allure.step("调用 API 注册学生"):
            cms_api = CmsApiPage(base_url)
            student_cms_id = cms_api.register_cms_user(student_cms_info)
            print("user_id: " + str(student_cms_id))
            assert student_cms_id is not None, f"用户 {student_cms_info['username']} 注册失败"

        with allure.step("登录用户"):
            helper.login_and_init(
                page, base_url, initial_admin["username"], initial_admin["password"],
                DATA["school_name"], "机构管理员",
                use_saved_auth=True,
                save_auth=True
            )
            helper.click_left_menu_item(page, "用户管理")

        with allure.step("绑定学生"):
            user_manage_page = UserManagePage(page)
            user_manage_page.bind_user(student_info["学号"], student_cms_id)
            assert user_manage_page.is_bind_user_success(), "绑定学生失败"
            screenshot_helper.capture_full_page("绑定学生成功")

    @pytest.mark.run(order=285)
    @pytest.mark.skip_prod
    @allure.title("重置学生密码")
    def test_reset_student_password(self, page: Page, screenshot_helper, base_url):
        """
        重置学生密码
        """
        # 学生用户信息
        student_info = DATA["user"]["student"]
        # CMS 学生用户信息
        student_cms_info = DATA["user"]["student_cms"]

        with allure.step("重置学生密码"):
            login_page = GqktLoginPage(page, base_url)
            login_page.goto()
            login_page.login(student_info["学号"], student_info["学号"][-6:])
            login_page.reset_password(student_cms_info["username"], student_cms_info["password"])
            assert login_page.is_reset_password_success(), "重置学生密码失败"
            screenshot_helper.capture_full_page("重置学生密码成功")
