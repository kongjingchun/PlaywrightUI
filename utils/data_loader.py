# ========================================
# 测试数据加载模块
# ========================================
# 提供测试数据加载功能，支持：
# - YAML 文件读取
# - JSON 文件读取
# - 参数化数据格式化
# - 数据驱动测试支持
# ========================================

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from config.settings import Settings
from utils.logger import Logger


class DataLoader:
    """
    测试数据加载器
    
    支持从 YAML 和 JSON 文件加载测试数据，
    并提供数据格式化功能用于参数化测试。
    
    使用方法：
        # 创建加载器实例
        loader = DataLoader()
        
        # 加载 YAML 数据
        login_data = loader.load_yaml("login_data.yaml")
        
        # 获取特定数据
        users = loader.get("login_data.yaml", "users")
        
        # 获取参数化测试数据
        test_params = loader.get_parametrize_data("login_data.yaml", "login_cases")
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        初始化数据加载器
        
        Args:
            data_dir: 测试数据目录路径，不传则使用默认的 data/ 目录
        """
        self.data_dir = data_dir or Settings.DATA_DIR
        self.logger = Logger("DataLoader")
        
        # 数据缓存，避免重复读取文件
        self._cache: Dict[str, Any] = {}
    
    def load_yaml(self, filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        加载 YAML 文件
        
        Args:
            filename: 文件名（相对于 data_dir）
            use_cache: 是否使用缓存，默认 True
        
        Returns:
            解析后的数据字典
        
        Raises:
            FileNotFoundError: 文件不存在
            yaml.YAMLError: YAML 解析错误
        
        使用方法：
            loader = DataLoader()
            
            # 加载数据文件
            data = loader.load_yaml("login_data.yaml")
            
            # 访问数据
            username = data["users"][0]["username"]
        """
        # 检查缓存
        cache_key = f"yaml:{filename}"
        if use_cache and cache_key in self._cache:
            self.logger.debug(f"从缓存加载: {filename}")
            return self._cache[cache_key]
        
        # 构建文件路径
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        self.logger.info(f"加载 YAML 文件: {filepath}")
        
        # 读取并解析 YAML
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        # 应用全局变量占位符替换（如 {suffix} -> test_suffix）
        data = self._apply_placeholders(data)
        
        # 存入缓存
        if use_cache:
            self._cache[cache_key] = data
        
        return data
    
    def _apply_placeholders(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归替换数据中的占位符（如 {suffix}）
        
        从数据中提取 test_suffix 等变量，替换所有字符串中的 {suffix}。
        支持扩展：可在数据顶层定义 variables 字典来声明更多占位符。
        
        Args:
            data: 解析后的 YAML 数据
        
        Returns:
            替换后的数据
        """
        # 收集占位符映射：占位符名 -> 替换值
        placeholders: Dict[str, str] = {}
        
        # 默认：test_suffix -> {suffix}
        if "test_suffix" in data:
            placeholders["suffix"] = str(data["test_suffix"])
        
        # 扩展：支持 variables 段定义更多占位符
        if "variables" in data and isinstance(data["variables"], dict):
            for k, v in data["variables"].items():
                placeholders[k] = str(v)
        
        if not placeholders:
            return data
        
        return self._replace_placeholders(data, placeholders)
    
    def _replace_placeholders(
        self, 
        obj: Any, 
        placeholders: Dict[str, str]
    ) -> Any:
        """
        递归遍历数据结构，替换字符串中的 {key} 占位符
        
        Args:
            obj: 任意类型数据
            placeholders: 占位符名 -> 替换值
        """
        if isinstance(obj, dict):
            return {k: self._replace_placeholders(v, placeholders) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_placeholders(item, placeholders) for item in obj]
        elif isinstance(obj, str):
            result = obj
            for key, value in placeholders.items():
                result = result.replace("{" + key + "}", value)
            return result
        else:
            return obj
    
    def load_json(self, filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        加载 JSON 文件
        
        Args:
            filename: 文件名（相对于 data_dir）
            use_cache: 是否使用缓存
        
        Returns:
            解析后的数据字典
        
        使用方法：
            data = loader.load_json("api_data.json")
        """
        # 检查缓存
        cache_key = f"json:{filename}"
        if use_cache and cache_key in self._cache:
            self.logger.debug(f"从缓存加载: {filename}")
            return self._cache[cache_key]
        
        # 构建文件路径
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        self.logger.info(f"加载 JSON 文件: {filepath}")
        
        # 读取并解析 JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 存入缓存
        if use_cache:
            self._cache[cache_key] = data
        
        return data
    
    def get(
        self, 
        filename: str, 
        key: str, 
        default: Any = None
    ) -> Any:
        """
        从数据文件中获取指定的数据项
        
        支持使用点号（.）获取嵌套数据。
        
        Args:
            filename: 文件名
            key: 数据键名，支持点号分隔的嵌套键
            default: 默认值
        
        Returns:
            数据值，如果不存在返回默认值
        
        使用方法：
            # YAML 内容:
            # users:
            #   admin:
            #     username: admin
            #     password: admin123
            
            username = loader.get("users.yaml", "users.admin.username")
        """
        # 根据文件扩展名选择加载方法
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            data = self.load_yaml(filename)
        elif filename.endswith('.json'):
            data = self.load_json(filename)
        else:
            raise ValueError(f"不支持的文件格式: {filename}")
        
        # 处理嵌套键
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            elif isinstance(value, list) and k.isdigit():
                # 支持列表索引访问
                index = int(k)
                value = value[index] if index < len(value) else None
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_parametrize_data(
        self, 
        filename: str, 
        key: str,
        id_field: str = "id"
    ) -> List[tuple]:
        """
        获取参数化测试数据
        
        将 YAML/JSON 中的列表数据转换为 pytest.mark.parametrize 需要的格式。
        
        Args:
            filename: 文件名
            key: 数据列表的键名
            id_field: 用作测试ID的字段名
        
        Returns:
            适用于 pytest.mark.parametrize 的数据列表
        
        使用方法：
            # YAML 内容:
            # login_cases:
            #   - id: valid_login
            #     username: admin
            #     password: admin123
            #     expected: success
            #   - id: invalid_password
            #     username: admin
            #     password: wrong
            #     expected: error
            
            # 测试代码:
            loader = DataLoader()
            test_data = loader.get_parametrize_data("login_data.yaml", "login_cases")
            
            @pytest.mark.parametrize("test_case", test_data, ids=lambda x: x.get("id"))
            def test_login(test_case):
                # test_case 是完整的数据字典
                username = test_case["username"]
                password = test_case["password"]
        """
        data = self.get(filename, key, [])
        
        if not isinstance(data, list):
            raise ValueError(f"数据 '{key}' 必须是列表类型")
        
        self.logger.info(f"加载参数化数据: {filename}:{key}, 共 {len(data)} 条")
        return data
    
    def get_parametrize_ids(
        self, 
        filename: str, 
        key: str,
        id_field: str = "id"
    ) -> List[str]:
        """
        获取参数化测试的ID列表
        
        Args:
            filename: 文件名
            key: 数据列表的键名
            id_field: ID字段名
        
        Returns:
            ID 字符串列表
        """
        data = self.get(filename, key, [])
        return [item.get(id_field, f"case_{i}") for i, item in enumerate(data)]
    
    def clear_cache(self) -> None:
        """
        清空数据缓存
        
        在数据文件更新后调用，确保读取最新数据。
        """
        self._cache.clear()
        self.logger.info("数据缓存已清空")


# ==================== 模块级便捷函数 ====================

# 全局数据加载器实例
_global_loader: Optional[DataLoader] = None


def _get_loader() -> DataLoader:
    """获取全局数据加载器实例"""
    global _global_loader
    if _global_loader is None:
        _global_loader = DataLoader()
    return _global_loader


def load_yaml(filename: str) -> Dict[str, Any]:
    """
    加载 YAML 文件（便捷函数）
    
    Args:
        filename: 文件名
    
    Returns:
        解析后的数据字典
    
    使用方法：
        from utils.data_loader import load_yaml
        
        data = load_yaml("login_data.yaml")
    """
    return _get_loader().load_yaml(filename)


def load_json(filename: str) -> Dict[str, Any]:
    """
    加载 JSON 文件（便捷函数）
    
    Args:
        filename: 文件名
    
    Returns:
        解析后的数据字典
    """
    return _get_loader().load_json(filename)


def get_test_data(filename: str, key: str, default: Any = None) -> Any:
    """
    获取测试数据（便捷函数）
    
    Args:
        filename: 文件名
        key: 数据键名
        default: 默认值
    
    Returns:
        数据值
    
    使用方法：
        from utils.data_loader import get_test_data
        
        username = get_test_data("login_data.yaml", "users.admin.username")
    """
    return _get_loader().get(filename, key, default)


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试数据加载功能
    loader = DataLoader()
    
    # 创建测试数据文件
    test_data = {
        "users": [
            {"username": "admin", "password": "admin123"},
            {"username": "user", "password": "user123"}
        ],
        "settings": {
            "timeout": 30,
            "retry": 3
        }
    }
    
    # 保存测试数据
    Settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(Settings.DATA_DIR / "test_sample.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(test_data, f, allow_unicode=True)
    
    # 测试加载
    data = loader.load_yaml("test_sample.yaml")
    print(f"加载的数据: {data}")
    
    # 测试获取嵌套数据
    timeout = loader.get("test_sample.yaml", "settings.timeout")
    print(f"超时设置: {timeout}")
