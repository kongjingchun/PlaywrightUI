# ========================================
# 创建培养方案
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.ai_major import TrainingProgramManagePage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("创建培养方案")
class TestCreateTrainingProgram:
    """
    创建培养方案测试类
    """

    @pytest.mark.run(order=200)
    @allure.title("创建培养方案")
    def test_007_create_training_program(self, page: Page, screenshot_helper, base_url):
        """
        创建培养方案
        """
        # CMS 教务管理员用户信息
        cms_prof_info = DATA["user"]["prof_cms"]
        # 培养方案信息
        tp_info = DATA["training_program"]

        helper = TestContextHelper()

        with allure.step("登录教务管理员"):
            helper.login_and_init(
                page, base_url, cms_prof_info["username"], cms_prof_info["password"],
                "智慧大学", "专业管理员",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击培养方案管理"):
            helper.click_left_menu_item(page, "培养方案管理")

        with allure.step("创建培养方案"):
            tp_manage_page = TrainingProgramManagePage(page)
            tp_manage_page.create_training_program(
                training_program_name=tp_info["方案名称"],
                training_program_major=tp_info["关联专业"],
                training_program_type=tp_info["培养类型"],
                training_program_level=tp_info["培养层次"],
                training_program_duration=tp_info["学制"],
                training_program_credit_requirement=tp_info["学分要求"],
                training_program_degree=tp_info["授予学位"],
                training_program_version_year=tp_info["版本年份"]
            )
            assert tp_manage_page.is_create_training_program_success(), "创建培养方案失败"
            screenshot_helper.capture_full_page("创建培养方案成功")
