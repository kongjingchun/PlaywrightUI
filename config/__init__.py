# ========================================
# 配置模块初始化文件
# ========================================
# 该模块负责管理所有配置相关的功能，包括：
# - settings.py: 全局配置（浏览器类型、超时时间等）
# - env_config.py: 环境配置加载器
# ========================================

from config.settings import Settings
from config.env_config import EnvConfig

# 导出配置类，方便其他模块直接导入使用
__all__ = ['Settings', 'EnvConfig']
