# ========================================
# 基础 API 类 - BaseAPI
# ========================================
# 这是所有 API 接口类的基类，封装了通用的 HTTP 请求方法。
# 所有具体的 API 类都应该继承此类。
#
# 主要功能：
# 1. 封装通用的 HTTP 请求方法（GET, POST, PUT, DELETE 等）
# 2. 统一的请求/响应日志记录
# 3. 统一的异常处理
# 4. 支持 Allure 报告集成
# ========================================

import requests
from typing import Optional, Dict, Any, Union
import allure
import json
from utils.logger import Logger
from config.settings import Settings


class BaseAPI:
    """
    基础 API 类
    
    所有 API 接口类都应继承此类，它提供了：
    - 通用的 HTTP 请求方法
    - 日志记录
    - 异常处理
    - Allure 报告集成
    
    使用方法：
        class UserAPI(BaseAPI):
            def __init__(self, base_url: str):
                super().__init__(base_url)
            
            def get_user(self, user_id: int):
                return self.get(f"/users/{user_id}")
            
            def create_user(self, data: dict):
                return self.post("/users", json=data)
    """
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        初始化基础 API 类
        
        Args:
            base_url: API 基础 URL（如 https://api.example.com）
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = Logger(self.__class__.__name__)
        
        # 默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    # ==================== 请求头管理 ====================
    
    def set_header(self, key: str, value: str) -> None:
        """
        设置请求头
        
        Args:
            key: 请求头名称
            value: 请求头值
        """
        self.session.headers[key] = value
        self.logger.debug(f"设置请求头: {key}={value}")
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """
        批量设置请求头
        
        Args:
            headers: 请求头字典
        """
        self.session.headers.update(headers)
        self.logger.debug(f"批量设置请求头: {headers}")
    
    def set_auth_token(self, token: str, prefix: str = "Bearer") -> None:
        """
        设置认证 Token
        
        Args:
            token: Token 值
            prefix: Token 前缀（默认 Bearer）
        """
        self.set_header("Authorization", f"{prefix} {token}")
    
    # ==================== HTTP 请求方法 ====================
    
    @allure.step("GET 请求: {endpoint}")
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送 GET 请求
        
        Args:
            endpoint: 接口路径（如 /users/1）
            params: URL 查询参数
            **kwargs: 其他 requests 参数
        
        Returns:
            Response 对象
        """
        return self._request("GET", endpoint, params=params, **kwargs)
    
    @allure.step("POST 请求: {endpoint}")
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送 POST 请求
        
        Args:
            endpoint: 接口路径
            data: 表单数据
            json: JSON 数据
            **kwargs: 其他 requests 参数
        
        Returns:
            Response 对象
        """
        return self._request("POST", endpoint, data=data, json=json, **kwargs)
    
    @allure.step("PUT 请求: {endpoint}")
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送 PUT 请求
        
        Args:
            endpoint: 接口路径
            data: 表单数据
            json: JSON 数据
            **kwargs: 其他 requests 参数
        
        Returns:
            Response 对象
        """
        return self._request("PUT", endpoint, data=data, json=json, **kwargs)
    
    @allure.step("PATCH 请求: {endpoint}")
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送 PATCH 请求
        
        Args:
            endpoint: 接口路径
            data: 表单数据
            json: JSON 数据
            **kwargs: 其他 requests 参数
        
        Returns:
            Response 对象
        """
        return self._request("PATCH", endpoint, data=data, json=json, **kwargs)
    
    @allure.step("DELETE 请求: {endpoint}")
    def delete(
        self,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        发送 DELETE 请求
        
        Args:
            endpoint: 接口路径
            **kwargs: 其他 requests 参数
        
        Returns:
            Response 对象
        """
        return self._request("DELETE", endpoint, **kwargs)
    
    # ==================== 核心请求方法 ====================
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        发送 HTTP 请求的核心方法
        
        Args:
            method: HTTP 方法（GET, POST, PUT, DELETE 等）
            endpoint: 接口路径
            **kwargs: requests 参数
        
        Returns:
            Response 对象
        """
        url = f"{self.base_url}{endpoint}"
        
        # 设置超时
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        # 记录请求日志
        self._log_request(method, url, kwargs)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # 记录响应日志
            self._log_response(response)
            
            # 附加到 Allure 报告
            self._attach_to_allure(method, url, kwargs, response)
            
            return response
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"请求超时: {url}")
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"连接错误: {url}, {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"请求失败: {url}, 错误: {str(e)}")
            raise
    
    # ==================== 日志方法 ====================
    
    def _log_request(self, method: str, url: str, kwargs: dict) -> None:
        """记录请求日志"""
        self.logger.info(f">>> {method} {url}")
        
        if "params" in kwargs and kwargs["params"]:
            self.logger.debug(f"    Params: {kwargs['params']}")
        if "json" in kwargs and kwargs["json"]:
            self.logger.debug(f"    JSON: {kwargs['json']}")
        if "data" in kwargs and kwargs["data"]:
            self.logger.debug(f"    Data: {kwargs['data']}")
    
    def _log_response(self, response: requests.Response) -> None:
        """记录响应日志"""
        self.logger.info(f"<<< {response.status_code} {response.reason}")
        
        # 尝试解析 JSON 响应
        try:
            body = response.json()
            self.logger.debug(f"    Body: {json.dumps(body, ensure_ascii=False)[:500]}")
        except:
            self.logger.debug(f"    Body: {response.text[:500]}")
    
    def _attach_to_allure(
        self,
        method: str,
        url: str,
        kwargs: dict,
        response: requests.Response
    ) -> None:
        """附加请求/响应到 Allure 报告"""
        # 请求信息
        request_info = {
            "method": method,
            "url": url,
            "headers": dict(self.session.headers),
        }
        if "params" in kwargs:
            request_info["params"] = kwargs["params"]
        if "json" in kwargs:
            request_info["json"] = kwargs["json"]
        if "data" in kwargs:
            request_info["data"] = kwargs["data"]
        
        allure.attach(
            json.dumps(request_info, indent=2, ensure_ascii=False),
            name="请求信息",
            attachment_type=allure.attachment_type.JSON
        )
        
        # 响应信息
        response_info = {
            "status_code": response.status_code,
            "reason": response.reason,
            "headers": dict(response.headers),
        }
        try:
            response_info["body"] = response.json()
        except:
            response_info["body"] = response.text[:1000]
        
        allure.attach(
            json.dumps(response_info, indent=2, ensure_ascii=False),
            name="响应信息",
            attachment_type=allure.attachment_type.JSON
        )
    
    # ==================== 响应断言方法 ====================
    
    def assert_status_code(self, response: requests.Response, expected: int) -> None:
        """
        断言响应状态码
        
        Args:
            response: Response 对象
            expected: 期望的状态码
        """
        actual = response.status_code
        assert actual == expected, f"状态码不匹配: 期望 {expected}, 实际 {actual}"
        self.logger.info(f"✓ 状态码断言通过: {actual}")
    
    def assert_json_key(
        self,
        response: requests.Response,
        key: str,
        expected: Any = None
    ) -> None:
        """
        断言 JSON 响应包含指定键
        
        Args:
            response: Response 对象
            key: JSON 键名（支持点分隔的嵌套键，如 "data.user.name"）
            expected: 期望的值（可选，不传则只检查键是否存在）
        """
        data = response.json()
        
        # 处理嵌套键
        keys = key.split(".")
        value = data
        for k in keys:
            assert k in value, f"JSON 响应中不存在键: {key}"
            value = value[k]
        
        if expected is not None:
            assert value == expected, f"值不匹配: 期望 {expected}, 实际 {value}"
            self.logger.info(f"✓ JSON 断言通过: {key} = {value}")
        else:
            self.logger.info(f"✓ JSON 键存在: {key}")
    
    def assert_json_contains(
        self,
        response: requests.Response,
        expected: Dict[str, Any]
    ) -> None:
        """
        断言 JSON 响应包含指定键值对
        
        Args:
            response: Response 对象
            expected: 期望包含的键值对字典
        """
        data = response.json()
        
        for key, value in expected.items():
            assert key in data, f"JSON 响应中不存在键: {key}"
            assert data[key] == value, f"值不匹配: {key} 期望 {value}, 实际 {data[key]}"
        
        self.logger.info(f"✓ JSON 包含断言通过")
    
    # ==================== 会话管理 ====================
    
    def close(self) -> None:
        """关闭会话"""
        self.session.close()
        self.logger.info("会话已关闭")
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时关闭会话"""
        self.close()
