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
from typing import Tuple, List, Optional, Dict, Any

from config.settings import Settings

_OUTCOME_PASSED = "passed"
_OUTCOME_FAILED = "failed"
_OUTCOME_SKIPPED = "skipped"


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
        process.record_success_testcase(nodeid, name)  # 按 nodeid 记录展示名
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

            # 清空用例记录（按 nodeid 存最终状态，避免重复与成功/失败交叉）
            self._write_json_file(self.testcase_file, {"case_results": {}})

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

    def _merge_case_result(self, nodeid: str, testcase_name: str, outcome: str) -> None:
        """同一 nodeid 后写入的结果覆盖先前结果（兼容失败重跑等场景）。"""
        with self._file_lock:
            testcase_data = self._read_json_file(self.testcase_file)
            case_results: Dict[str, Any] = testcase_data.get("case_results", {})
            if not isinstance(case_results, dict):
                case_results = {}
            case_results[nodeid] = {"outcome": outcome, "name": testcase_name}
            testcase_data["case_results"] = case_results
            self._write_json_file(self.testcase_file, testcase_data)

    def record_success_testcase(self, nodeid: str, testcase_name: str) -> None:
        """
        记录成功用例（按 pytest nodeid 去重，与失败/跳过互斥）

        Args:
            nodeid: pytest 用例节点 id
            testcase_name: 展示用名称（通常为 docstring 首行）
        """
        self._merge_case_result(nodeid, testcase_name, _OUTCOME_PASSED)

    def record_failed_testcase(self, nodeid: str, testcase_name: str) -> None:
        """
        记录失败用例（按 pytest nodeid 去重，与成功/跳过互斥）

        Args:
            nodeid: pytest 用例节点 id
            testcase_name: 展示用名称（通常为 docstring 首行）
        """
        self._merge_case_result(nodeid, testcase_name, _OUTCOME_FAILED)

    def record_skipped_testcase(self, nodeid: str, testcase_name: str) -> None:
        """
        记录跳过用例（按 pytest nodeid 去重）

        Args:
            nodeid: pytest 用例节点 id
            testcase_name: 展示用名称（通常为 docstring 首行）
        """
        self._merge_case_result(nodeid, testcase_name, _OUTCOME_SKIPPED)

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

    def _case_results_map(self) -> Dict[str, Any]:
        testcase_data = self._read_json_file(self.testcase_file)
        raw = testcase_data.get("case_results", {})
        if isinstance(raw, dict) and raw:
            return raw
        return {}

    def get_success_testcases(self) -> List[str]:
        """获取成功用例展示名列表（每个 nodeid 至多一条，按 nodeid 排序）。"""
        m = self._case_results_map()
        if m:
            return [
                str(v.get("name", ""))
                for _, v in sorted(m.items())
                if v.get("outcome") == _OUTCOME_PASSED
            ]
        data = self._read_json_file(self.testcase_file)
        return list(data.get("success_testcases", []))

    def get_failed_testcases(self) -> List[str]:
        """获取失败用例展示名列表（每个 nodeid 至多一条，按 nodeid 排序）。"""
        m = self._case_results_map()
        if m:
            return [
                str(v.get("name", ""))
                for _, v in sorted(m.items())
                if v.get("outcome") == _OUTCOME_FAILED
            ]
        data = self._read_json_file(self.testcase_file)
        return list(data.get("failed_testcases", []))

    def get_skipped_testcases(self) -> List[str]:
        """获取跳过用例展示名列表（每个 nodeid 至多一条，按 nodeid 排序）。"""
        m = self._case_results_map()
        if m:
            return [
                str(v.get("name", ""))
                for _, v in sorted(m.items())
                if v.get("outcome") == _OUTCOME_SKIPPED
            ]
        data = self._read_json_file(self.testcase_file)
        return list(data.get("skipped_testcases", []))

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
