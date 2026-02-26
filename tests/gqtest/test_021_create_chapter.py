# ========================================
# 创建章节
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖课程创建流程
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import CourseContentPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建章节")
class TestCreateChapter:
    """
    创建章节测试类
    """

    @pytest.mark.run(order=341)
    @allure.title("创建课程内容版本")
    def test_create_chapter(self, page: Page, screenshot_helper, base_url):
        """
        创建课程内容版
        """
        teacher_cms = DATA["user"]["prof_cms"]
        course_name = DATA["course"]["课程名称"]
        ch_config = DATA["chapter"]

        helper = TestContextHelper()

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, teacher_cms["username"], teacher_cms["password"],
                "智慧大学", "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入课程内容"):
            content_page = CourseContentPage(page)
            content_page.click_left_menu_by_name("课程设计")
            content_page.click_left_menu_by_name("课程内容")

        with allure.step("创建章"):
            content_page.create_chapter(
                chapter_name=ch_config["章名称"],
                chapter_description=ch_config.get("章描述", "")
            )
            assert content_page.is_create_chapter_success(), "创建章失败"
            screenshot_helper.capture_full_page("章创建完成")

        with allure.step("在主章下添加关联学习单元"):
            content_page.add_all_learning_units_to_chapter(
                chapter_name=ch_config["章名称"],
                select_only=ch_config.get("主章关联学习单元")
            )
            assert content_page.is_add_learning_units_to_chapter_success(), "主章添加学习单元失败"
            screenshot_helper.capture_full_page("主章学习单元添加完成")

        with allure.step("在该章下创建子章节"):
            content_page.add_subsection_to_chapter(
                chapter_name=ch_config["章名称"],
                subsection_name=ch_config["子章节名称"],
                subsection_description=ch_config.get("子章节描述", "")
            )
            assert content_page.is_create_chapter_success(), "创建子章节失败"
            screenshot_helper.capture_full_page("子章节创建完成")

        with allure.step("在子章节下添加关联学习单元"):
            content_page.add_all_learning_units_to_chapter(
                chapter_name=ch_config["子章节名称"],
                select_only=ch_config.get("子章节关联学习单元")
            )
            assert content_page.is_add_learning_units_to_chapter_success(), "子章节添加学习单元失败"
            screenshot_helper.capture_full_page("子章节学习单元添加完成")

        with allure.step("在该章下关联知识点章节"):
            content_page.associate_first_level_knowledge_graph_by_chapter(
                chapter_name=ch_config["子章节名称"],
                knowledge_graph_name=ch_config["知识点章节名称"]
            )
            assert content_page.is_add_knowledge_graph_to_chapter_success(), "关联知识点章节失败"
            screenshot_helper.capture_full_page("关联知识点章节完成")

        with allure.step("创建版本"):
            content_page.create_version_from_default(version_name=ch_config["版本名称"])
            assert content_page.is_create_version_success(), "创建版本失败"
            screenshot_helper.capture_full_page("创建版本完成")
