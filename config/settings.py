# ========================================
# 全局配置管理模块
# ========================================
# 该模块定义了框架的所有全局配置项，包括：
# - 浏览器配置（类型、无头模式、视口大小等）
# - 超时配置（默认超时、导航超时等）
# - 路径配置（报告、日志、截图等目录）
# - 运行配置（并行数、重试次数等）
# ========================================

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 环境变量文件
# .env 文件用于存储敏感信息（如密码、API密钥）和环境特定配置
load_dotenv()

# ==================== 默认环境（修改此处即可同步 conftest 和 env_config） ====================
# 支持 local、dev、test、prod
DEFAULT_ENV = "prod"


class Settings:
    """
    全局配置类

    使用方法：
        from config.settings import Settings

        # 获取浏览器类型
        browser = Settings.BROWSER_TYPE

        # 获取项目根目录
        root = Settings.PROJECT_ROOT

    配置优先级：
        1. 环境变量（最高优先级）
        2. .env 文件
        3. 默认值（最低优先级）
    """
    # ==================== 浏览器配置 ====================
    # HEADLESS: 默认无头/有头模式（可被命令行 --headed 覆盖）
    # True = 无界面运行（适合 CI/CD），False = 有界面运行（适合调试）
    # 修改此处或 .env 的 HEADLESS 即可改默认；执行时加 --headed 可临时覆盖为有头
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

    # BROWSER_TYPE / SLOW_MO: 可由命令行 --browser、--slowmo 覆盖
    BROWSER_TYPE = os.getenv("BROWSER", "chromium")
    SLOW_MO = int(os.getenv("SLOW_MO", "0"))

    # 视口（浏览器窗口）大小配置
    VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "1080"))

    # ==================== 环境配置 ====================
    # ENV: 当前运行环境（从环境变量读取，未设置时使用 DEFAULT_ENV）
    ENV = os.getenv("ENV", DEFAULT_ENV)

    # ==================== 超时配置（单位：毫秒） ====================
    # DEFAULT_TIMEOUT: 默认操作超时时间
    # 用于等待元素出现、点击、输入等操作
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10000"))

    # NAVIGATION_TIMEOUT: 页面导航超时时间
    # 用于 page.goto()、page.reload() 等导航操作
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "10000"))

    # EXPECT_TIMEOUT: 断言等待超时时间
    # 用于 expect() 断言等待条件满足
    EXPECT_TIMEOUT = int(os.getenv("EXPECT_TIMEOUT", "5000"))

    # ==================== 项目路径配置 ====================
    # PROJECT_ROOT: 项目根目录的绝对路径
    # 使用 Path(__file__).parent.parent 获取当前文件的上两级目录
    PROJECT_ROOT = Path(__file__).parent.parent

    # 各种输出目录的路径配置
    REPORTS_DIR = PROJECT_ROOT / "UIreport"         # Allure 报告目录（统一使用 UIreport）
    LOGS_DIR = PROJECT_ROOT / "logs"                # 日志文件目录
    SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"  # 失败截图目录
    VIDEOS_DIR = PROJECT_ROOT / "videos"            # 录屏文件目录
    HAR_DIR = PROJECT_ROOT / "har"                  # HAR网络日志目录
    DATA_DIR = PROJECT_ROOT / "data"                # 测试数据目录

    

    # ==================== 运行配置 ====================
    # 注意：实际由 pytest 命令行控制：-n 1（pytest-xdist）、--reruns 1（pytest-rerunfailures）
    # 以下仅作参考，可在 .env 中设置后由脚本读取
    WORKERS = int(os.getenv("WORKERS", "1"))
    RETRIES = int(os.getenv("RETRIES", "1"))

    # ==================== 录制配置 ====================
    # RECORD_VIDEO: 是否录制测试视频
    # 建议仅在失败时录制以节省空间
    RECORD_VIDEO = os.getenv("RECORD_VIDEO", "false").lower() == "true"

    # RECORD_HAR: 是否记录网络请求（HAR格式）
    # HAR文件可用于分析网络问题
    RECORD_HAR = os.getenv("RECORD_HAR", "false").lower() == "true"

    # SCREENSHOT_ON_FAILURE: 失败时是否自动截图
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"

    @classmethod
    def ensure_dirs(cls):
        """
        确保所有输出目录存在

        在测试开始前调用此方法，自动创建所需的目录结构。
        如果目录已存在，不会报错。

        使用方法：
            Settings.ensure_dirs()
        """
        dirs = [
            cls.REPORTS_DIR,
            cls.LOGS_DIR,
            cls.SCREENSHOTS_DIR,
            cls.VIDEOS_DIR,
            cls.HAR_DIR,
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_browser_launch_args(cls) -> dict:
        """
        获取浏览器启动参数

        返回用于 browser.launch() 的参数字典。

        Returns:
            dict: 包含 headless、slow_mo 等启动参数的字典

        使用方法：
            args = Settings.get_browser_launch_args()
            browser = playwright.chromium.launch(**args)
        """
        return {
            "headless": cls.HEADLESS,
            "slow_mo": cls.SLOW_MO,
        }

    @classmethod
    def get_context_args(cls) -> dict:
        """
        获取浏览器上下文参数

        返回用于 browser.new_context() 的参数字典。
        包含视口大小、录制配置等。

        Returns:
            dict: 包含 viewport、record_video_dir 等上下文参数的字典

        使用方法：
            args = Settings.get_context_args()
            context = browser.new_context(**args)
        """
        args = {
            "viewport": {
                "width": cls.VIEWPORT_WIDTH,
                "height": cls.VIEWPORT_HEIGHT
            },
        }

        # 如果启用了视频录制，添加录制目录配置
        if cls.RECORD_VIDEO:
            args["record_video_dir"] = str(cls.VIDEOS_DIR)
            args["record_video_size"] = {
                "width": cls.VIEWPORT_WIDTH,
                "height": cls.VIEWPORT_HEIGHT
            }

        # 如果启用了HAR录制，添加HAR路径配置
        if cls.RECORD_HAR:
            args["record_har_path"] = str(cls.HAR_DIR / "network.har")

        return args
