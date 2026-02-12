# ========================================
# 设置初始用户
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages import GqktLoginPage
from pages.gqkt import CmsApiPage
from pages.gqkt.dean_manage import UserManagePage
from pages.gqkt.dean_manage import RoleManagePage
from tests.gqtest import TestContextHelper
from utils.auth_helper import AuthHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("初始化用户数据")
class TestSetInitialUser:
    """
    设置初始用户测试类
    """

    @pytest.mark.run(order=100)
    @allure.title("创建用户")
    def test_create_user(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        创建用户
        """
        # 教务管理员用户信息
        dean_user_info = DATA["user"]["dean"]

        # 专业负责人用户信息
        prof_user_info = DATA["user"]["prof"]

        # 定义用户标识（用于免登录）
        auth_key = "超级管理员"

        helper = TestContextHelper()

        # ========== 手动控制免登录 ==========
        with allure.step("登录用户"):
            helper.login_and_init(
                page, base_url, initial_admin["username"], initial_admin["password"],
                "智慧大学", "机构管理员",
                use_saved_auth=False,  # 不自动尝试免登录（我们手动控制）
                save_auth=True        # 自动保存（我们手动保存）
            )

        with allure.step("点击用户管理"):
            helper.click_left_menu_item(page, "用户管理")

        with allure.step("创建教务管理员"):
            user_manage_page = UserManagePage(page)
            user_manage_page.create_user("创建教务管理员", dean_user_info["姓名"], dean_user_info["工号"])
            assert user_manage_page.is_create_user_success(), "创建教务管理员失败"
            screenshot_helper.capture_full_page("创建教务管理员成功")

        with allure.step("创建专业负责人"):
            user_manage_page = UserManagePage(page)
            user_manage_page.create_user("创建专业负责人", prof_user_info["姓名"], prof_user_info["工号"])
            assert user_manage_page.is_create_user_success(), "创建专业负责人失败"
            screenshot_helper.capture_full_page("创建专业负责人成功")

    @pytest.mark.run(order=120)
    @pytest.mark.skip_local
    @allure.title("注册CMS账户并绑定用户")
    def test_bind_user(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        注册CMS账户并绑定用户
        """
        # cms 教务管理员用户信息
        dean_cms_info = DATA["user"]["dean_cms"]
        # cms 专业负责人用户信息
        prof_cms_info = DATA["user"]["prof_cms"]
        # 教务管理员用户信息
        dean_info = DATA["user"]["dean"]
        # 专业负责人用户信息
        prof_info = DATA["user"]["prof"]
        # 测试上下文助手
        helper = TestContextHelper()

        with allure.step("调用 API 注册教务管理员"):
            cms_api = CmsApiPage(base_url)
            dean_cms_id = cms_api.register_cms_user(dean_cms_info)
            print("user_id: " + str(dean_cms_id))
            assert dean_cms_id is not None, f"用户 {dean_cms_info['username']} 注册失败"

        with allure.step("调用 API 注册专业负责人"):
            cms_api = CmsApiPage(base_url)
            prof_cms_id = cms_api.register_cms_user(prof_cms_info)
            print("user_id: " + str(prof_cms_id))
            assert prof_cms_id is not None, f"用户 {prof_cms_info['username']} 注册失败"

        with allure.step("登录用户"):
            helper.login_and_init(
                page, base_url, initial_admin["username"], initial_admin["password"],
                "智慧大学", "机构管理员",
                use_saved_auth=True,  # 自动尝试免登录（我们手动控制）
                save_auth=True        # 自动保存（我们手动保存）
            )
            helper.click_left_menu_item(page, "用户管理")

        with allure.step("绑定教务管理员"):
            user_manage_page = UserManagePage(page)
            user_manage_page.bind_user(dean_info["工号"], dean_cms_id)
            assert user_manage_page.is_bind_user_success(), "绑定教务管理员失败"
            screenshot_helper.capture_full_page("绑定教务管理员成功")

        with allure.step("绑定专业负责人"):
            user_manage_page = UserManagePage(page)
            user_manage_page.bind_user(prof_info["工号"], prof_cms_id)
            assert user_manage_page.is_bind_user_success(), "绑定专业负责人失败"
            screenshot_helper.capture_full_page("绑定专业负责人成功")

    @pytest.mark.run(order=130)
    @pytest.mark.skip_prod
    @allure.title("重置密码")
    def test_reset_password(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        重置密码
        """
        # 教务管理员用户信息
        dean_info = DATA["user"]["dean"]
        # CMS 教务管理员用户信息
        dean_cms_info = DATA["user"]["dean_cms"]
        # 专业负责人用户信息
        prof_info = DATA["user"]["prof"]
        # CMS 专业负责人用户信息
        prof_cms_info = DATA["user"]["prof_cms"]

        with allure.step("重置教务管理员密码"):
            login_page = GqktLoginPage(page, base_url)
            login_page.goto()
            login_page.login(dean_info["工号"], dean_info["工号"][-6:])
            login_page.reset_password(dean_cms_info["username"], dean_cms_info["password"])
            assert login_page.is_reset_password_success(), "重置教务管理员密码失败"
            screenshot_helper.capture_full_page("重置教务管理员密码成功")

        with allure.step("重置专业负责人密码"):
            login_page = GqktLoginPage(page, base_url)
            login_page.goto()
            login_page.login(prof_info["工号"], prof_info["工号"][-6:])
            login_page.reset_password(prof_cms_info["username"], prof_cms_info["password"])
            assert login_page.is_reset_password_success(), "重置专业负责人密码失败"
            screenshot_helper.capture_full_page("重置专业负责人密码成功")

    @pytest.mark.run(order=140)
    @allure.title("分配角色")
    def test_assign_role(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        分配角色
        """
        # 教务管理员用户信息
        cms_dean_info = DATA["user"]["dean_cms"]
        # 专业负责人用户信息
        cms_prof_info = DATA["user"]["prof_cms"]
        # 教务管理员用户信息
        dean_info = DATA["user"]["dean"]
        # 专业负责人用户信息
        prof_info = DATA["user"]["prof"]
        # 测试上下文助手
        helper = TestContextHelper()
        # 登录CMS教务管理员
        with allure.step("登录用户"):
            helper.login_and_init(
                page, base_url, cms_dean_info["username"], cms_dean_info["password"],
                "智慧大学", "教务管理员",
                use_saved_auth=False,  # 不自动尝试免登录（我们手动控制）
                save_auth=True        # 自动保存（我们手动保存）
            )
        with allure.step("点击角色管理"):
            helper.click_left_menu_item(page, "角色管理")
        with allure.step("分配教务管理员角色"):
            role_manage_page = RoleManagePage(page)
            role_manage_page.assign_role_to_user("教师", prof_info["姓名"])
            assert role_manage_page.is_assign_role_success(), "分配教务管理员角色失败"
            screenshot_helper.capture_full_page("分配教务管理员角色成功")
