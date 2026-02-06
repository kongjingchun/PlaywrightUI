# ========================================
# 环境配置加载模块
# ========================================
# 该模块负责根据当前环境（dev/test/prod）加载对应的配置文件。
# 配置文件使用 YAML 格式，存放在 config/environments/ 目录下。
# 
# 功能特点：
# - 支持多环境切换（开发、测试、生产）
# - 从 YAML 文件读取环境特定配置
# - 支持动态获取配置项
# ========================================

import os
import yaml
from pathlib import Path
from typing import Any, Optional

from config.settings import DEFAULT_ENV


class EnvConfig:
    """
    环境配置加载器
    
    根据 ENV 环境变量加载对应的配置文件。
    
    使用方法：
        from config.env_config import EnvConfig
        
        # 创建配置实例（自动加载当前环境配置）
        config = EnvConfig()
        
        # 获取配置项
        base_url = config.get("base_url")
        username = config.get("credentials.username")  # 支持嵌套获取
        
        # 获取配置项，带默认值
        timeout = config.get("timeout", default=30000)
    
    环境配置文件位置：
        config/environments/dev.yaml   - 开发环境
        config/environments/test.yaml  - 测试环境
        config/environments/prod.yaml  - 生产环境
    """
    
    # 配置文件目录
    _CONFIG_DIR = Path(__file__).parent / "environments"
    
    def __init__(self, env: Optional[str] = None):
        """
        初始化环境配置
        
        Args:
            env: 环境名称（dev/test/prod），不传则从 ENV 环境变量获取
        
        Raises:
            FileNotFoundError: 配置文件不存在时抛出
        """
        # 获取当前环境，优先使用传入的参数，其次使用环境变量（与 config.settings.DEFAULT_ENV 保持一致）
        self.env = env or os.getenv("ENV", DEFAULT_ENV)
        
        # 配置文件路径
        self._config_file = self._CONFIG_DIR / f"{self.env}.yaml"
        
        # 存储加载的配置数据
        self._config: dict = {}
        
        # 加载配置文件
        self._load_config()
    
    def _load_config(self) -> None:
        """
        从 YAML 文件加载配置
        
        私有方法，在初始化时自动调用。
        
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 解析错误
        """
        if not self._config_file.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {self._config_file}\n"
                f"请创建环境配置文件或检查 ENV 环境变量设置（当前值: {self.env}）"
            )
        
        # 读取并解析 YAML 文件
        with open(self._config_file, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}
        
        # 打印加载成功信息（仅在调试时有用）
        print(f"✓ 已加载 {self.env} 环境配置: {self._config_file}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项的值
        
        支持使用点号（.）获取嵌套配置。
        
        Args:
            key: 配置项的键名，支持点号分隔的嵌套键（如 "credentials.username"）
            default: 配置项不存在时返回的默认值
        
        Returns:
            配置项的值，如果不存在则返回默认值
        
        Examples:
            # YAML 配置内容：
            # base_url: https://test.example.com
            # credentials:
            #   username: admin
            #   password: secret
            
            config.get("base_url")                    # "https://test.example.com"
            config.get("credentials.username")        # "admin"
            config.get("not_exist", "默认值")          # "默认值"
        """
        # 分割键名以支持嵌套获取
        keys = key.split(".")
        value = self._config
        
        # 逐层获取配置值
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            # 如果中间某层为 None，返回默认值
            if value is None:
                return default
        
        return value
    
    def get_all(self) -> dict:
        """
        获取所有配置项
        
        Returns:
            包含所有配置的字典
        """
        return self._config.copy()
    
    @property
    def base_url(self) -> str:
        """
        获取基础 URL（快捷属性）
        
        这是最常用的配置项，提供快捷访问方式。
        
        Returns:
            当前环境的 base_url
        """
        return self.get("base_url", "")
    
    @property
    def credentials(self) -> dict:
        """
        获取登录凭据（快捷属性）
        
        Returns:
            包含 username 和 password 的字典
        """
        return self.get("credentials", {})


# ==================== 模块级便捷函数 ====================
# 创建一个全局配置实例，方便直接导入使用

def get_env_config(env: Optional[str] = None) -> EnvConfig:
    """
    获取环境配置实例的工厂函数
    
    Args:
        env: 环境名称，不传则使用 ENV 环境变量
    
    Returns:
        EnvConfig 实例
    
    使用方法：
        from config.env_config import get_env_config
        
        config = get_env_config()
        # 或指定环境
        config = get_env_config("prod")
    """
    return EnvConfig(env)
