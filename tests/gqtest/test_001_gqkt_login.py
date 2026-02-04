# ========================================
# 光穹课堂登录测试
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

from _pytest.stash import T
import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.dean_manage import UserManagePage
from tests.gqtest import TestContextHelper
from utils.auth_helper import AuthHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("初始化用户数据")
class TestGqktInitUser:
    """
    光穹课堂初始化用户数据测试类
    """

    @pytest.mark.run(order=100)
    @allure.title("创建用户")
    def test_001_create_user(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        登陆用户
        """
        # 教务管理员用户信息
        dean_user_info = DATA["user"]["dean"]

        # 专业负责人用户信息
        prof_user_info = DATA["user"]["prof"]

        # 定义用户标识（用于免登录）
        auth_key = "超级管理员"

        helper = TestContextHelper()
        auth = AuthHelper()

        # ========== 手动控制免登录 ==========
        with allure.step("登录用户"):
            helper.login_and_init(
                page, base_url, initial_admin,
                "智慧大学", "机构管理员",
                use_saved_auth=False,  # 不自动尝试免登录（我们手动控制）
                save_auth=True        # 自动保存（我们手动保存）
            )

        with allure.step("点击用户管理"):
            helper.get_left_menu(page, "用户管理")

        # with allure.step("创建教务管理员"):
        #     user_manage_page = UserManagePage(page)
        #     result = user_manage_page.create_user("创建教务管理员", dean_user_info["姓名"], dean_user_info["工号"])
        #     screenshot_helper.capture_full_page("创建教务管理员成功")
        #     assert result, "创建教务管理员失败"

        # with allure.step("创建专业负责人"):
        #     user_manage_page = UserManagePage(page)
        #     result = user_manage_page.create_user("创建专业负责人", prof_user_info["姓名"], prof_user_info["工号"])
        #     screenshot_helper.capture_full_page("创建专业负责人成功")
        #     assert result, "创建专业负责人失败"

    @pytest.mark.run(order=101)
    @allure.title("绑定用户")
    def test_002_bind_user(self, page: Page, screenshot_helper, base_url, initial_admin):
        """
        登陆用户
        """

        helper = TestContextHelper()
        auth = AuthHelper()

        with allure.step("登录用户"):
            helper.login_and_init(
                page, base_url + "/console", initial_admin,
                "智慧大学", "机构管理员",
                use_saved_auth=True,  # 自动尝试免登录（我们手动控制）
                save_auth=True        # 自动保存（我们手动保存）
            )

        page.pause()
