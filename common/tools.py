# ========================================
# 通用工具函数
# ========================================
# 提供常用的功能函数，如时间处理、路径处理等
# ========================================

import os
import datetime
from pathlib import Path
from typing import List, Union, Optional


def get_now_time() -> datetime.datetime:
    """
    获取当前时间
    
    Returns:
        当前的日期时间对象
    """
    return datetime.datetime.now()


def get_now_time_str(format_str: str = "%Y%m%d%H%M%S") -> str:
    """
    获取当前时间字符串
    
    Args:
        format_str: 时间格式字符串，默认 "%Y%m%d%H%M%S"
    
    Returns:
        当前时间字符串
    
    示例：
        get_now_time_str()  # "20260203184500"
        get_now_time_str("%Y-%m-%d %H:%M:%S")  # "2026-02-03 18:45:00"
    """
    return get_now_time().strftime(format_str)


def get_project_path() -> Path:
    """
    获取项目根路径
    
    Returns:
        项目根目录的 Path 对象
    """
    # 从当前文件向上查找，直到找到包含 pytest.ini 的目录
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if (parent / "pytest.ini").exists():
            return parent
    # 如果找不到 pytest.ini，返回当前文件的上两级目录
    return current_file.parents[1]


def get_project_path_str() -> str:
    """
    获取项目根路径字符串
    
    Returns:
        项目根目录的绝对路径字符串
    """
    return str(get_project_path())


def sep(path: Union[List[str], tuple], 
        add_sep_before: bool = False,
        add_sep_after: bool = False) -> str:
    """
    构造路径字符串，在路径片段之间添加系统分隔符
    
    Args:
        path: 路径片段列表或元组
        add_sep_before: 是否在路径前添加分隔符，默认 False
        add_sep_after: 是否在路径后添加分隔符，默认 False
    
    Returns:
        处理后的路径字符串
    
    示例：
        sep(['logs', 'test.log'])  # "logs/test.log" (Unix) 或 "logs\\test.log" (Windows)
        sep(['img', 'pic.png'], add_sep_before=True)  # "/img/pic.png"
    """
    # 使用 os.path.join 处理跨平台路径
    all_path = os.path.join(*path)
    
    if add_sep_before:
        all_path = os.sep + all_path
    if add_sep_after:
        all_path = all_path + os.sep
    
    return all_path


def build_path(*paths: str, base_path: Optional[Path] = None) -> Path:
    """
    构建路径对象（推荐使用，比 sep 更现代）
    
    Args:
        *paths: 路径片段
        base_path: 基础路径，默认为项目根路径
    
    Returns:
        Path 对象
    
    示例：
        build_path('logs', 'test.log')  # Path('project_root/logs/test.log')
        build_path('data', 'yaml', 'test.yaml')  # Path('project_root/data/yaml/test.yaml')
    """
    if base_path is None:
        base_path = get_project_path()
    return base_path / Path(*paths)


def get_img_path(img_name: str) -> str:
    """
    获取图片文件的完整路径
    
    Args:
        img_name: 图片文件名
    
    Returns:
        图片文件的完整路径字符串
    """
    return str(get_project_path() / "img" / img_name)


def get_data_path(data_name: str) -> str:
    """
    获取数据文件的完整路径
    
    Args:
        data_name: 数据文件名
    
    Returns:
        数据文件的完整路径字符串
    """
    return str(get_project_path() / "data" / data_name)


def get_log_path(log_name: str) -> str:
    """
    获取日志文件的完整路径
    
    Args:
        log_name: 日志文件名
    
    Returns:
        日志文件的完整路径字符串
    """
    return str(get_project_path() / "logs" / log_name)


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    确保目录存在，不存在则创建
    
    Args:
        directory: 目录路径
    
    Returns:
        目录的 Path 对象
    """
    dir_path = Path(directory) if isinstance(directory, str) else directory
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_duration(seconds: int) -> str:
    """
    格式化时长（秒数转为易读的字符串）
    
    Args:
        seconds: 秒数
    
    Returns:
        格式化后的时长字符串
    
    示例：
        format_duration(65)  # "1分5秒"
        format_duration(3665)  # "1小时1分5秒"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


if __name__ == '__main__':
    # 测试函数功能
    print(f"项目路径: {get_project_path()}")
    print(f"当前时间: {get_now_time_str()}")
    print(f"路径分隔: {sep(['logs', 'test.log'])}")
    print(f"格式化时长: {format_duration(3665)}")
