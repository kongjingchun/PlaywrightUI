# ========================================
# 根级 conftest.py - pytest 全局配置
# ========================================
# 该文件是 pytest 的全局配置文件，位于项目根目录。
# 包含所有测试共享的 fixtures 和钩子函数。
#
# 注意：pytest-playwright 插件已提供以下参数和 fixtures：
# - 参数：--browser, --headed, --slowmo, --browser-channel
# - fixtures: page, context, browser, browser_name, browser_channel
# 我们不需要重复定义这些，只需扩展自定义的部分。
#
# 主要功能：
# 1. 扩展的命令行参数（环境切换等）
# 2. 失败截图和日志记录
# 3. Allure 报告集成
# 4. 测试数据加载
# ========================================

import pytest
import os
import allure
from datetime import datetime
from pathlib import Path
from typing import Generator

from playwright.sync_api import Page

# 项目模块导入
from config.settings import Settings
from config.env_config import EnvConfig
from utils.logger import Logger
from utils.screenshot_helper import ScreenshotHelper, ConsoleLogCollector
from utils.allure_helper import AllureHelper
from utils.data_loader import DataLoader


# ==================== 全局日志实例 ====================
logger = Logger("conftest")


# ==================== pytest 钩子函数 ====================

def pytest_addoption(parser):
    """
    添加自定义命令行参数
    
    注意：--browser, --headed, --slowmo 由 pytest-playwright 提供，不要重复定义！
    
    使用方法：
        pytest --env=prod
        pytest --base-url=https://example.com
    """
    # 环境选择（自定义参数）
    parser.addoption(
        "--env",
        action="store",
        default="test",
        choices=["dev", "test", "prod"],
        help="选择测试环境: dev, test, prod"
    )
    
    # 基础URL覆盖（自定义参数）
    parser.addoption(
        "--base-url-override",
        action="store",
        default=None,
        help="覆盖环境配置中的基础URL"
    )


def pytest_configure(config):
    """
    pytest 配置钩子
    
    在测试运行前执行，用于：
    1. 创建输出目录
    2. 配置 Allure 环境信息
    3. 注册自定义标记
    """
    logger.info("=" * 60)
    logger.info("Playwright 自动化测试框架 - 测试开始")
    logger.info("=" * 60)
    
    # 确保所有输出目录存在
    Settings.ensure_dirs()
    
    # 生成 Allure 环境信息文件
    AllureHelper.generate_environment_file()
    
    # 注册自定义标记
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "wip: 开发中的测试")
    config.addinivalue_line("markers", "login: 登录相关测试")
    config.addinivalue_line("markers", "search: 搜索相关测试")


def pytest_collection_modifyitems(session, config, items):
    """
    修改收集到的测试项
    
    用于：
    1. 按优先级排序测试
    2. 根据标记过滤测试
    """
    # 可以在这里添加测试排序逻辑
    pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    生成测试报告钩子
    
    在每个测试阶段（setup/call/teardown）后调用。
    用于捕获测试结果，以便在 fixture 中判断测试是否失败。
    """
    outcome = yield
    rep = outcome.get_result()
    
    # 存储每个阶段的结果到 item 对象
    setattr(item, f"rep_{rep.when}", rep)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    终端摘要钩子
    
    在测试运行结束后打印摘要信息。
    """
    logger.info("=" * 60)
    logger.info("测试运行完成")
    
    # 统计结果
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    error = len(terminalreporter.stats.get('error', []))
    
    logger.info(f"通过: {passed}, 失败: {failed}, 跳过: {skipped}, 错误: {error}")
    logger.info("=" * 60)


# ==================== 自定义 Fixtures ====================
# 注意：page, context, browser 等由 pytest-playwright 提供
# 我们只定义扩展的 fixtures

@pytest.fixture(scope="session")
def env_name(request) -> str:
    """
    获取环境名称
    
    Scope: session
    
    Returns:
        环境名称字符串
    """
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def env_config(env_name) -> EnvConfig:
    """
    获取环境配置
    
    Scope: session
    
    Args:
        env_name: 环境名称（从 fixture 注入）
    
    Returns:
        EnvConfig 实例
    
    使用方法：
        def test_something(env_config):
            base_url = env_config.base_url
            username = env_config.get("credentials.username")
    """
    logger.info(f"加载环境配置: {env_name}")
    return EnvConfig(env_name)


