# ========================================
# Page Object Model (POM) 模块
# ========================================
# 该模块包含所有页面对象类，遵循 Page Object Model 设计模式。
# 
# POM 模式的优点：
# 1. 提高代码复用性 - 页面元素和操作只定义一次
# 2. 提高可维护性 - UI 变化只需修改对应的 Page 类
# 3. 提高可读性 - 测试用例代码更简洁清晰
# 4. 降低耦合度 - 测试逻辑与页面实现分离
#
# 目录结构：
# pages/
# ├── __init__.py          # 当前文件
# ├── demo/
# │   ├── __init__.py
# │   ├── login_page.py    # 登录页面
# │   └── home_page.py     # 首页
# └── gqkt/
#     ├── __init__.py
#     ├── login_page.py    # 光穹课堂登录页面
#     └── api/
#         ├── __init__.py
#         └── cms_api_page.py  # CMS API 页面
#
# base/
# ├── base_page.py         # 基础页面类（所有页面的父类）
# └── base_api.py          # 基础 API 类（所有接口的父类）
# ========================================

from base.base_page import BasePage
from base.base_api import BaseAPI
from pages.demo.login_page import LoginPage
from pages.demo.home_page import HomePage
from pages.gqkt.login_page import GqktLoginPage

__all__ = ['BasePage', 'BaseAPI', 'LoginPage', 'HomePage', 'GqktLoginPage']
