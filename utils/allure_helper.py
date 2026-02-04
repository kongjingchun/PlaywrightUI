# ========================================
# Allure 报告增强模块
# ========================================
# 提供 Allure 报告相关的辅助功能，包括：
# - 附件管理
# - 步骤记录
# - 环境信息
# - 自定义装饰器
# ========================================

import allure
from allure_commons.types import AttachmentType, Severity
from functools import wraps
from typing import Callable, Optional, Any
import json
from datetime import datetime
from pathlib import Path
from config.settings import Settings
from utils.logger import Logger


class AllureHelper:
    """
    Allure 报告辅助类
    
    提供各种 Allure 报告增强功能。
    
    使用方法：
        allure_helper = AllureHelper()
        
        # 附加文本信息
        allure_helper.attach_text("请求数据", json.dumps(data))
        
        # 附加 JSON
        allure_helper.attach_json("API响应", response_data)
        
        # 设置测试元数据
        allure_helper.set_test_metadata(
            severity=Severity.CRITICAL,
            story="用户登录",
            feature="认证模块"
        )
    """
    
    def __init__(self):
        """初始化 Allure 辅助类"""
        self.logger = Logger("AllureHelper")
    
    # ==================== 附件方法 ====================
    
    def attach_text(self, name: str, body: str) -> None:
        """
        附加文本内容到报告
        
        Args:
            name: 附件名称
            body: 文本内容
        
        使用方法：
            allure_helper.attach_text("SQL查询", "SELECT * FROM users")
        """
        allure.attach(
            body,
            name=name,
            attachment_type=AttachmentType.TEXT
        )
        self.logger.debug(f"已附加文本: {name}")
    
    def attach_json(self, name: str, data: Any) -> None:
        """
        附加 JSON 数据到报告
        
        Args:
            name: 附件名称
            data: 要序列化的数据（dict 或 list）
        
        使用方法：
            allure_helper.attach_json("API响应", {"status": "ok", "data": [...]})
        """
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        allure.attach(
            json_str,
            name=name,
            attachment_type=AttachmentType.JSON
        )
        self.logger.debug(f"已附加JSON: {name}")
    
    def attach_html(self, name: str, html_content: str) -> None:
        """
        附加 HTML 内容到报告
        
        Args:
            name: 附件名称
            html_content: HTML 内容
        """
        allure.attach(
            html_content,
            name=name,
            attachment_type=AttachmentType.HTML
        )
        self.logger.debug(f"已附加HTML: {name}")
    
    def attach_image(self, name: str, image_path: str) -> None:
        """
        附加图片到报告
        
        Args:
            name: 附件名称
            image_path: 图片文件路径
        """
        allure.attach.file(
            image_path,
            name=name,
            attachment_type=AttachmentType.PNG
        )
        self.logger.debug(f"已附加图片: {name}")
    
    def attach_video(self, name: str, video_path: str) -> None:
        """
        附加视频到报告
        
        Args:
            name: 附件名称
            video_path: 视频文件路径
        """
        # Allure 默认不直接支持视频，但可以作为文件附加
        allure.attach.file(
            video_path,
            name=name,
            attachment_type=AttachmentType.WEBM
        )
        self.logger.debug(f"已附加视频: {name}")
    
    # ==================== 测试元数据方法 ====================
    
    @staticmethod
    def set_severity(level: Severity) -> None:
        """
        设置测试严重程度
        
        Args:
            level: 严重程度级别
                   - BLOCKER: 阻塞
                   - CRITICAL: 严重
                   - NORMAL: 普通
                   - MINOR: 次要
                   - TRIVIAL: 轻微
        
        使用方法：
            AllureHelper.set_severity(Severity.CRITICAL)
        """
        allure.severity(level)
    
    @staticmethod
    def set_feature(feature_name: str) -> None:
        """
        设置功能模块名称
        
        Args:
            feature_name: 功能名称
        """
        allure.dynamic.feature(feature_name)
    
    @staticmethod
    def set_story(story_name: str) -> None:
        """
        设置用户故事名称
        
        Args:
            story_name: 故事名称
        """
        allure.dynamic.story(story_name)
    
    @staticmethod
    def set_title(title: str) -> None:
        """
        设置测试标题
        
        Args:
            title: 测试标题
        """
        allure.dynamic.title(title)
    
    @staticmethod
    def set_description(description: str) -> None:
        """
        设置测试描述
        
        Args:
            description: 测试描述（支持 Markdown 格式）
        """
        allure.dynamic.description(description)
    
    @staticmethod
    def add_link(url: str, name: str = None) -> None:
        """
        添加链接
        
        Args:
            url: 链接地址
            name: 链接显示名称
        """
        allure.dynamic.link(url, name=name)
    
    @staticmethod
    def add_issue(issue_id: str) -> None:
        """
        添加关联的问题/缺陷
        
        Args:
            issue_id: 问题ID
        """
        allure.dynamic.issue(issue_id)
    
    @staticmethod
    def add_test_case(test_case_id: str) -> None:
        """
        添加关联的测试用例
        
        Args:
            test_case_id: 测试用例ID
        """
        allure.dynamic.testcase(test_case_id)
    
    @staticmethod
    def add_tag(tag: str) -> None:
        """
        添加标签
        
        Args:
            tag: 标签名称
        """
        allure.dynamic.tag(tag)
    
    # ==================== 环境信息 ====================
    
    @staticmethod
    def generate_environment_file() -> None:
        """
        生成 Allure 环境信息文件
        
        在报告中显示测试环境信息。
        文件会生成在 UIreport/ 目录下。
        
        使用方法（在 conftest.py 中）:
            @pytest.fixture(scope="session", autouse=True)
            def setup_allure_env():
                AllureHelper.generate_environment_file()
        """
        from config.settings import Settings
        import os
        
        # 环境信息
        env_props = {
            "Browser": Settings.BROWSER_TYPE,
            "Headless": str(Settings.HEADLESS),
            "Environment": Settings.ENV,
            "Viewport": f"{Settings.VIEWPORT_WIDTH}x{Settings.VIEWPORT_HEIGHT}",
            "Base URL": os.getenv("BASE_URL", "N/A"),
            "Python": os.popen("python --version").read().strip(),
            "Playwright": "latest",
            "OS": os.name,
        }
        
        # 确保报告目录存在（UIreport 即 Allure 结果目录）
        allure_results_dir = Settings.REPORTS_DIR
        allure_results_dir.mkdir(parents=True, exist_ok=True)
        
        # 写入环境文件
        env_file = allure_results_dir / "environment.properties"
        with open(env_file, 'w', encoding='utf-8') as f:
            for key, value in env_props.items():
                f.write(f"{key}={value}\n")
        
        print(f"✓ Allure 环境信息已生成: {env_file}")


