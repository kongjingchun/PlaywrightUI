# ========================================
# 设置我的班级
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖课程创建流程、test_019 创建教学班
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage, CourseGuidePage, TeachingContentPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("设置我的班级")
class TestSetMyClass:
    """
    设置我的班级测试类
    """

    @pytest.mark.run(order=342)
    @allure.title("设置我的班级")
    def test_set_my_class(self, page: Page, screenshot_helper, base_url):
        """
        设置我的班级
        """
        teacher_cms = DATA["user"]["prof_cms"]
        mc_config = DATA["my_class"]

        helper = TestContextHelper()

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, teacher_cms["username"], teacher_cms["password"],
                "智慧大学", "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我的班级"):
            helper.click_left_menu_item(page, "我的班级")

        with allure.step("搜索并点击班级卡片"):
            course_guide_page = CourseGuidePage(page)
            course_guide_page.click_class_card_by_name(mc_config["班级名称"])

        with allure.step("课程导读设置"):
            course_guide_page.click_edit_button()
            course_guide_page.click_save_button()
            assert course_guide_page.is_save_course_guide_success(), "设置课程导读失败"
            screenshot_helper.capture_full_page("课程导读设置完成")
        with allure.step("教学内容设置-引用课程内容"):
            teaching_content_page = TeachingContentPage(page)
            teaching_content_page.click_tab_by_name("教学内容")
            teaching_content_page.reference_course_content(mc_config["引用版本名称"])
            assert teaching_content_page.is_reference_course_content_success(), "引用课程内容失败"
            screenshot_helper.capture_full_page("引用课程内容完成")

        with allure.step("添加一个章"):
            teaching_content_page.add_chapter(
                chapter_name=mc_config["章名称"],
                chapter_description=mc_config.get("章描述", "")
            )
            assert teaching_content_page.is_create_chapter_success(), "添加章失败"
            screenshot_helper.capture_full_page("添加章完成")

        with allure.step("章下添加关联学习单元"):
            teaching_content_page.add_learning_units_to_chapter(
                chapter_name=mc_config["章名称"],
                select_only=mc_config.get("主章关联学习单元")
            )
            assert teaching_content_page.is_add_learning_units_to_chapter_success(), "章添加学习单元失败"
            screenshot_helper.capture_full_page("章添加学习单元完成")

        with allure.step("章下添加一个节"):
            teaching_content_page.add_section_to_chapter(
                chapter_name=mc_config["章名称"],
                section_name=mc_config["子章节名称"],
                section_description=mc_config.get("子章节描述", "")
            )
            assert teaching_content_page.is_create_chapter_success(), "添加节失败"
            screenshot_helper.capture_full_page("添加节完成")

        with allure.step("节下添加关联学习单元"):
            teaching_content_page.add_learning_units_to_chapter(
                chapter_name=mc_config["子章节名称"],
                select_only=mc_config.get("子章节关联学习单元")
            )
            assert teaching_content_page.is_add_learning_units_to_chapter_success(), "节添加学习单元失败"
            screenshot_helper.capture_full_page("节添加学习单元完成")

        with allure.step("章下添加一个知识图谱"):
            teaching_content_page.add_knowledge_graph_to_chapter(
                chapter_name=mc_config["章名称"],
                knowledge_graph_name=mc_config["知识点章节名称"]
            )
            assert teaching_content_page.is_add_knowledge_graph_to_chapter_success(), "添加知识图谱失败"
            screenshot_helper.capture_full_page("添加知识图谱完成")
