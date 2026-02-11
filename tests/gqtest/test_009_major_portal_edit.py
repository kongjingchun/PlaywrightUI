# ========================================
# 专业门户编辑
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.ai_major import MajorPortalManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("专业门户编辑")
class TestMajorPortalEdit:
    """
    专业门户编辑测试类
    """

    @pytest.mark.run(order=220)
    @allure.title("专业门户编辑")
    def test_009_major_portal_edit(self, page: Page, screenshot_helper, base_url):
        """
        专业门户编辑：进入专业门户管理，选择专业进入编辑页，修改标题并发布。
        """
        # 专业管理员用户信息
        cms_prof_info = DATA["user"]["prof_cms"]
        # 专业名称（用于在列表中定位要编辑的专业）
        major_name = DATA["major"]["专业名称"]

        helper = TestContextHelper()

        with allure.step("登录专业管理员"):
            helper.login_and_init(
                page, base_url, cms_prof_info["username"], cms_prof_info["password"],
                "智慧大学", "专业管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击专业门户管理"):
            helper.click_left_menu_item(page, "专业门户管理")

        with allure.step("进入专业门户编辑"):
            portal_page = MajorPortalManagePage(page)
            portal_page.click_edit_page_button(major_name)
            screenshot_helper.capture_full_page("进入专业门户编辑页")

        with allure.step("编辑页面并发布"):
            portal_page.edit_page(major_name)
            assert portal_page.is_publish_success(), "发布专业门户失败"
            screenshot_helper.capture_full_page("专业门户编辑完成")