@pytest.fixture(scope="session")
def base_url(request, env_config) -> str:
    """
    获取基础URL
    
    优先使用命令行参数，否则使用环境配置。
    
    Scope: session
    
    Returns:
        基础URL字符串
    """
    # 命令行参数优先
    url = request.config.getoption("--base-url-override")
    if url:
        logger.info(f"使用命令行指定的 base_url: {url}")
        return url
    
    # 使用环境配置
    url = env_config.base_url
    logger.info(f"使用环境配置的 base_url: {url}")
    return url


@pytest.fixture(scope="function")
def screenshot_helper(page: Page) -> ScreenshotHelper:
    """
    获取截图助手实例
    
    Scope: function
    
    Args:
        page: 页面实例（由 pytest-playwright 提供）
    
    Returns:
        ScreenshotHelper 实例
    """
    return ScreenshotHelper(page)


@pytest.fixture(scope="function")
def console_logs(page: Page) -> Generator[ConsoleLogCollector, None, None]:
    """
    控制台日志收集器
    
    Scope: function
    
    自动收集浏览器控制台输出，便于调试。
    
    Args:
        page: 页面实例
    
    Yields:
        ConsoleLogCollector 实例
    
    使用方法：
        def test_something(page, console_logs):
            page.goto("https://example.com")
            # ... 测试操作 ...
            errors = console_logs.get_errors()
            assert len(errors) == 0, f"页面有控制台错误: {errors}"
    """
    collector = ConsoleLogCollector(page)
    yield collector


@pytest.fixture(scope="session")
def data_loader() -> DataLoader:
    """
    获取数据加载器实例
    
    Scope: session
    
    Returns:
        DataLoader 实例
    
    使用方法：
        def test_login(data_loader):
            login_data = data_loader.load_yaml("login_data.yaml")
            username = login_data["valid_credentials"]["username"]
    """
    return DataLoader()


@pytest.fixture(autouse=True)
def test_setup_teardown(request, page, screenshot_helper):
    """
    测试前后的自动设置和清理
    
    autouse=True 表示自动应用到所有测试。
    
    功能：
    1. 测试前：记录测试开始日志，设置超时
    2. 测试后：失败时自动截图
    
    Args:
        request: pytest 请求对象
        page: 页面实例（由 pytest-playwright 提供）
        screenshot_helper: 截图助手
    """
    test_name = request.node.name
    print(f"\n🚀 测试开始: {test_name}")
    
    # 设置页面默认超时
    page.set_default_timeout(Settings.DEFAULT_TIMEOUT)
    page.set_default_navigation_timeout(Settings.NAVIGATION_TIMEOUT)
    
    # 测试执行
    yield
    
    # 测试后处理
    # 检查测试是否失败
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        print(f"❌ 测试失败: {test_name}")
        
        # 失败时截图
        if Settings.SCREENSHOT_ON_FAILURE:
            try:
                screenshot_helper.capture_on_failure(test_name=test_name)
            except Exception as e:
                print(f"截图失败: {e}")
        
        # 保存页面源代码
        try:
            screenshot_helper.save_page_source(f"FAIL_{test_name}")
        except Exception:
            pass
    else:
        print(f"✅ 测试通过: {test_name}")


# ==================== 常用数据 Fixtures ====================

@pytest.fixture(scope="session")
def login_data(data_loader) -> dict:
    """
    加载登录测试数据
    
    Scope: session
    
    Returns:
        登录数据字典
    """
    return data_loader.load_yaml("login_data.yaml")


@pytest.fixture(scope="session")
def search_data(data_loader) -> dict:
    """
    加载搜索测试数据
    
    Scope: session
    
    Returns:
        搜索数据字典
    """
    return data_loader.load_yaml("search_data.yaml")


@pytest.fixture(scope="session")
def common_data(data_loader) -> dict:
    """
    加载通用测试数据
    
    Scope: session
    
    Returns:
        通用数据字典
    """
    return data_loader.load_yaml("common_data.yaml")


# ==================== Allure 报告 Fixtures ====================

@pytest.fixture(autouse=True)
def add_allure_environment_info(request, env_name, base_url):
    """
    为每个测试添加 Allure 环境信息
    
    autouse=True 自动应用。
    """
    # 添加环境信息到 Allure
    allure.dynamic.parameter("环境", env_name)
    allure.dynamic.parameter("基础URL", base_url)
    
    yield
