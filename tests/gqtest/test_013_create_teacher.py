# ========================================
# 创建教师
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖 test_001 中的机构管理员权限
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
@allure.story("创建教师")
class TestCreateTeacher:
    """
    创建教师测试类
    """

    @pytest.mark.run(order=260)
    @allure.title("创建教师")
    def test_create_teacher(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        创建教师：
        """
        # 教师用户信息
        teacher_info = DATA["user"]["teacher"]

        helper = TestContextHelper()

        with allure.step("登录机构管理员"):
            helper.login_and_init(
                page, base_url, initial_admin["username"], initial_admin["password"],
                "智慧大学", "机构管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击用户管理"):
            helper.click_left_menu_item(page, "用户管理")

        with allure.step("创建教师"):
            user_manage_page = UserManagePage(page)
            user_manage_page.create_user(role_name="创建教师", name=teacher_info["姓名"], code=teacher_info["工号"], dept_name=teacher_info["学院"])
            assert user_manage_page.is_create_user_success(), "创建教师失败"
            screenshot_helper.capture_full_page("创建教师成功")

    @pytest.mark.run(order=270)
    @pytest.mark.skip_local
    @allure.title("注册CMS账户并绑定教师")
    def test_bind_teacher(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        注册CMS账户并绑定教师
        """
        # CMS 教师用户信息
        teacher_cms_info = DATA["user"]["teacher_cms"]
        # 教师用户信息
        teacher_info = DATA["user"]["teacher"]
        helper = TestContextHelper()

        with allure.step("调用 API 注册教师"):
            cms_api = CmsApiPage(base_url)
            teacher_cms_id = cms_api.register_cms_user(teacher_cms_info)
            print("user_id: " + str(teacher_cms_id))
            assert teacher_cms_id is not None, f"用户 {teacher_cms_info['username']} 注册失败"

        with allure.step("登录用户"):
            helper.login_and_init(
                page, base_url, initial_admin["username"], initial_admin["password"],
                "智慧大学", "机构管理员",
                use_saved_auth=True,
                save_auth=True
            )
            helper.click_left_menu_item(page, "用户管理")

        with allure.step("绑定教师"):
            user_manage_page = UserManagePage(page)
            user_manage_page.bind_user(teacher_info["工号"], teacher_cms_id)
            assert user_manage_page.is_bind_user_success(), "绑定教师失败"
            screenshot_helper.capture_full_page("绑定教师成功")

    @pytest.mark.run(order=280)
    @pytest.mark.skip_prod
    @allure.title("重置教师密码")
    def test_reset_teacher_password(self, page: Page, screenshot_helper, base_url):
        """
        重置教师密码
        """
        # 教师用户信息
        teacher_info = DATA["user"]["teacher"]
        # CMS 教师用户信息
        teacher_cms_info = DATA["user"]["teacher_cms"]

        with allure.step("重置教师密码"):
            login_page = GqktLoginPage(page, base_url)
            login_page.goto()
            login_page.login(teacher_info["工号"], teacher_info["工号"][-6:])
            login_page.reset_password(teacher_cms_info["username"], teacher_cms_info["password"])
            assert login_page.is_reset_password_success(), "重置教师密码失败"
            screenshot_helper.capture_full_page("重置教师密码成功")
