# ========================================
# 创建课程内容
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
@allure.story("创建课程内容")
class TestCreateCourseContent:
    """
    创建课程内容测试类
    """

    @pytest.mark.run(order=340)
    @allure.title("创建课程内容")
    def test_create_course_content(self, page: Page, screenshot_helper, base_url):
        """
        根据 yaml 配置创建课程内容（视频/资料/课件/讨论/作业/考试/链接/音频/课堂）
        """
        teacher_cms = DATA["user"]["prof_cms"]
        course_name = DATA["course"]["课程名称"]

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

        with allure.step("点击管理学习单元"):
            content_page.click_element(content_page.manage_learning_unit_button)

        cc_config = DATA["course_content"]
        # 支持的学习单元类型（待页面补充 create_xxx_learning_unit 后扩展 课件/讨论/作业）
        supported_types = ("视频", "资料", "课件", "讨论", "作业", "考试", "链接", "音频", "课堂")

        for unit_type, items in cc_config.items():
            if unit_type not in supported_types:
                continue
            for idx, item in enumerate(items):
                title = item.get("学习单元标题", "")
                content = item.get("学习单元正文", "")
                step_name = f"创建{unit_type}学习单元{idx + 1}: {title}"

                with allure.step(step_name):
                    if unit_type == "视频":
                        content_page.create_video_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "资料":
                        content_page.create_material_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "课件":
                        content_page.create_courseware_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "讨论":
                        content_page.create_discussion_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "作业":
                        content_page.create_homework_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "考试":
                        content_page.create_exam_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "链接":
                        content_page.create_link_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "音频":
                        content_page.create_audio_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    elif unit_type == "课堂":
                        content_page.create_classroom_learning_unit(
                            learning_unit_title=title,
                            learning_unit_content=content
                        )
                    else:
                        raise NotImplementedError(f"学习单元类型「{unit_type}」暂未实现")
                    assert content_page.is_create_learning_unit_success(), f"创建{unit_type}学习单元失败: {title}"

        screenshot_helper.capture_full_page("课程内容创建完成")
