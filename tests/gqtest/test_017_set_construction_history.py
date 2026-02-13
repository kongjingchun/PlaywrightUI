# ========================================
# 设置建设历程
# ========================================
# 符合 Page Object Model 设计模式
# 断言在测试用例中，不在页面对象中
# 依赖课程创建流程
# ========================================

import pytest
import allure
from playwright.sync_api import Page

from pages.gqkt.teacher_workbench import MyTaughtCoursesPage
from pages.gqkt.teacher_workbench.course_workbench.course_construction import ConstructionHistoryPage
from tests.gqtest import TestContextHelper
from utils.data_loader import load_yaml


DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("光穹课堂")
@allure.story("设置建设历程")
class TestSetConstructionHistory:
    """
    设置建设历程测试类
    """

    @pytest.mark.run(order=310)
    @allure.title("设置建设历程")
    def test_set_construction_history(self, page: Page, screenshot_helper, base_url):
        """
        设置建设历程：
        """
        # 教师用户信息（有课程权限的专业负责人）
        teacher_cms = DATA["user"]["prof_cms"]
        # 课程名称（用于在我教的课中进入该课程）
        course_name = DATA["course"]["课程名称"]
        # 建设历程配置
        construction_history = DATA["course_outline"]["建设历程"]

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

        with allure.step("进入建设历程"):
            history_page = ConstructionHistoryPage(page)
            history_page.click_left_menu_by_name("课程大纲")
            history_page.click_left_menu_by_name("建设历程")

        with allure.step("设置建设历程并保存"):
            history_page.set_construction_history(
                construction_time=construction_history["建设时间"],
                content=construction_history["建设内容"],
                honor=construction_history["获得荣誉"],
                team=construction_history["建设团队"]
            )
            assert history_page.is_set_construction_history_success(), "设置建设历程失败"
            screenshot_helper.capture_full_page("建设历程设置完成")
