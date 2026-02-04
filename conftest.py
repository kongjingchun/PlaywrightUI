# ========================================
# 根级 conftest.py - pytest 全局配置
# ========================================
# 该文件是 pytest 的全局配置文件，位于项目根目录。
# 包含所有测试共享的 fixtures 和钩子函数。
#
# 主要功能：
# 1. 扩展的命令行参数（环境切换等）
# 2. 失败截图和日志记录
# 3. Allure 报告集成
# 4. 测试数据加载
# 5. 测试进度统计和汇总报告
# ========================================

import pytest
import os
import shutil
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
from utils.dingtalk_notification import send_dingtalk_report
from common.process_file import ProcessFile


# ==================== 全局实例 ====================
logger = Logger("conftest")
process = ProcessFile()
_report_printed = False  # 防止报告重复打印


# ==================== pytest 钩子函数 ====================

def pytest_addoption(parser):
    """
    添加自定义命令行参数
    
    注意：--browser, --headed, --slowmo 由 pytest-playwright 提供
    
    使用方法：
        pytest --env=prod
        pytest --base-url-override=https://example.com
    """
    # 环境选择
    parser.addoption(
        "--env",
        action="store",
        default="prod",
        choices=["local", "dev", "test", "prod"],
        help="选择测试环境: local, dev, test, prod"
    )
    
    # 基础URL覆盖
    parser.addoption(
        "--base-url-override",
        action="store",
        default=None,
        help="覆盖环境配置中的基础URL"
    )


def pytest_configure(config):
    """
    pytest 配置钩子（测试运行前执行）
    
    功能：
    1. 创建输出目录
    2. 配置 Allure 环境信息
    3. 注册自定义标记
    """
    # 检查是否只是收集测试用例
    if hasattr(config, 'option') and hasattr(config.option, 'collectonly'):
        if config.option.collectonly:
            return
    
    logger.info("=" * 80)
    logger.info(" " * 20 + "🚀 Playwright 自动化测试框架 🚀" + " " * 20)
    logger.info("=" * 80)
    
    # 确保所有输出目录存在
    Settings.ensure_dirs()
    
    # 清理并重建报告目录
    reports_dir = Settings.PROJECT_ROOT / "reports"
    if reports_dir.exists():
        try:
            shutil.rmtree(reports_dir)
            logger.info(f"已清理报告目录: {reports_dir}")
        except Exception as e:
            logger.warning(f"清理报告目录失败: {e}")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成 Allure 环境信息文件
    AllureHelper.generate_environment_file()
    
    # 注册自定义标记
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "wip: 开发中的测试")
    config.addinivalue_line("markers", "login: 登录相关测试")
    config.addinivalue_line("markers", "search: 搜索相关测试")
    config.addinivalue_line("markers", "skip_local: 本地环境跳过")
    config.addinivalue_line("markers", "skip_remote: 远程环境跳过")
    config.addinivalue_line("markers", "run(order): 指定用例执行顺序")


def pytest_collection_modifyitems(session, config, items):
    """
    修改收集到的测试项
    
    功能：
    1. 按 order 全局排序
    2. 根据环境标记跳过测试
    """
    # 按 order 排序
    def get_order_key(item):
        run_marker = item.get_closest_marker("run")
        order = 999999
        if run_marker and "order" in run_marker.kwargs:
            try:
                order = int(run_marker.kwargs["order"])
            except (TypeError, ValueError):
                pass
        return (order, item.nodeid)
    
    items.sort(key=get_order_key)


def pytest_collection_finish(session):
    """
    pytest 收集完测试用例后执行
    
    初始化测试进度（只在主进程中执行）
    """
    if not hasattr(session, 'items') or len(session.items) == 0:
        return
    
    # 只在主进程中初始化进度
    if not hasattr(session.config, 'workerinput'):
        total = len(session.items)
        process.reset_all()
        process.init_process(total)
        logger.info(f"收集到 {total} 个测试用例")


