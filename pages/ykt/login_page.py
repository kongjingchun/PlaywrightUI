import io
import re
import time
from typing import Optional

import allure
from PIL import Image
from playwright.sync_api import Page

from base.base_page import BasePage
from config.env_config import EnvConfig
from utils.click_captcha_ddddocr import ordered_click_centers_from_image


class YktLoginPage(BasePage):
    """
    雨课堂登录页面
    设计原则：
    - 继承 BasePage，复用基类方法
    - Page 层不写 log，日志由 BasePage 统一输出
    - 方法返回 self 支持链式调用
    - URL 从配置或参数获取，不写死

    使用方法：
        # 使用环境配置的 base_url
        login_page = YktLoginPage(page)

        # 或指定 base_url（如从 fixture 注入）
        login_page = YktLoginPage(page, base_url="https://www.yuketang.cn")

        login_page.goto().login("admin", "123456")
    """

    # 登录路径（相对 base_url）
    LOGIN_PATH = "/web"

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page)
        # base_url 优先使用传入参数，否则从环境配置获取
        self._base_url = base_url or EnvConfig().base_url or "https://www.yuketang.cn"
        self._login_url = self._base_url.rstrip("/") + self.LOGIN_PATH

        # ========== 登陆页面元素 ==========
        # 账号密码登录切换按钮
        self.account_password_login_switch_button = page.get_by_role("img", name="账号密码登录")
        # 手机号输入框
        self.phone_input = page.get_by_role("textbox", name="输入手机号")
        # 密码输入框
        self.password_input = page.get_by_role("textbox", name="输入密码")
        # 登录按钮
        self.login_button = page.get_by_text("登录", exact=True)
    # ==================== 页面导航 ====================

    @allure.step("打开登录页面")
    def goto(self) -> "YktLoginPage":
        """打开登录页面"""
        self.navigate_to(self._login_url)
        return self

    # ==================== 元素操作 ====================
    @allure.step("点击账号密码登录切换按钮")
    def click_account_password_login_switch_button(self) -> "YktLoginPage":
        """点击账号密码登录切换按钮"""
        self.click_element(self.account_password_login_switch_button)
        return self

    @allure.step("处理点字防水墙（若出现）")
    def solve_waterproof_wall_if_present(
        self,
        captcha_char_pool: Optional[str] = None,
        wait_timeout_ms: int = 10000,
    ) -> bool:
        """
        若出现「请依次点击」类点字验证码：截图验证码图 → ddddocr 定位与识别 → 依次点击 → 确定。

        :param captcha_char_pool: 传给 ddddocr set_ranges 的候选字串；不传则用语义解析的题目字拼接。
        :return: 是否检测到并尝试处理验证码弹层（未出现则 False）
        """
        page = self.page
        try:
            page.get_by_text(re.compile(r"请依次点击")).first.wait_for(
                state="visible", timeout=wait_timeout_ms
            )
        except Exception:
            return False

        instr_el = page.get_by_text(re.compile(r"请依次点击")).first
        instruction_text = instr_el.inner_text()
        # 验证码图：优先取题目文案后的第一张图；canvas 类验证码用 canvas
        img = instr_el.locator("xpath=following::img[1]")
        if not img.is_visible(timeout=2000):
            modal = page.locator("div").filter(has_text="安全验证").first
            img = modal.locator("img").first
        if not img.is_visible(timeout=2000):
            img = page.locator("xpath=//*[contains(., '请依次点击')]/following::img[1]")
        if not img.is_visible(timeout=2000):
            # 部分站点用 canvas 画图
            img = instr_el.locator("xpath=following::canvas[1]")
        if not img.is_visible(timeout=2000):
            modal = page.locator("div").filter(has_text="安全验证").first
            img = modal.locator("canvas").first

        img.scroll_into_view_if_needed(timeout=5000)
        png = img.screenshot()
        box = img.bounding_box()
        if not box:
            return False

        centers = ordered_click_centers_from_image(
            png, instruction_text, captcha_char_pool
        )
        # ddddocr 坐标基于截图像素；Playwright 点击需相对元素的 CSS 尺寸，高 DPI 下二者比例用缩放对齐
        pil_im = Image.open(io.BytesIO(png))
        pw, ph = pil_im.size
        if pw <= 0 or ph <= 0:
            return False
        sx = float(box["width"]) / float(pw)
        sy = float(box["height"]) / float(ph)

        for cx, cy in centers:
            img.click(
                position={"x": cx * sx, "y": cy * sy},
                timeout=10_000,
                force=True,
            )
            time.sleep(0.2)

        confirm = page.get_by_role("button", name="确定")
        if confirm.is_visible(timeout=2000):
            confirm.click()
        else:
            page.get_by_text("确定", exact=True).click()
        page.wait_for_timeout(500)
        return True

    # ==================== 业务方法 ====================
    @allure.step("手机号密码登录: {phone}")
    def login(
        self,
        phone: str,
        password: str,
        captcha_char_pool: Optional[str] = None,
    ) -> "YktLoginPage":
        """
        手机号密码登录流程；若登录后出现点字防水墙，将自动尝试识别并点击（ddddocr）。

        :param captcha_char_pool: 验证码识别候选字（与 test.py CHAR_POOL 一致）；可从 data/ykt 配置传入。
        """
        self.goto()
        self.click_account_password_login_switch_button()
        self.fill_element(self.phone_input, phone)
        self.fill_element(self.password_input, password)
        self.click_element(self.login_button)
        # 登录后验证码异步弹出，略等再检测「请依次点击」
        self.page.wait_for_timeout(600)
        try:
            self.solve_waterproof_wall_if_present(captcha_char_pool=captcha_char_pool)
        except Exception as e:
            self.logger.warning(f"防水墙自动处理未成功（可忽略若本次无验证码）: {e}")
        return self
