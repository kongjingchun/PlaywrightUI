# ========================================
# 等待助手模块
# ========================================
# 提供自定义等待功能，扩展 Playwright 原生等待能力，包括：
# - 自定义条件等待
# - API 响应等待
# - 元素状态变化等待
# - 重试机制
# ========================================

from playwright.sync_api import Page, Locator, Response
from typing import Callable, Optional, Any, List
import time
from utils.logger import Logger


class WaitHelper:
    """
    等待助手类
    
    扩展 Playwright 的等待功能，提供更灵活的等待机制。
    
    使用方法：
        wait_helper = WaitHelper(page)
        
        # 等待自定义条件
        wait_helper.wait_for_condition(
            lambda: page.locator("#result").count() > 0,
            timeout=10000,
            message="等待搜索结果"
        )
        
        # 等待 API 响应
        response = wait_helper.wait_for_api_response("/api/users")
        
        # 带重试的操作
        wait_helper.retry_on_failure(
            lambda: page.click("#unstable-button"),
            max_retries=3
        )
    """
    
    def __init__(self, page: Page):
        """
        初始化等待助手
        
        Args:
            page: Playwright 的 Page 对象
        """
        self.page = page
        self.logger = Logger("WaitHelper")
    
    def wait_for_condition(
        self,
        condition: Callable[[], bool],
        timeout: int = 30000,
        interval: int = 500,
        message: str = "等待条件满足"
    ) -> bool:
        """
        等待自定义条件满足
        
        周期性检查条件函数的返回值，直到返回 True 或超时。
        这是最灵活的等待方式，适用于复杂场景。
        
        Args:
            condition: 条件函数，返回 True 表示条件满足
            timeout: 超时时间（毫秒）
            interval: 检查间隔（毫秒）
            message: 等待描述信息（用于日志）
        
        Returns:
            True 如果条件在超时前满足，否则抛出异常
        
        Raises:
            TimeoutError: 超时时抛出
        
        使用方法：
            # 等待元素数量变化
            wait_helper.wait_for_condition(
                lambda: page.locator(".item").count() >= 10,
                timeout=10000,
                message="等待加载至少10个项目"
            )
            
            # 等待页面状态变化
            wait_helper.wait_for_condition(
                lambda: "成功" in page.locator("#message").inner_text(),
                message="等待成功提示"
            )
        """
        self.logger.info(f"开始等待: {message}")
        
        start_time = time.time()
        timeout_seconds = timeout / 1000
        interval_seconds = interval / 1000
        
        while True:
            try:
                # 检查条件
                if condition():
                    self.logger.info(f"条件满足: {message}")
                    return True
            except Exception as e:
                # 条件检查出错时记录但继续等待
                self.logger.debug(f"条件检查出错: {e}")
            
            # 检查是否超时
            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                error_msg = f"等待超时({timeout}ms): {message}"
                self.logger.error(error_msg)
                raise TimeoutError(error_msg)
            
            # 等待下一次检查
            time.sleep(interval_seconds)
    
    def wait_for_api_response(
        self,
        url_pattern: str,
        timeout: int = 30000,
        status: Optional[int] = None
    ) -> Response:
        """
        等待特定的 API 响应
        
        拦截网络请求，等待匹配指定 URL 模式的响应。
        适用于需要等待后台接口返回的场景。
        
        Args:
            url_pattern: URL 匹配模式（支持 glob 模式）
            timeout: 超时时间（毫秒）
            status: 期望的状态码，不传则不校验
        
        Returns:
            匹配的 Response 对象
        
        使用方法：
            # 等待登录接口响应
            response = wait_helper.wait_for_api_response("**/api/login")
            assert response.status == 200
            
            # 等待特定状态码的响应
            response = wait_helper.wait_for_api_response(
                "**/api/users",
                status=200
            )
            data = response.json()
        """
        self.logger.info(f"等待 API 响应: {url_pattern}")
        
        # 使用 Playwright 的 expect_response 等待
        with self.page.expect_response(
            lambda r: url_pattern.replace("**", "") in r.url,
            timeout=timeout
        ) as response_info:
            pass
        
        response = response_info.value
        self.logger.info(f"收到响应: {response.url}, 状态码: {response.status}")
        
        # 检查状态码
        if status is not None and response.status != status:
            raise AssertionError(
                f"API 响应状态码不匹配: 期望 {status}, 实际 {response.status}"
            )
        
        return response
    
    def wait_for_element_count(
        self,
        locator: Locator,
        expected_count: int,
        comparison: str = "==",
        timeout: int = 30000
    ) -> bool:
        """
        等待元素数量达到期望值
        
        Args:
            locator: 元素定位器
            expected_count: 期望的元素数量
            comparison: 比较方式，支持 "==", ">=", "<=", ">", "<"
            timeout: 超时时间
        
        Returns:
            True 如果条件满足
        
        使用方法：
            # 等待恰好 5 个元素
            wait_helper.wait_for_element_count(
                page.locator(".item"),
                expected_count=5
            )
            
            # 等待至少 3 个元素
            wait_helper.wait_for_element_count(
                page.locator(".item"),
                expected_count=3,
                comparison=">="
            )
        """
        def check_count():
            actual_count = locator.count()
            
            if comparison == "==":
                return actual_count == expected_count
            elif comparison == ">=":
                return actual_count >= expected_count
            elif comparison == "<=":
                return actual_count <= expected_count
            elif comparison == ">":
                return actual_count > expected_count
            elif comparison == "<":
                return actual_count < expected_count
            else:
                raise ValueError(f"不支持的比较方式: {comparison}")
        
        return self.wait_for_condition(
            check_count,
            timeout=timeout,
            message=f"等待元素数量 {comparison} {expected_count}"
        )
    
    def wait_for_text_change(
        self,
        locator: Locator,
        original_text: str,
        timeout: int = 30000
    ) -> str:
        """
        等待元素文本发生变化
        
        Args:
            locator: 元素定位器
            original_text: 原始文本
            timeout: 超时时间
        
        Returns:
            变化后的新文本
        
        使用方法：
            original = page.locator("#counter").inner_text()
            page.click("#increment")
            new_text = wait_helper.wait_for_text_change(
                page.locator("#counter"),
                original
            )
        """
        new_text = [original_text]  # 使用列表以便在闭包中修改
        
        def check_text_changed():
            current = locator.inner_text()
            if current != original_text:
                new_text[0] = current
                return True
            return False
        
        self.wait_for_condition(
            check_text_changed,
            timeout=timeout,
            message=f"等待文本从 '{original_text}' 变化"
        )
        
        self.logger.info(f"文本已变化: '{original_text}' -> '{new_text[0]}'")
        return new_text[0]
    
    def wait_for_loading_complete(
        self,
        loading_indicator: str = ".loading, .spinner, [data-loading]",
        timeout: int = 60000
    ) -> None:
        """
        等待加载指示器消失
        
        通用的等待加载完成方法，适用于有 loading 动画的场景。
        
        Args:
            loading_indicator: 加载指示器的选择器
            timeout: 超时时间
        
        使用方法：
            page.click("#submit")
            wait_helper.wait_for_loading_complete()
            # 加载完成后继续操作
        """
        self.logger.info("等待加载完成...")
        
        locator = self.page.locator(loading_indicator)
        
        # 先等待加载指示器出现（可能立即就没有）
        try:
            locator.wait_for(state="visible", timeout=1000)
        except:
            # 如果加载指示器没有出现，可能加载很快就完成了
            self.logger.debug("未检测到加载指示器，可能已加载完成")
            return
        
        # 等待加载指示器消失
        locator.wait_for(state="hidden", timeout=timeout)
        self.logger.info("加载完成")
    
    def retry_on_failure(
        self,
        action: Callable[[], Any],
        max_retries: int = 3,
        retry_interval: int = 1000,
        on_retry: Optional[Callable[[int, Exception], None]] = None
    ) -> Any:
        """
        带重试机制执行操作
        
        如果操作失败，会自动重试指定次数。
        适用于可能因临时问题失败的操作（如元素被遮挡、网络延迟等）。
        
        Args:
            action: 要执行的操作函数
            max_retries: 最大重试次数
            retry_interval: 重试间隔（毫秒）
            on_retry: 重试时的回调函数，参数为 (重试次数, 异常)
        
        Returns:
            操作的返回值
        
        Raises:
            最后一次失败的异常
        
        使用方法：
            # 带重试的点击操作
            wait_helper.retry_on_failure(
                lambda: page.click("#flaky-button"),
                max_retries=3
            )
            
            # 带重试回调的操作
            def on_retry(attempt, error):
                print(f"第 {attempt} 次重试，错误: {error}")
                page.reload()  # 重试前刷新页面
            
            wait_helper.retry_on_failure(
                lambda: page.click("#button"),
                max_retries=3,
                on_retry=on_retry
            )
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return action()
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    self.logger.warning(
                        f"操作失败，准备第 {attempt + 1} 次重试: {str(e)}"
                    )
                    
                    # 调用重试回调
                    if on_retry:
                        on_retry(attempt + 1, e)
                    
                    # 等待后重试
                    time.sleep(retry_interval / 1000)
                else:
                    self.logger.error(
                        f"操作失败，已达到最大重试次数 ({max_retries}): {str(e)}"
                    )
        
        raise last_exception
    
    def wait_for_download(
        self,
        trigger_action: Callable[[], None],
        timeout: int = 60000
    ) -> str:
        """
        等待文件下载完成
        
        Args:
            trigger_action: 触发下载的操作
            timeout: 超时时间
        
        Returns:
            下载文件的路径
        
        使用方法：
            filepath = wait_helper.wait_for_download(
                lambda: page.click("#download-btn")
            )
            print(f"文件已下载到: {filepath}")
        """
        self.logger.info("等待文件下载...")
        
        with self.page.expect_download(timeout=timeout) as download_info:
            trigger_action()
        
        download = download_info.value
        
        # 等待下载完成并保存
        path = download.path()
        self.logger.info(f"文件已下载: {download.suggested_filename}")
        
        return path
    
    def wait_for_navigation(
        self,
        trigger_action: Callable[[], None],
        url_pattern: Optional[str] = None,
        timeout: int = 30000
    ) -> None:
        """
        等待页面导航完成
        
        Args:
            trigger_action: 触发导航的操作
            url_pattern: 期望的 URL 模式
            timeout: 超时时间
        
        使用方法：
            wait_helper.wait_for_navigation(
                lambda: page.click("#go-to-dashboard"),
                url_pattern="**/dashboard"
            )
        """
        self.logger.info("等待页面导航...")
        
        if url_pattern:
            with self.page.expect_navigation(
                url=url_pattern,
                timeout=timeout
            ):
                trigger_action()
        else:
            with self.page.expect_navigation(timeout=timeout):
                trigger_action()
        
        self.logger.info(f"导航完成，当前 URL: {self.page.url}")