def pytest_runtest_setup(item):
    """测试用例执行前调用"""
    # 获取测试名称（优先使用 docstring）
    if item.function.__doc__:
        test_name = item.function.__doc__.strip().split('\n')[0]
    else:
        test_name = item.name
    
    logger.info("=" * 80)
    logger.info(f"{'=' * 20} 开始执行: {test_name} {'=' * 20}")
    logger.info("=" * 80)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    生成测试报告钩子
    
    功能：
    1. 捕获测试结果
    2. 失败时自动截图
    3. 记录测试进度
    """
    outcome = yield
    rep = outcome.get_result()
    
    # 存储每个阶段的结果
    setattr(item, f"rep_{rep.when}", rep)
    
    # 将测试函数的文档字符串添加到报告
    rep.description = str(item.function.__doc__) if item.function.__doc__ else item.name
    
    # 测试执行阶段处理
    if rep.when == "call":
        # 获取测试名称
        if item.function.__doc__:
            test_name = item.function.__doc__.strip().split('\n')[0]
        else:
            test_name = item.name
        
        if rep.failed:
            logger.info("=" * 80)
            logger.info(f"{'=' * 20} ❌ 执行失败: {test_name} {'=' * 20}")
            logger.info("=" * 80)
            
            # 失败时截图
            try:
                page = item._request.getfixturevalue('page') if hasattr(item, '_request') else None
                if page:
                    screenshot_helper = ScreenshotHelper(page)
                    screenshot_helper.capture_on_failure(test_name=test_name)
            except Exception as e:
                logger.warning(f"失败截图失败: {e}")
            
            # 记录失败
            process.update_fail()
            process.record_failed_testcase(test_name)
            
        elif rep.passed:
            logger.info("=" * 80)
            logger.info(f"{'=' * 20} ✅ 执行成功: {test_name} {'=' * 20}")
            logger.info("=" * 80)
            
            # 记录成功
            process.update_success()
            process.record_success_testcase(test_name)
    
    # 跳过的用例处理
    elif rep.when == "setup" and rep.skipped:
        if item.function.__doc__:
            test_name = item.function.__doc__.strip().split('\n')[0]
        else:
            test_name = item.name
        
        process.update_skip()
        process.record_skipped_testcase(test_name)


def pytest_sessionfinish(session, exitstatus):
    """
    pytest 会话结束时执行
    
    记录测试结束时间（汇总报告在 pytest_terminal_summary 中生成）
    """
    # 只在主进程中执行
    if hasattr(session.config, 'workerinput'):
        return
    
    # 检查是否只是收集测试
    try:
        if hasattr(session.config, 'option') and hasattr(session.config.option, 'collectonly'):
            if session.config.option.collectonly:
                return
    except Exception:
        pass
    
    # 记录结束时间
    process.write_end_time()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    终端摘要钩子 - 生成测试执行结果汇总报告
    """
    global _report_printed
    
    # 防止重复打印
    if _report_printed:
        return
    _report_printed = True
    
    # 只在主进程中执行
    if hasattr(config, 'workerinput'):
        return
    
    # 获取测试结果
    total, success, fail, skip, start_time = process.get_result()
    duration = process.get_duration()
    executed = success + fail
    
    # 计算成功率
    if executed > 0:
        success_rate = (success / executed) * 100
        fail_rate = (fail / executed) * 100
    else:
        success_rate = 0.0
        fail_rate = 0.0
    
    # 生成汇总报告行
    report_lines = [
        "",
        "=" * 80,
        "=" * 80,
        " " * 20 + "📊 测试执行结果汇总报告 📊" + " " * 20,
        "=" * 80,
        "",
        " " * 25 + "【总体统计】" + " " * 25,
        "-" * 80,
        f"  测试用例总数:     {total:>6} 个",
        f"  实际执行用例:     {executed:>6} 个",
        f"  跳过用例数:       {skip:>6} 个",
        f"  执行耗时:        {duration:>15}",
        "-" * 80,
        "",
        " " * 25 + "【执行结果】" + " " * 25,
        "-" * 80,
        f"  ✅ 执行成功:      {success:>6} 个  |  成功率: {success_rate:>6.2f}%",
        f"  ❌ 执行失败:      {fail:>6} 个  |  失败率: {fail_rate:>6.2f}%",
        "-" * 80,
        "",
    ]
    
    # 成功用例列表
    success_testcases = process.get_success_testcases()
    if success_testcases:
        report_lines.append(" " * 25 + "【执行成功的用例】" + " " * 25)
        report_lines.append("-" * 80)
        for idx, name in enumerate(reversed(success_testcases), 1):
            display_name = name.strip().split('\n')[0] if name else "未知用例"
            report_lines.append(f"  ✅ {idx:>3}. {display_name}")
        report_lines.append("-" * 80)
        report_lines.append("")
    
    # 失败用例列表
    failed_testcases = process.get_failed_testcases()
    if failed_testcases:
        report_lines.append(" " * 25 + "【执行失败的用例】" + " " * 25)
        report_lines.append("-" * 80)
        for idx, name in enumerate(reversed(failed_testcases), 1):
            display_name = name.strip().split('\n')[0] if name else "未知用例"
            report_lines.append(f"  ❌ {idx:>3}. {display_name}")
        report_lines.append("-" * 80)
        report_lines.append("")
    
    # 跳过用例列表
    skipped_testcases = process.get_skipped_testcases()
    if skipped_testcases:
        report_lines.append(" " * 25 + "【跳过的用例】" + " " * 25)
        report_lines.append("-" * 80)
        for idx, name in enumerate(reversed(skipped_testcases), 1):
            display_name = name.strip().split('\n')[0] if name else "未知用例"
            report_lines.append(f"  ⏭️  {idx:>3}. {display_name}")
        report_lines.append("-" * 80)
        report_lines.append("")
    
    # 最终状态
    report_lines.append(" " * 25 + "【最终状态】" + " " * 25)
    report_lines.append("-" * 80)
    if fail == 0 and executed > 0:
        report_lines.append("  🎉 所有测试用例执行成功！")
    elif fail > 0:
        report_lines.append(f"  ⚠️  有 {fail} 个测试用例执行失败，请检查失败详情")
    elif executed == 0:
        report_lines.append("  ℹ️  没有实际执行的测试用例")
    report_lines.append("-" * 80)
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 输出到控制台
    for line in report_lines:
        print(line)
    
    # 写入日志文件
    from utils.logger import _get_log_file_path
    try:
        log_file = _get_log_file_path()
        with open(log_file, 'a', encoding='utf-8') as f:
            for line in report_lines:
                f.write(line + "\n")
    except Exception:
        pass  # 写入失败不影响测试
    
    # 发送钉钉通知（如果配置启用）
    try:
        env_name_value = config.getoption("--env")
        env_cfg = EnvConfig(env_name_value)
        
        # 获取钉钉配置
        dingtalk_config = env_cfg.get("dingtalk", {})
        if dingtalk_config.get("enabled", False):
            webhook = dingtalk_config.get("webhook", "")
            secret = dingtalk_config.get("secret", "")
            
            if webhook:
                logger.info("📤 开始发送钉钉通知...")
                # 准备失败用例列表
                failed_list = [name.strip().split('\n')[0] for name in failed_testcases] if failed_testcases else []
                
                # 发送通知
                success = send_dingtalk_report(
                    webhook=webhook,
                    secret=secret,
                    total=total,
                    passed=success,
                    failed=fail,
                    skipped=skip,
                    duration=duration,
                    failed_cases=failed_list,
                    environment=env_name_value
                )
                
                if success:
                    logger.info("✅ 钉钉通知发送成功")
                else:
                    logger.warning("⚠️ 钉钉通知发送失败")
            else:
                logger.info("ℹ️ 钉钉通知已启用但未配置 webhook，跳过发送")
    except Exception as e:
        logger.warning(f"⚠️ 发送钉钉通知时出错: {e}")
        # 不影响测试执行，继续


