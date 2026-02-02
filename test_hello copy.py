from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.gqkt.cn/")
    page.get_by_text("登录",exact=True).click()
    page.get_by_role("textbox", name="请输入您的账户").type("superadmin")
    page.get_by_placeholder("请输入您的密码").fill("gqkt111!")
    page.get_by_role("button", name="登录",exact=True).click()
    page.get_by_text('我教的课').click()
    page.pause()