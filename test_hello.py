"""Playwright UI 自动化测试 - 使用 pytest 运行。"""
from playwright.sync_api import Page, expect
from time import sleep


def test_my_test(page: Page):
    page.goto("https://www.gqkt.cn/")
    page.get_by_role("button", name="登录").click()
    # 断点调试
    page.pause()
    page.locator("div").nth(3).click()
    page.get_by_role("textbox", name="请输入您的账户").click()
    page.get_by_role("textbox", name="请输入您的账户").fill("superadmin")
    page.get_by_role("textbox", name="请输入您的账户").press("Tab")
    page.get_by_role("textbox", name="请输入您的密码").fill("gqkt111!")
    page.get_by_role("button", name="登录").click()
    sleep(5)