# ==================== 自定义 Fixtures ====================

@pytest.fixture(scope="session")
def env_name(request) -> str:
    """获取环境名称"""
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def env_config(env_name) -> EnvConfig:
    """获取环境配置"""
    logger.info(f"加载环境配置: {env_name}")
    return EnvConfig(env_name)


@pytest.fixture(scope="session")
def base_url(request, env_config) -> str:
    """获取基础URL（命令行参数优先）"""
    url = request.config.getoption("--base-url-override")
    if url:
        logger.info(f"使用命令行指定的 base_url: {url}")
        return url
    
    url = env_config.base_url
    logger.info(f"使用环境配置的 base_url: {url}")
    return url


@pytest.fixture(scope="function")
def screenshot_helper(page: Page) -> ScreenshotHelper:
    """获取截图助手实例"""
    return ScreenshotHelper(page)


@pytest.fixture(scope="function")
def console_logs(page: Page) -> Generator[ConsoleLogCollector, None, None]:
    """控制台日志收集器"""
    collector = ConsoleLogCollector(page)
    yield collector


@pytest.fixture(scope="session")
def data_loader() -> DataLoader:
    """获取数据加载器实例"""
    return DataLoader()


@pytest.fixture(scope="session")
def mysql_helper(env_config):
    """
    获取 MySQL 数据库连接实例（如果启用）
    
    使用示例：
        def test_user_data(mysql_helper):
            if mysql_helper:
                users = mysql_helper.query("SELECT * FROM users")
    """
    from utils.mysql_helper import MySQLHelper
    
    mysql_config = env_config.get("mysql", {})
    if not mysql_config.get("enabled", False):
        logger.info("MySQL 未启用，跳过连接")
        yield None
        return
    
    # 创建连接
    db = MySQLHelper(
        host=mysql_config.get("host", "localhost"),
        port=mysql_config.get("port", 3306),
        user=mysql_config.get("user", "root"),
        password=mysql_config.get("password", ""),
        database=mysql_config.get("database", ""),
        charset=mysql_config.get("charset", "utf8mb4")
    )
    
    # 连接数据库
    if db.connect():
        yield db
    else:
        yield None
    
    # 清理
    db.close()


