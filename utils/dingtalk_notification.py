# ========================================
# 钉钉通知工具
# ========================================
# 用于在测试执行完成后发送钉钉通知
# ========================================

import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from typing import Dict, Optional, List
from utils.logger import Logger


class DingTalkNotification:
    """钉钉通知类，用于发送测试报告到钉钉群"""
    
    def __init__(self, webhook: str, secret: Optional[str] = None):
        """
        初始化钉钉通知
        
        Args:
            webhook: 钉钉机器人的 webhook 地址
            secret: 钉钉机器人的加签密钥（如果启用了加签）
        """
        self.webhook = webhook
        self.secret = secret
        self.logger = Logger(self.__class__.__name__)
    
    def _generate_sign(self) -> tuple:
        """
        生成钉钉加签
        
        Returns:
            (timestamp, sign) 元组
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(
            secret_enc, 
            string_to_sign_enc, 
            digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign
    
    def _get_webhook_url(self) -> str:
        """
        获取完整的 webhook URL（包含加签参数）
        
        Returns:
            完整的 webhook URL
        """
        if self.secret:
            timestamp, sign = self._generate_sign()
            return f"{self.webhook}&timestamp={timestamp}&sign={sign}"
        return self.webhook
    
    def send_text(self, content: str, at_mobiles: Optional[List[str]] = None, 
                  at_all: bool = False) -> bool:
        """
        发送文本消息
        
        Args:
            content: 消息内容
            at_mobiles: 要@的手机号列表
            at_all: 是否@所有人
        
        Returns:
            是否发送成功
        """
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": at_all
            }
        }
        return self._send(data)
    
    def send_markdown(self, title: str, text: str, 
                     at_mobiles: Optional[List[str]] = None,
                     at_all: bool = False) -> bool:
        """
        发送 Markdown 消息
        
        Args:
            title: 消息标题
            text: Markdown 格式的消息内容
            at_mobiles: 要@的手机号列表
            at_all: 是否@所有人
        
        Returns:
            是否发送成功
        """
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": at_all
            }
        }
        return self._send(data)
    
    def _send(self, data: Dict) -> bool:
        """
        发送消息到钉钉
        
        Args:
            data: 消息数据
        
        Returns:
            是否发送成功
        """
        try:
            url = self._get_webhook_url()
            headers = {"Content-Type": "application/json;charset=utf-8"}
            response = requests.post(url, json=data, headers=headers, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                self.logger.info("✓ 钉钉消息发送成功")
                return True
            else:
                self.logger.error(f"✗ 钉钉消息发送失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            self.logger.error(f"✗ 发送钉钉消息异常: {e}")
            return False
    
    def send_test_report(self, 
                        total: int,
                        passed: int, 
                        failed: int,
                        skipped: int,
                        duration: str,
                        failed_cases: Optional[List[str]] = None,
                        environment: str = "测试环境") -> bool:
        """
        发送测试报告
        
        Args:
            total: 总用例数
            passed: 通过数
            failed: 失败数
            skipped: 跳过数
            duration: 执行时长
            failed_cases: 失败用例列表
            environment: 环境名称
        
        Returns:
            是否发送成功
        """
        # 计算通过率
        pass_rate = f"{(passed / total * 100):.2f}%" if total > 0 else "0%"
        
        # 确定测试状态图标
        if failed > 0:
            status_icon = "❌"
            status_text = "测试失败"
            status_color = "#FF0000"
        elif skipped > 0:
            status_icon = "⚠️"
            status_text = "部分跳过"
            status_color = "#FFA500"
        else:
            status_icon = "✅"
            status_text = "全部通过"
            status_color = "#00FF00"
        
        # 构建 Markdown 消息
        title = f"{status_icon} 自动化测试报告"
        
        text_parts = [
            f"# {status_icon} 自动化测试报告\n",
            f"---\n",
            f"### 📊 测试结果\n",
            f"- **环境**: {environment}\n",
            f"- **状态**: <font color='{status_color}'>{status_text}</font>\n",
            f"- **总数**: {total}\n",
            f"- **通过**: <font color='#00FF00'>{passed}</font>\n",
            f"- **失败**: <font color='#FF0000'>{failed}</font>\n",
            f"- **跳过**: <font color='#FFA500'>{skipped}</font>\n",
            f"- **通过率**: {pass_rate}\n",
            f"- **耗时**: {duration}\n",
        ]
        
        # 如果有失败用例，添加失败列表
        if failed > 0 and failed_cases:
            text_parts.append("\n### ❌ 失败用例\n")
            for i, case in enumerate(failed_cases[:10], 1):  # 最多显示10个
                text_parts.append(f"{i}. {case}\n")
            if len(failed_cases) > 10:
                text_parts.append(f"\n... 还有 {len(failed_cases) - 10} 个失败用例\n")
        
        text_parts.append(f"\n---\n")
        text_parts.append(f"*{time.strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        text = "".join(text_parts)
        
        # 发送消息
        return self.send_markdown(
            title=title,
            text=text,
            at_all=failed > 0  # 如果有失败用例，@所有人
        )


def send_dingtalk_report(webhook: str,
                        secret: Optional[str],
                        total: int,
                        passed: int,
                        failed: int,
                        skipped: int,
                        duration: str,
                        failed_cases: Optional[List[str]] = None,
                        environment: str = "测试环境") -> bool:
    """
    发送钉钉测试报告的便捷函数
    
    Args:
        webhook: 钉钉机器人 webhook
        secret: 加签密钥
        total: 总用例数
        passed: 通过数
        failed: 失败数
        skipped: 跳过数
        duration: 执行时长
        failed_cases: 失败用例列表
        environment: 环境名称
    
    Returns:
        是否发送成功
    """
    if not webhook:
        return False
    
    notifier = DingTalkNotification(webhook, secret)
    return notifier.send_test_report(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration=duration,
        failed_cases=failed_cases,
        environment=environment
    )


if __name__ == '__main__':
    # 测试功能（需要配置真实的 webhook）
    # webhook = "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    # secret = "SECxxx"
    # 
    # notifier = DingTalkNotification(webhook, secret)
    # notifier.send_test_report(
    #     total=10,
    #     passed=8,
    #     failed=2,
    #     skipped=0,
    #     duration="1分30秒",
    #     failed_cases=["test_login_failed", "test_search_error"],
    #     environment="测试环境"
    # )
    print("钉钉通知模块已加载")
