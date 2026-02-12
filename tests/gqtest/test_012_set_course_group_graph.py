# ========================================
# 设置专业课程群图谱
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖 test_010 创建的专业图谱概览
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.ai_major import MajorCourseGroupGraphPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("设置专业课程群图谱")
class TestSetCourseGroupGraph:
    """
    设置专业课程群图谱测试类
    """

    @pytest.mark.run(order=250)
    @allure.title("设置专业课程群图谱")
    def test_012_set_course_group_graph(self, page: Page, screenshot_helper, base_url):
        """
        设置专业课程群图谱：专业管理员登录 -> 专业AI模型 -> 专业课程群图谱 -> 关联图谱。
        """
        # 专业管理员用户信息
        cms_prof_info = DATA["user"]["prof_cms"]
        # 关联图谱名称
        graph_name = DATA["knowledge_graph"]["图谱名称"]

        helper = TestContextHelper()

        with allure.step("登录专业管理员"):
            helper.login_and_init(
                page, base_url, cms_prof_info["username"], cms_prof_info["password"],
                "智慧大学", "专业管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击专业AI模型"):
            helper.click_left_menu_item(page, "专业AI模型")

        with allure.step("点击专业课程群图谱"):
            graph_page = MajorCourseGroupGraphPage(page)
            graph_page.click_menu_item("专业课程群图谱")

        with allure.step("关联图谱"):
            graph_page.associate_graph(graph_name)
            assert graph_page.is_associate_graph_success(), "关联图谱失败"
            screenshot_helper.capture_full_page("专业课程群图谱设置完成")