@pytest.fixture(scope="session")
def redis_helper(env_config):
    """
    获取 Redis 连接实例（如果启用）
    
    使用示例：
        def test_cache(redis_helper):
            if redis_helper:
                redis_helper.set("test_key", "test_value")
    """
    from utils.redis_helper import RedisHelper
    
    redis_config = env_config.get("redis", {})
    if not redis_config.get("enabled", False):
        logger.info("Redis 未启用，跳过连接")
        yield None
        return
    
    # 创建连接
    redis_client = RedisHelper(
        host=redis_config.get("host", "localhost"),
        port=redis_config.get("port", 6379),
        db=redis_config.get("db", 0),
        password=redis_config.get("password", None)
    )
    
    # 连接 Redis
    if redis_client.connect():
        yield redis_client
    else:
        yield None
    
    # 清理
    redis_client.close()


@pytest.fixture(autouse=True)
def test_setup_teardown(request, page, screenshot_helper):
    """
    测试前后的自动设置和清理
    
    功能：
    1. 测试前：设置超时
    2. 测试后：失败时自动截图
    """
    test_name = request.node.name
    
    # 设置页面默认超时
    page.set_default_timeout(Settings.DEFAULT_TIMEOUT)
    page.set_default_navigation_timeout(Settings.NAVIGATION_TIMEOUT)
    
    yield
    
    # 测试后处理已在 pytest_runtest_makereport 中完成


# ==================== 数据 Fixtures ====================

@pytest.fixture(scope="session")
def login_data(data_loader) -> dict:
    """加载登录测试数据"""
    return data_loader.load_yaml("login_data.yaml")


@pytest.fixture(scope="session")
def search_data(data_loader) -> dict:
    """加载搜索测试数据"""
    return data_loader.load_yaml("search_data.yaml")


@pytest.fixture(scope="session")
def common_data(data_loader) -> dict:
    """加载通用测试数据"""
    return data_loader.load_yaml("common_data.yaml")


# ==================== Allure 报告 Fixtures ====================

@pytest.fixture(autouse=True)
def add_allure_environment_info(request, env_name, base_url):
    """为每个测试添加 Allure 环境信息"""
    allure.dynamic.parameter("环境", env_name)
    allure.dynamic.parameter("基础URL", base_url)
    yield
