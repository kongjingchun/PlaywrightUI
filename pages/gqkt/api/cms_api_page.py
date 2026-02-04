# ========================================
# CMS API 页面
# ========================================
# 封装 CMS 相关 API 接口，继承 BaseAPI
# 用于通过 API 注册用户等操作
# ========================================

from typing import Dict, Any, Optional
import allure

from base.base_api import BaseAPI


class CmsApiPage(BaseAPI):
    """
    CMS API 页面
    
    封装 CMS 系统的 API 接口，如用户注册等。
    
    使用方法：
        from config.env_config import EnvConfig
        
        config = EnvConfig()
        cms_api = CmsApiPage(config.base_url)
        success = cms_api.register_cms_user({"username": "test", "password": "123456"})
    """
    
    # 注册接口路径
    REGISTER_ENDPOINT = "/api/auth/register"
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        初始化 CMS API 页面
        
        Args:
            base_url: 基础 URL（如 https://cms.example.com）
            timeout: 请求超时时间（秒）
        """
        super().__init__(base_url, timeout)
    
    @allure.step("API 注册 CMS 用户")
    def register_cms_user(self, user_info: Dict[str, Any]) -> Optional[int]:
        """
        通过 API 注册 CMS 用户
        
        成功时接口返回格式：
        {
            "code": "200",
            "data": {"user_id": *******},
            "message": "注册成功"
        }
        
        Args:
            user_info: 用户信息字典，需包含 username、password
        
        Returns:
            int: 注册成功时返回 user_id，失败时返回 None
        
        使用方法：
            user_id = cms_api.register_cms_user({
                "username": "test_user",
                "password": "123456"
            })
            if user_id:
                print(f"注册成功，user_id={user_id}")
        """
        username = user_info.get("username", "")
        password = user_info.get("password", "")
        
        self.logger.info(f"API 注册 CMS 用户: 用户名={username}, 密码={'*' * len(str(password))}")
        
        data = {
            "username": str(username),
            "password": str(password)
        }
        
        try:
            res = self.post(self.REGISTER_ENDPOINT, json=data)
            response_data = res.json()
            
            code = response_data.get("code")
            message = response_data.get("message", "")
            data_obj = response_data.get("data") or {}
            
            if code == "200" and "注册成功" in message:
                user_id = data_obj.get("user_id")
                self.logger.info(f"用户 {username} 注册成功，user_id={user_id}")
                return user_id
            
            error_msg = f"用户 {username} 注册失败，返回结果：{response_data}"
            self.logger.error(error_msg)
            return None
            
        except Exception as e:
            self.logger.error(f"用户 {username} 注册异常: {e}")
            return None
