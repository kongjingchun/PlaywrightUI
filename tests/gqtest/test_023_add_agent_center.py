# ========================================
# 添加智能体中心
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import AgentCenterPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")

# 本次添加的智能体卡片
AGENT_NAMES = ["智能教案", "教学案例", "伴学书童", "智能出题", "课程设计师"]


@allure.feature("光穹课堂")
@allure.story("添加智能体中心")
class TestAddAgentCenter:
    """
    添加智能体中心测试类
    """

    @pytest.mark.run(order=370)
    @allure.title("添加智能体中心")
    def test_add_agent_center(self, page: Page, screenshot_helper, base_url):
        """
        进入智能体中心，点击智能体广场，依次添加智能教案、教学案例、伴学书童、智能出题、课程设计师
        """
        prof_cms = DATA["user"]["prof_cms"]
        course_name = DATA["course"]["课程名称"]

        helper = TestContextHelper()

        with allure.step("登录教师"):
            helper.login_and_init(
                page, base_url, prof_cms["username"], prof_cms["password"],
                "智慧大学", "教师",
                use_saved_auth=True,
                save_auth=True
            )

        with allure.step("点击我教的课"):
            helper.click_left_menu_item(page, "我教的课")

        with allure.step("进入课程工作台"):
            my_courses_page = MyTaughtCoursesPage(page)
            my_courses_page.click_course_card_by_name(course_name)

        with allure.step("进入智能体中心"):
            agent_center_page = AgentCenterPage(page)
            agent_center_page.click_left_menu_by_name("AI教创空间")
            agent_center_page.click_left_menu_by_name("智能体中心")

        with allure.step("点击智能体广场按钮"):
            agent_center_page.click_agent_square_button()

        with allure.step("依次添加智能体"):
            for agent_name in AGENT_NAMES:
                agent_center_page.click_join_agent_button_by_name(agent_name)
                assert agent_center_page.is_add_agent_success(), f"添加智能体失败: {agent_name}"

            screenshot_helper.capture_full_page("添加智能体完成")
