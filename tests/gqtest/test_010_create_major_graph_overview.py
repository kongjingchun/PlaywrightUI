# ========================================
# 创建专业图谱概览
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.ai_major import MajorGraphOverviewPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建专业图谱概览")
class TestCreateMajorGraphOverview:
    """
    创建专业图谱概览测试类
    """

    @pytest.mark.run(order=230)
    @allure.title("创建专业图谱概览")
    def test_010_create_major_graph_overview(self, page: Page, screenshot_helper, base_url):
        """
        创建专业图谱概览：进入专业知识图谱，点击创建专业图谱，添加若干节点构成概览。
        """
        # 专业管理员用户信息
        cms_prof_info = DATA["user"]["prof_cms"]
        # 专业图谱节点列表（类型 + 名称）
        node_list = DATA["major_graph"]["节点列表"]

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

        with allure.step("点击图谱概览"):
            graph_page = MajorGraphOverviewPage(page)
            graph_page.click_menu_item("图谱概览")

        with allure.step("点击创建专业图谱"):
            graph_page.click_create_major_graph_button()
            screenshot_helper.capture_full_page("进入创建专业图谱")

        with allure.step("添加节点"):
            for node in node_list:
                graph_page.add_major_node(node["类型"], node["名称"])
                assert graph_page.is_add_node_success(), f"添加节点失败: {node['类型']} - {node['名称']}"
            screenshot_helper.capture_full_page("专业图谱概览创建完成")

        with allure.step("关联节点"):
            graph_page.associate_node_by_names(node_list[0]["名称"], node_list[1]["类型"], node_list[1]["名称"])
            assert graph_page.is_associate_node_success(), f"关联节点失败"
            graph_page.associate_node_by_names(node_list[2]["名称"], node_list[3]["类型"], node_list[3]["名称"])
            assert graph_page.is_associate_node_success(), f"关联节点失败:"
            screenshot_helper.capture_full_page("专业图谱概览关联完成")
