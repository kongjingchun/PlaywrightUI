# ========================================
# 创建能力 group graph
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import CapabilityGroupGraphPage
from tests.gqtest import TestContextHelper

@allure.feature("光穹课堂")
@allure.story("创建能力图谱")
class TestCreateCapabilityGroupGraph:
    """
    创建能力 group graph 测试类
    """

    @pytest.mark.run(order=380)
    @allure.title("创建能力图谱并添加一级能力及子能力")
    def test_create_capability_group_graph(self, page: Page, screenshot_helper, base_url, gqkt_data: dict):
        """
        创建能力图谱，添加问题分析和抽象能力、算法和结构设计能力两个一级节点，
        再递归添加其子能力（如计算思维、分解和抽象等）
        """
        # 教师用户信息
        teacher_cms = gqkt_data["user"]["teacher_cms"]
        # 课程名称（用于在我教的课中进入该课程）
        course_name = gqkt_data["course"]["课程名称"]

        helper = TestContextHelper()

        capability_graph = gqkt_data["capability_graph"]

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, teacher_cms["username"], teacher_cms["password"],
                gqkt_data["school_name"], "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入能力图谱"):
            cap_group_graph_page = CapabilityGroupGraphPage(page)
            cap_group_graph_page.click_left_menu_by_name("AI垂直模型")
            cap_group_graph_page.click_left_menu_by_name("能力图谱")

        with allure.step("创建能力图谱"):
            cap_group_graph_page.click_create_graph_button()
            assert cap_group_graph_page.is_create_graph_success(), "创建能力图谱失败"
            screenshot_helper.capture_viewport("创建能力图谱完成")
            
        # with allure.step("编辑能力图谱"):
        #     cap_group_graph_page.click_edit_button()

        cg = capability_graph
        level1 = cg.get("一级能力", [])
        level2 = cg.get("二级能力", [])
        level3 = cg.get("三级能力", [])

        with allure.step("添加一级能力"):
            for cap in level1:
                name = cap["能力名称"]
                desc = cap.get("描述", "")
                tags = cap.get("标签")
                knowledge = cap.get("关联知识点")
                cap_group_graph_page.add_main_ability(name, desc, tags, knowledge)
                assert cap_group_graph_page.is_add_sub_ability_success(), f"添加一级能力失败: {name}"

        with allure.step("添加二级能力"):
            for cap in level2:
                parent = cap["父级"]
                name = cap["能力名称"]
                desc = cap.get("描述", "")
                tags = cap.get("标签")
                knowledge = cap.get("关联知识点")
                cap_group_graph_page.add_sub_ability(parent, name, desc, tags, knowledge)
                assert cap_group_graph_page.is_add_sub_ability_success(), f"添加二级能力失败: {name}"

        with allure.step("添加三级能力"):
            for cap in level3:
                parent = cap["父级"]
                name = cap["能力名称"]
                desc = cap.get("描述", "")
                tags = cap.get("标签")
                knowledge = cap.get("关联知识点")
                cap_group_graph_page.add_sub_ability(parent, name, desc, tags, knowledge)
                assert cap_group_graph_page.is_add_sub_ability_success(), f"添加三级能力失败: {name}"

            screenshot_helper.capture_viewport("添加能力完成")
