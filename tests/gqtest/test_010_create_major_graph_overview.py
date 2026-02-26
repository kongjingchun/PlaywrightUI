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
    def test_create_major_graph_overview(self, page: Page, screenshot_helper, base_url):
        """
        创建专业图谱概览：进入专业知识图谱，点击创建专业图谱，添加若干节点构成概览。
        """
        # 专业管理员用户信息
        cms_prof_info = DATA["user"]["prof_cms"]
        # 专业图谱节点列表（类型 + 名称）
        node_list = DATA["major_graph"]["节点列表"]
        # 专业图谱名称
        graph_name = DATA["major_graph"]["图谱名称"]

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

        with allure.step("创建专业图谱"):
            graph_page.create_major_graph(graph_name)

        with allure.step("添加节点"):
            for node in node_list:
                graph_page.add_major_node(
                    node["类型"],
                    node["名称"],
                    node.get("描述", "")
                )
                assert graph_page.is_add_node_success(), f"添加节点失败: {node['类型']} - {node['名称']}"
        screenshot_helper.capture_full_page("专业图谱概览创建完成")

        with allure.step("关联节点"):
            # (源节点索引, 目标节点索引) 跨类型关联形成更丰富的图谱
            # (源节点索引, 目标节点索引)，仅跨类型关联（同类型不关联）
            associate_pairs = [
                (1, 10),  # 责任心 -> 爱国敬业精神 (能力->素质)
                (3, 5),   # 逻辑思维 -> 操作系统引论 (能力->知识)
                (5, 15),  # 操作系统引论 -> 软件工程的核心定义... (知识->问题)
                (4, 19),  # 性能调优 -> 软件测试的核心目的... (能力->问题)
                (8, 17),  # 软件测试 -> 常见的软件开发模型... (知识->问题)
                (0, 12),  # 跨部门沟通 -> 良好的职业道德 (能力->素质)
                (2, 7),   # 系统架构设计 -> 进程的描述与控制 (能力->知识)
                (11, 16),  # 社会责任感 -> 软件工程生命周期... (素质->问题)
                (9, 13),  # 项目计划 -> 健康的身心 (知识->素质)
            ]
            for src_idx, tgt_idx in associate_pairs:
                src, tgt = node_list[src_idx], node_list[tgt_idx]
                graph_page.associate_node_by_names(src["名称"], tgt["类型"], tgt["名称"])
                assert graph_page.is_associate_node_success(), f"关联节点失败: {src['名称']} -> {tgt['名称']}"
            screenshot_helper.capture_full_page("专业图谱概览关联完成")
