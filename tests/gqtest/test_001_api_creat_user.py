# ========================================
# CMS API 创建用户测试
# ========================================
# 通过 API 注册 CMS 用户
# 注意：需在 config/environments/*.yaml 中配置 base_url 为 CMS 服务地址
# 或使用 --base-url-override 指定
# ========================================

from _pytest.stash import T
import pytest
import allure

from pages.gqkt.api import CmsApiPage
from utils.data_loader import load_yaml


# ========== 模块级加载数据 ==========
DATA = load_yaml("gqkt/gqkt_config.yaml")


@allure.feature("CMS API")
@allure.story("用户注册")
class Test001ApiCreatUser:
    """
    测试通过 API 创建 CMS 用户
    """
    
    @pytest.mark.smoke
    @allure.title("API 注册用户")
    def test_001_api_create_user_success(self, base_url):
        """
        测试通过 API 注册用户
        
        Args:
            base_url: 基础 URL（通过 conftest fixture 注入）
        """
        user_info = DATA["user"]["dean_cms"]
        
        with allure.step("调用 API 注册用户"):
            cms_api = CmsApiPage(base_url)
            user_id = cms_api.register_cms_user(user_info)
            print("user_id: "+str(user_id))
        
        with allure.step("断言注册成功并获取 user_id"):
            username = user_info.get("username", "unknown")
            assert user_id is not None, f"用户 {username} 注册失败"
            assert isinstance(user_id, int), f"user_id 应为整数，实际: {type(user_id)}"