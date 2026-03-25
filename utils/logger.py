# ========================================
# 日志管理模块
# ========================================
# 提供统一的日志管理功能，支持：
# - 分级日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
# - 彩色控制台输出
# - 文件日志记录（仅在 pytest 运行时生成）
# - 每次测试执行生成独立的日志文件
# 
# 注意：日志文件只在 pytest 运行环境中创建，避免编辑器保存时生成文件
# ========================================

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# 尝试导入 colorlog，如果不可用则使用标准 logging
try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

from config.settings import Settings


class _ConsoleStreamHandler(logging.StreamHandler):
    """
    控制台输出用 Handler。

    pytest-xdist 在 worker 子进程里跑用例时，往 sys.stdout 打日志经常无法实时出现在
    主进程终端里，``-s`` 也往往无效（捕获/管道与 execnet 转发限制）。
    此时改用 sys.stderr 并在每条记录后 flush，主终端通常能稳定看到与 logs 一致的内容。
    非 worker（单进程或未启用 xdist）仍用 stdout，行为与历史一致。
    """

    def __init__(self, stream, flush_each: bool) -> None:
        super().__init__(stream)
        self._flush_each = flush_each

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        if self._flush_each:
            try:
                self.flush()
            except Exception:
                pass


def _xdist_worker_console_target() -> tuple:
    """
    Returns:
        (stream, flush_each): 控制台写入目标与是否每条后 flush
    """
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return sys.stderr, True
    return sys.stdout, False


# ==================== 全局日志文件路径 ====================
# 每次测试运行使用同一个日志文件（通过时间戳区分不同运行）
_LOG_FILE_PATH: Optional[Path] = None
_LOG_SESSION_ID: Optional[str] = None


def _is_pytest_running() -> bool:
    """
    检测当前是否在 pytest 运行环境中
    
    Returns:
        True 如果在 pytest 运行中，否则 False
    """
    # pytest 运行时会设置 PYTEST_CURRENT_TEST 环境变量
    return 'PYTEST_CURRENT_TEST' in os.environ


