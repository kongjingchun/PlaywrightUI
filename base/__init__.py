# ========================================
# base 模块
# ========================================
# 存放所有基类
# - BasePage: UI 页面基类
# - BaseAPI: API 接口基类
# ========================================

from base.base_page import BasePage, PageAssertions
from base.base_api import BaseAPI

__all__ = [
    "BasePage",
    "PageAssertions",
    "BaseAPI",
]
