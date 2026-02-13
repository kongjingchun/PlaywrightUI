# ========================================
# 添加课程资源
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖课程创建流程
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from common.tools import build_path
from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import CourseResourcePage
from pages.gqkt.teacher_workbench.course_workbench.course_construction.course_resource import LinkPage, QuestionBankPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("添加课程资源")
class TestAddCourseResource:
    """
    添加课程资源测试类
    """

    @pytest.mark.run(order=320)
    @allure.title("添加课程资源")
    def test_add_course_resource(self, page: Page, screenshot_helper, base_url):
        """
        添加课程资源
        """
        # 教师用户信息（有课程权限的专业负责人）
        teacher_cms = DATA["user"]["prof_cms"]
        # 课程名称（用于在我教的课中进入该课程）
        course_name = DATA["course"]["课程名称"]
        # 课程资源配置
        course_resource = DATA["course_resource"]

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

        with allure.step("进入课程资源"):
            resource_page = CourseResourcePage(page)
            resource_page.click_left_menu_by_name("课程资源")

        # with allure.step("上传教材"):
        #     resource_page.click_left_menu_by_name("教材")
        #     for path_str in course_resource["教材"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传教材失败: {path_str}"
        #     screenshot_helper.capture_full_page("教材上传完成")

        # with allure.step("上传课件"):
        #     resource_page.click_left_menu_by_name("课件")
        #     for path_str in course_resource["课件"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传课件失败: {path_str}"
        #     screenshot_helper.capture_full_page("课件上传完成")

        # with allure.step("上传视频"):
        #     resource_page.click_left_menu_by_name("视频")
        #     for path_str in course_resource["视频"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传视频失败: {path_str}"
        #     screenshot_helper.capture_full_page("视频上传完成")

        # with allure.step("上传音频"):
        #     resource_page.click_left_menu_by_name("音频")
        #     for path_str in course_resource["音频"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传音频失败: {path_str}"
        #     screenshot_helper.capture_full_page("音频上传完成")

        # with allure.step("上传论文"):
        #     resource_page.click_left_menu_by_name("论文")
        #     for path_str in course_resource["论文"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传论文失败: {path_str}"
        #     screenshot_helper.capture_full_page("论文上传完成")

        # with allure.step("上传案例"):
        #     resource_page.click_left_menu_by_name("案例")
        #     for path_str in course_resource["案例"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传案例失败: {path_str}"
        #     screenshot_helper.capture_full_page("案例上传完成")

        # with allure.step("上传图片"):
        #     resource_page.click_left_menu_by_name("图片")
        #     for path_str in course_resource["图片"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传图片失败: {path_str}"
        #     screenshot_helper.capture_full_page("图片上传完成")

        # with allure.step("上传其他资料"):
        #     resource_page.click_left_menu_by_name("其他资料")
        #     for path_str in course_resource["其他资料"]:
        #         file_path = build_path(path_str)
        #         assert file_path.exists(), f"上传文件不存在: {file_path}"
        #         resource_page.upload_file(str(file_path))
        #         assert resource_page.is_upload_file_success(), f"上传其他资料失败: {path_str}"
        #     screenshot_helper.capture_full_page("其他资料上传完成")

        # with allure.step("新建链接"):
        #     link_page = LinkPage(page)
        #     link_page.click_left_menu_by_name("链接")
        #     for path_str in course_resource["链接"]:
        #         link_page.create_link(path_str)
        #         assert link_page.is_link_create_success(), f"创建链接失败: {path_str}"
        #     screenshot_helper.capture_full_page("链接创建完成")

        # with allure.step("新建简答题"):
        #     resource_page.click_left_menu_by_name("题库")
        #     qb_config = DATA["question_bank"]["简答题"]
        #     question_page = QuestionBankPage(page)
        #     knowledge_info = None
        #     if "知识点" in qb_config:
        #         k_list = qb_config["知识点"]
        #         k_list = k_list if isinstance(k_list, list) else [k_list]
        #         knowledge_info = [
        #             {"name": k["名称"], "open_to_student": k.get("开放给学生", False)}
        #             for k in k_list
        #         ]
        #     question_page.create_short_answer_question(
        #         question_content=qb_config["题目内容"],
        #         reference_answer=qb_config["参考答案"],
        #         question_analysis=qb_config.get("题目解析"),
        #         knowledge_info=knowledge_info
        #     )
        #     assert question_page.is_question_create_success(), "新建简答题失败"
        #     screenshot_helper.capture_full_page("简答题创建完成")

        # with allure.step("导入题库"):
        #     resource_page.click_left_menu_by_name("题库")
        #     import_path = DATA["question_bank"]["导入文件"]
        #     file_path = build_path(import_path)
        #     assert file_path.exists(), f"导入文件不存在: {file_path}"
        #     question_page.upload_question(str(file_path))
        #     assert question_page.is_question_upload_success(), "导入题库失败"
        #     screenshot_helper.capture_full_page("题库导入完成")
