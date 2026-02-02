from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://47.116.12.183/login.html")
    page.get_by_label("用 户 名:",exact=True).fill("test")
    page.get_by_label("密 码:",exact=True).fill("123456")
    page.get_by_role("button", name="登录").click()
    page.get_by_role('link', name='新增模块').click()
    page.get_by_label("模块名称:").fill("test")
    page.get_by_role("listbox").get_by_role("option", name="78119270ead64c1bab153a73f").click()
    page.get_by_label("模块描述:").fill("test")
    page.get_by_text('点击提交').click()
    page.pause()