def _get_log_file_path() -> Path:
    """
    获取当前测试运行的日志文件路径
    
    每次测试运行（pytest 启动）生成一个独立的日志文件。
    文件名格式：test_YYYYMMDD_HHMMSS.log
    
    只在 pytest 运行环境中才创建日志文件，避免每次保存文件时都生成日志。
    
    Returns:
        日志文件路径
    """
    global _LOG_FILE_PATH, _LOG_SESSION_ID
    
    if _LOG_FILE_PATH is None and _is_pytest_running():
        # 确保日志目录存在
        Settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 生成带时间戳的文件名（精确到秒）
        _LOG_SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
        _LOG_FILE_PATH = Settings.LOGS_DIR / f"test_{_LOG_SESSION_ID}.log"
        
        # 在日志文件开头写入分隔信息
        with open(_LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"测试执行开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"日志文件: {_LOG_FILE_PATH}\n")
            f.write("=" * 80 + "\n\n")
    
    return _LOG_FILE_PATH


def get_log_session_id() -> str:
    """
    获取当前日志会话ID
    
    Returns:
        会话ID字符串（时间戳格式）
    """
    global _LOG_SESSION_ID
    if _LOG_SESSION_ID is None:
        _get_log_file_path()  # 初始化
    return _LOG_SESSION_ID


class Logger:
    """
    日志管理类
    
    提供统一的日志记录功能，支持控制台彩色输出和文件记录。
    每次测试运行会生成一个独立的日志文件。
    
    使用方法：
        # 创建日志实例
        logger = Logger("TestLogin")
        
        # 记录不同级别的日志
        logger.debug("调试信息")
        logger.info("一般信息")
        logger.warning("警告信息")
        logger.error("错误信息")
        logger.critical("严重错误")
    
    日志级别说明：
        - DEBUG: 详细的调试信息，通常只在开发时使用
        - INFO: 确认程序按预期运行的信息
        - WARNING: 表明发生了意外情况，但程序仍能继续运行
        - ERROR: 由于更严重的问题，程序无法执行某些功能
        - CRITICAL: 严重错误，可能导致程序无法继续运行
    """
    
    # 类级别的日志实例缓存，避免重复创建
    _loggers = {}
    
    # 文件处理器缓存（所有 logger 共享同一个文件处理器）
    _file_handler: Optional[logging.Handler] = None
    
    # 日志格式配置
    # 控制台格式（带颜色）
    CONSOLE_FORMAT = "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s%(reset)s"
    # 文件格式（纯文本）
    FILE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    # 时间格式
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # 颜色配置
    LOG_COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
    
    def __init__(self, name: str, level: int = logging.DEBUG):
        """
        初始化日志实例
        
        Args:
            name: 日志名称，通常使用类名或模块名
            level: 日志级别，默认 DEBUG
        """
        self.name = name
        self.level = level
        
        # 如果已经创建过同名日志实例，直接复用
        if name in Logger._loggers:
            self._logger = Logger._loggers[name]
        else:
            self._logger = self._create_logger()
            Logger._loggers[name] = self._logger
    
    def _create_logger(self) -> logging.Logger:
        """
        创建并配置日志实例
        
        Returns:
            配置好的 Logger 实例
        """
        # 创建日志实例
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        
        # 防止重复添加处理器
        if logger.handlers:
            return logger
        
        # 添加控制台处理器
        console_handler = self._create_console_handler()
        logger.addHandler(console_handler)
        
        # 添加文件处理器（所有 logger 共享）
        file_handler = self._get_shared_file_handler()
        if file_handler:
            logger.addHandler(file_handler)
        
        return logger
    
    def _create_console_handler(self) -> logging.Handler:
        """
        创建控制台日志处理器
        
        如果 colorlog 可用，使用彩色输出；否则使用纯文本。

        Returns:
            配置好的控制台处理器
        """
        stream, flush_each = _xdist_worker_console_target()
        handler = _ConsoleStreamHandler(stream, flush_each)
        handler.setLevel(logging.DEBUG)
        
        if HAS_COLORLOG:
            # 使用彩色格式
            formatter = colorlog.ColoredFormatter(
                self.CONSOLE_FORMAT,
                datefmt=self.DATE_FORMAT,
                log_colors=self.LOG_COLORS
            )
        else:
            # 使用标准格式
            formatter = logging.Formatter(
                self.FILE_FORMAT,
                datefmt=self.DATE_FORMAT
            )
        
        handler.setFormatter(formatter)
        return handler
    
    @classmethod
    def _get_shared_file_handler(cls) -> Optional[logging.Handler]:
        """
        获取共享的文件处理器
        
        所有 Logger 实例共享同一个文件处理器，确保写入同一个日志文件。
        只在 pytest 运行环境中创建文件处理器。
        
        Returns:
            配置好的文件处理器，如果不在 pytest 环境或创建失败则返回 None
        """
        # 如果已经创建过，直接返回
        if cls._file_handler is not None:
            return cls._file_handler
        
        # 如果不在 pytest 运行环境中，不创建文件处理器
        if not _is_pytest_running():
            return None
        
        try:
            # 获取日志文件路径
            log_file = _get_log_file_path()
            
            # 如果没有获取到日志文件路径（不在 pytest 环境），返回 None
            if log_file is None:
                return None
            
            # 创建文件处理器
            cls._file_handler = logging.FileHandler(
                log_file,
                encoding='utf-8',
                mode='a'  # 追加模式
            )
            cls._file_handler.setLevel(logging.DEBUG)
            
            # 设置格式
            formatter = logging.Formatter(
                cls.FILE_FORMAT,
                datefmt=cls.DATE_FORMAT
            )
            cls._file_handler.setFormatter(formatter)
            
            return cls._file_handler
            
        except Exception as e:
            print(f"警告：无法创建日志文件处理器: {e}")
            return None
    
    # ==================== 日志记录方法 ====================
    
    def debug(self, message: str) -> None:
        """
        记录 DEBUG 级别日志
        
        用于记录详细的调试信息，帮助开发人员理解程序执行流程。
        
        Args:
            message: 日志消息
        """
        self._logger.debug(message)
    
    def info(self, message: str) -> None:
        """
        记录 INFO 级别日志
        
        用于记录程序正常运行的关键信息。
        
        Args:
            message: 日志消息
        """
        self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """
        记录 WARNING 级别日志
        
        用于记录可能的问题，但不影响程序继续运行。
        
        Args:
            message: 日志消息
        """
        self._logger.warning(message)
    
    def error(self, message: str) -> None:
        """
        记录 ERROR 级别日志
        
        用于记录错误信息，表明程序遇到了问题。
        
        Args:
            message: 日志消息
        """
        self._logger.error(message)
    
    def critical(self, message: str) -> None:
        """
        记录 CRITICAL 级别日志
        
        用于记录严重错误，可能导致程序无法继续。
        
        Args:
            message: 日志消息
        """
        self._logger.critical(message)
    
    def exception(self, message: str) -> None:
        """
        记录异常信息（包含堆栈跟踪）
        
        在 except 块中使用，会自动记录异常堆栈信息。
        
        Args:
            message: 日志消息
        
        使用方法：
            try:
                risky_operation()
            except Exception:
                logger.exception("操作失败")
        """
        self._logger.exception(message)
    
    # ==================== 便捷方法 ====================
    
    def step(self, step_name: str) -> None:
        """
        记录测试步骤
        
        用于标记测试用例中的关键步骤，便于追踪执行流程。
        
        Args:
            step_name: 步骤名称
        
        使用方法：
            logger.step("开始登录")
            logger.step("输入用户名和密码")
            logger.step("点击登录按钮")
        """
        self.info(f"📍 步骤: {step_name}")
    
    def test_start(self, test_name: str) -> None:
        """
        记录测试用例开始
        
        Args:
            test_name: 测试用例名称
        """
        self.info(f"🚀 测试开始: {test_name}")
        self.info("=" * 50)
    
    def test_end(self, test_name: str, passed: bool = True) -> None:
        """
        记录测试用例结束
        
        Args:
            test_name: 测试用例名称
            passed: 是否通过
        """
        self.info("=" * 50)
        if passed:
            self.info(f"✅ 测试通过: {test_name}")
        else:
            self.error(f"❌ 测试失败: {test_name}")


# ==================== 模块级便捷函数 ====================

def get_logger(name: str = "PlaywrightTest") -> Logger:
    """
    获取日志实例的便捷函数
    
    Args:
        name: 日志名称
    
    Returns:
        Logger 实例
    
    使用方法：
        from utils.logger import get_logger
        
        logger = get_logger("MyTest")
        logger.info("这是一条日志")
    """
    return Logger(name)


def get_current_log_file() -> Optional[Path]:
    """
    获取当前测试运行的日志文件路径
    
    Returns:
        日志文件路径，如果未初始化则返回 None
    """
    global _LOG_FILE_PATH
    return _LOG_FILE_PATH


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试日志功能
    logger = Logger("TestLogger")
    
    print(f"日志文件: {get_current_log_file()}")
    
    logger.debug("这是一条 DEBUG 日志")
    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")
    logger.critical("这是一条 CRITICAL 日志")
    
    logger.step("测试步骤记录")
    logger.test_start("示例测试")
    logger.test_end("示例测试", passed=True)
    
    print(f"\n日志已保存到: {get_current_log_file()}")
