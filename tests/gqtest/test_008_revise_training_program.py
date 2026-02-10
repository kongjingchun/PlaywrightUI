# ========================================
# 修订培养方案
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

from tkinter import W
import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.ai_major import TrainingProgramManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("修订培养方案")
class TestReviseTrainingProgram:
    """
    修订培养方案测试类
    """

    @pytest.mark.run(order=210)
    @allure.title("修订培养方案")
    def test_008_revise_training_program(self, page: Page, screenshot_helper, base_url):
        """
        修订培养方案
        """
        # CMS 专业管理员用户信息
        cms_prof_info = DATA["user"]["prof_cms"]
        # 课程信息
        course_info = DATA["course"]
        # 培养方案信息
        tp_info = DATA["training_program"]

        helper = TestContextHelper()

        with allure.step("登录专业管理员"):
            helper.login_and_init(
                page, base_url, cms_prof_info["username"], cms_prof_info["password"],
                "智慧大学", "专业管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击培养方案管理"):
            helper.click_left_menu_item(page, "培养方案管理")

        with allure.step("修订培养方案：专业信息"):
            tp_manage_page = TrainingProgramManagePage(page)
            tp_manage_page.click_edit_training_program_menu(tp_info["方案名称"])
            tp_manage_page.edit_training_program_major_info(tp_info["专业信息"]["专业概述"])
            assert tp_manage_page.is_edit_training_program_success(), "修订培养方案：专业信息失败"
            screenshot_helper.capture_full_page("修订培养方案：专业信息成功")

        with allure.step("修订培养方案：培养目标概述"):
            tp_manage_page.edit_training_program_major_training_goal(tp_info["培养目标"]["培养目标概述"])
            assert tp_manage_page.is_edit_training_program_success(), "修订培养方案：培养目标概述失败"
            screenshot_helper.capture_full_page("修订培养方案：培养目标概述成功")

        with allure.step("修订培养方案：添加培养目标"):
            for desc in tp_info["培养目标"]["培养目标描述"]:
                tp_manage_page.add_training_goal(desc)
                screenshot_helper.capture_full_page("修订培养方案：添加培养目标成功")

        with allure.step("修订培养方案：毕业要求概述"):
            tp_manage_page.edit_training_program_major_graduation_requirement(tp_info["毕业要求"]["毕业要求概述"])
            assert tp_manage_page.is_edit_training_program_success(), "修订培养方案：毕业要求概述失败"
            screenshot_helper.capture_full_page("修订培养方案：毕业要求概述成功")

        with allure.step("修订培养方案：添加指标点"):
            for indicator in tp_info["指标点"].values():
                tp_manage_page.add_graduation_requirement(indicator["指标点名称"], indicator["指标点描述"], indicator["分解指标点名称"], indicator["分解指标点描述"])
                screenshot_helper.capture_full_page("修订培养方案：添加指标点成功")
            screenshot_helper.capture_full_page("修订培养方案：添加指标点成功")
        with allure.step("修订培养方案：添加目标支撑"):
            tp_manage_page.add_target_support()
            assert tp_manage_page.is_edit_training_program_success(), "修订培养方案：添加目标支撑失败"
            screenshot_helper.capture_full_page("修订培养方案：添加目标支撑成功")
        with allure.step("修订培养方案：添加课程"):
            tp_manage_page.add_course(course_info["课程名称"])
            assert tp_manage_page.is_add_course_success(), "修订培养方案：添加课程失败"
            screenshot_helper.capture_full_page("修订培养方案：添加课程成功")
