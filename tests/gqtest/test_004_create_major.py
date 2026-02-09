# ========================================
# 创建专业
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.ai_major import MajorManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建专业")
class TestCreateMajor:
    """
    创建专业测试类
    """

    @pytest.mark.run(order=170)
    @allure.title("创建专业")
    def test_004_create_major(self, page: Page, screenshot_helper, base_url):
        """
        创建专业
        """
        # CMS 教务管理员用户信息
        cms_dean_info = DATA["user"]["dean_cms"]
        # 专业信息
        major_info = DATA["major"]

        helper = TestContextHelper()

        with allure.step("登录教务管理员"):
            helper.login_and_init(
                page, base_url, cms_dean_info["username"], cms_dean_info["password"],
                "智慧大学", "教务管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击专业管理"):
            helper.click_left_menu_item(page, "专业管理")

        with allure.step("创建专业"):
            major_manage_page = MajorManagePage(page)
            major_manage_page.create_major(
                major_name=major_info["专业名称"],
                major_code_school=major_info["学校专业代码"],
                major_code_national=major_info["国家专业代码"],
                major_dept=major_info["所属院系"],
                major_prof=major_info["专业负责人"],
                major_level=major_info["专业建设层次"],
                major_feature=major_info["专业特色标签"]
            )
            assert major_manage_page.is_create_major_success(), "创建专业失败"
            screenshot_helper.capture_full_page("创建专业成功")
