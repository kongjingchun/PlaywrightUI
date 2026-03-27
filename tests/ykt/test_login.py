# ========================================
# 雨课堂网页版 - 登录相关用例
# ========================================
# 数据文件：在 config/environments/ykt/*.yaml 中配置 ykt_config_file（相对于 data/）
# 可选在 data/ykt/*.yaml 中配置 captcha_char_pool，供点字防水墙 ddddocr 候选字（与 test.py CHAR_POOL 一致）
# 执行示例：
#   pytest tests/ykt/test_login.py --config=config/environments/ykt/prod.yaml -v
# ========================================

from time import sleep
import pytest
import allure
from playwright.sync_api import Page

from pages.ykt import YktLoginPage


@allure.feature("雨课堂")
@allure.story("登录")
class TestYktLogin:
    """雨课堂网页版登录"""

    @pytest.mark.login
    def test_login(self, page: Page, ykt_data: dict):
        teacher_info = ykt_data["user"]["teacher"]
        pool = ykt_data.get("captcha_char_pool")
        if isinstance(pool, str):
            pool = pool.strip() or None
        else:
            pool = None

        login_page = YktLoginPage(page)
        login_page.login(
            str(teacher_info["账号"]),
            str(teacher_info["密码"]),
            captcha_char_pool=pool,
        )
        sleep(100)