# ==================== 装饰器 ====================

def allure_step(step_name: str):
    """
    Allure 步骤装饰器
    
    为方法添加 Allure 步骤记录，支持参数替换。
    
    Args:
        step_name: 步骤名称，支持 {arg_name} 格式的参数替换
    
    使用方法：
        @allure_step("登录用户: {username}")
        def login(username, password):
            # 登录逻辑
            pass
        
        login("admin", "password")  # 步骤会显示为 "登录用户: admin"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数参数名
            import inspect
            sig = inspect.signature(func)
            params = sig.parameters
            
            # 构建参数字典
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 替换步骤名中的参数
            formatted_step = step_name
            for name, value in bound_args.arguments.items():
                formatted_step = formatted_step.replace(f"{{{name}}}", str(value))
            
            # 执行步骤
            with allure.step(formatted_step):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def allure_feature(feature_name: str):
    """
    功能模块装饰器
    
    为测试类或测试方法添加功能分类。
    
    使用方法：
        @allure_feature("用户管理")
        class TestUserManagement:
            pass
    """
    return allure.feature(feature_name)


def allure_story(story_name: str):
    """
    用户故事装饰器
    
    使用方法：
        @allure_story("用户登录")
        def test_login():
            pass
    """
    return allure.story(story_name)


def allure_severity(level: str):
    """
    严重程度装饰器
    
    Args:
        level: 严重程度，可选值：blocker/critical/normal/minor/trivial
    
    使用方法：
        @allure_severity("critical")
        def test_important_feature():
            pass
    """
    severity_map = {
        "blocker": Severity.BLOCKER,
        "critical": Severity.CRITICAL,
        "normal": Severity.NORMAL,
        "minor": Severity.MINOR,
        "trivial": Severity.TRIVIAL,
    }
    return allure.severity(severity_map.get(level.lower(), Severity.NORMAL))


def allure_title(title: str):
    """
    测试标题装饰器
    
    使用方法：
        @allure_title("验证用户使用正确密码登录成功")
        def test_login_success():
            pass
    """
    return allure.title(title)


def allure_description(description: str):
    """
    测试描述装饰器
    
    使用方法：
        @allure_description('''
        ## 测试目标
        验证登录功能正常工作
        
        ## 前置条件
        - 用户已注册
        - 账号未被锁定
        ''')
        def test_login():
            pass
    """
    return allure.description(description)


def allure_link(url: str, name: Optional[str] = None):
    """
    链接装饰器
    
    使用方法：
        @allure_link("https://jira.example.com/TEST-123", "JIRA")
        def test_something():
            pass
    """
    return allure.link(url, name=name)


def allure_issue(issue_id: str):
    """
    问题关联装饰器
    
    使用方法：
        @allure_issue("BUG-456")
        def test_bug_fix():
            pass
    """
    return allure.issue(issue_id)
