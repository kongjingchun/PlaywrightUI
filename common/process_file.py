# ========================================
# 测试进度管理类
# ========================================
# 通过 JSON 文件记录测试执行进度和结果
# 支持多进程/多线程安全操作
# ========================================

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Optional

from config.settings import Settings


class ProcessFile:
    """
    测试进度管理类
    
    使用 JSON 文件存储测试执行进度和结果，支持：
    - 测试进度跟踪（总数、成功、失败）
    - 测试用例名称记录
    - 执行时间统计
    
    使用方法：
        process = ProcessFile()
        process.init_process(total=10)  # 初始化
        process.update_success()  # 成功+1
        process.update_fail()  # 失败+1
        total, success, fail, start_time = process.get_result()  # 获取结果
    """
    
    # 单例实例
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式，确保全局只有一个实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化文件路径"""
        if self._initialized:
            return
            
        # 日志目录
        self.logs_dir = Settings.PROJECT_ROOT / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 进度文件路径
        self.process_file = self.logs_dir / "test_process.json"
        # 用例记录文件路径
        self.testcase_file = self.logs_dir / "testcase_records.json"
        
        # 线程锁
        self._file_lock = threading.Lock()
        
        self._initialized = True
    
    def _read_json_file(self, file_path: Path) -> dict:
        """
        读取 JSON 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            JSON 数据字典，文件不存在返回空字典
        """
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"读取文件失败: {file_path}, 错误: {e}")
            return {}
    
    def _write_json_file(self, file_path: Path, data: dict) -> None:
        """
        写入 JSON 文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入文件失败: {file_path}, 错误: {e}")
    
    def reset_all(self) -> None:
        """清空所有进度数据"""
        with self._file_lock:
            # 重置进度数据
            process_data = {
                "total": 0,
                "success": 0,
                "fail": 0,
                "skip": 0,
                "start_time": "",
                "end_time": "",
                "running_status": 0
            }
            self._write_json_file(self.process_file, process_data)
            
            # 清空用例记录
            self._write_json_file(self.testcase_file, {
                "success_testcases": [],
                "failed_testcases": [],
                "skipped_testcases": []
            })
    
    def init_process(self, total: int) -> None:
        """
        初始化测试进度
        
        Args:
            total: 测试用例总数
        """
        with self._file_lock:
            process_data = {
                "total": total,
                "success": 0,
                "fail": 0,
                "skip": 0,
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": "",
                "running_status": 1
            }
            self._write_json_file(self.process_file, process_data)
    
    def update_success(self) -> None:
        """成功用例数 +1"""
        with self._file_lock:
            process_data = self._read_json_file(self.process_file)
            if not process_data:
                process_data = {"total": 0, "success": 0, "fail": 0, "skip": 0}
            process_data["success"] = process_data.get("success", 0) + 1
            self._write_json_file(self.process_file, process_data)
    
    def update_fail(self) -> None:
        """失败用例数 +1"""
        with self._file_lock:
            process_data = self._read_json_file(self.process_file)
            if not process_data:
                process_data = {"total": 0, "success": 0, "fail": 0, "skip": 0}
            process_data["fail"] = process_data.get("fail", 0) + 1
            self._write_json_file(self.process_file, process_data)
    
    def update_skip(self) -> None:
        """跳过用例数 +1"""
        with self._file_lock:
            process_data = self._read_json_file(self.process_file)
            if not process_data:
                process_data = {"total": 0, "success": 0, "fail": 0, "skip": 0}
            process_data["skip"] = process_data.get("skip", 0) + 1
            self._write_json_file(self.process_file, process_data)
    
    def record_success_testcase(self, testcase_name: str) -> None:
        """
        记录成功用例名称
        
        Args:
            testcase_name: 测试用例名称
        """
        with self._file_lock:
            testcase_data = self._read_json_file(self.testcase_file)
            if "success_testcases" not in testcase_data:
                testcase_data["success_testcases"] = []
            testcase_data["success_testcases"].insert(0, testcase_name)
            self._write_json_file(self.testcase_file, testcase_data)
    
    def record_failed_testcase(self, testcase_name: str) -> None:
        """
        记录失败用例名称
        
        Args:
            testcase_name: 测试用例名称
        """
        with self._file_lock:
            testcase_data = self._read_json_file(self.testcase_file)
            if "failed_testcases" not in testcase_data:
                testcase_data["failed_testcases"] = []
            testcase_data["failed_testcases"].insert(0, testcase_name)
            self._write_json_file(self.testcase_file, testcase_data)
    
    def record_skipped_testcase(self, testcase_name: str) -> None:
        """
        记录跳过用例名称
        
        Args:
            testcase_name: 测试用例名称
        """
        with self._file_lock:
            testcase_data = self._read_json_file(self.testcase_file)
            if "skipped_testcases" not in testcase_data:
                testcase_data["skipped_testcases"] = []
            testcase_data["skipped_testcases"].insert(0, testcase_name)
            self._write_json_file(self.testcase_file, testcase_data)
    
    def get_result(self) -> Tuple[int, int, int, int, str]:
        """
        获取测试结果统计
        
        Returns:
            (总数, 成功数, 失败数, 跳过数, 开始时间)
        """
        process_data = self._read_json_file(self.process_file)
        total = process_data.get("total", 0)
        success = process_data.get("success", 0)
        fail = process_data.get("fail", 0)
        skip = process_data.get("skip", 0)
        start_time = process_data.get("start_time", "-")
        return total, success, fail, skip, start_time
    
    def get_progress(self) -> str:
        """
        计算测试进度百分比
        
        Returns:
            进度百分比字符串，如 "50.0%"
        """
        total, success, fail, skip, _ = self.get_result()
        if total == 0:
            return "0%"
        percentage = (success + fail + skip) / total * 100
        return f"{percentage:.1f}%"
    
    def get_success_testcases(self) -> List[str]:
        """获取所有成功用例名称列表"""
        testcase_data = self._read_json_file(self.testcase_file)
        return testcase_data.get("success_testcases", [])
    
    def get_failed_testcases(self) -> List[str]:
        """获取所有失败用例名称列表"""
        testcase_data = self._read_json_file(self.testcase_file)
        return testcase_data.get("failed_testcases", [])
    
    def get_skipped_testcases(self) -> List[str]:
        """获取所有跳过用例名称列表"""
        testcase_data = self._read_json_file(self.testcase_file)
        return testcase_data.get("skipped_testcases", [])
    
    def write_end_time(self) -> None:
        """记录测试结束时间"""
        with self._file_lock:
            process_data = self._read_json_file(self.process_file)
            process_data["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            process_data["running_status"] = 0
            self._write_json_file(self.process_file, process_data)
    
    def get_duration(self) -> str:
        """
        计算执行耗时
        
        Returns:
            格式化的耗时字符串，如 "1小时2分3秒"
        """
        process_data = self._read_json_file(self.process_file)
        start_time_str = process_data.get("start_time", "")
        end_time_str = process_data.get("end_time", "")
        
        if not start_time_str or not end_time_str:
            return "未知"
        
        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            duration = end_time - start_time
            duration_seconds = int(duration.total_seconds())
            
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            
            if hours > 0:
                return f"{hours}小时{minutes}分{seconds}秒"
            elif minutes > 0:
                return f"{minutes}分{seconds}秒"
            else:
                return f"{seconds}秒"
        except Exception:
            return "计算失败"
