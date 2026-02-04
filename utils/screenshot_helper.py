# ========================================
# 截图助手模块
# ========================================
# 提供截图和视频录制管理功能，包括：
# - 失败自动截图
# - 元素截图
# - 全页面截图
# - 截图对比（可选）
# ========================================

from playwright.sync_api import Page, Locator
from pathlib import Path
from datetime import datetime
from typing import Optional
import allure
from config.settings import Settings
from utils.logger import Logger


class ScreenshotHelper:
    """
    截图助手类
    
    提供各种截图功能，并自动集成到 Allure 报告。
    
    使用方法：
        screenshot_helper = ScreenshotHelper(page)
        
        # 截取全页面
        screenshot_helper.capture_full_page("homepage")
        
        # 截取可视区域
        screenshot_helper.capture_viewport("visible_area")
        
        # 截取指定元素
        screenshot_helper.capture_element(page.locator("#chart"), "chart")
    """
    
    def __init__(self, page: Page, output_dir: Optional[Path] = None):
        """
        初始化截图助手
        
        Args:
            page: Playwright 的 Page 对象
            output_dir: 截图保存目录，不传则使用默认目录
        """
        self.page = page
        self.output_dir = output_dir or Settings.SCREENSHOTS_DIR
        self.logger = Logger("ScreenshotHelper")
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, name: str, extension: str = "png") -> Path:
        """
        生成带时间戳的文件名
        
        Args:
            name: 截图名称
            extension: 文件扩展名
        
        Returns:
            完整的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{name}_{timestamp}.{extension}"
        return self.output_dir / filename
    
    def capture_full_page(
        self, 
        name: str = "full_page",
        attach_to_allure: bool = True
    ) -> str:
        """
        截取完整页面（包括滚动区域）
        
        Args:
            name: 截图名称
            attach_to_allure: 是否附加到 Allure 报告
        
        Returns:
            截图文件路径
        
        使用方法：
            screenshot_helper.capture_full_page("order_page")
        """
        filepath = self._generate_filename(name)
        
        # self.logger.info(f"截取完整页面: {name}")
        
        self.page.screenshot(
            path=str(filepath),
            full_page=True  # 截取完整页面
        )
        
        # self.logger.info(f"截图已保存: {filepath}")
        
        # 附加到 Allure 报告
        if attach_to_allure:
            self._attach_to_allure(filepath, name)
        
        return str(filepath)
    
    def capture_viewport(
        self, 
        name: str = "viewport",
        attach_to_allure: bool = True
    ) -> str:
        """
        截取当前可视区域
        
        只截取浏览器窗口当前显示的内容。
        
        Args:
            name: 截图名称
            attach_to_allure: 是否附加到 Allure 报告
        
        Returns:
            截图文件路径
        """
        filepath = self._generate_filename(name)
        
        # self.logger.info(f"截取可视区域: {name}")
        
        self.page.screenshot(
            path=str(filepath),
            full_page=False  # 只截取可视区域
        )
        
        # self.logger.info(f"截图已保存: {filepath}")
        
        if attach_to_allure:
            self._attach_to_allure(filepath, name)
        
        return str(filepath)
    
    def capture_element(
        self, 
        locator: Locator,
        name: str = "element",
        attach_to_allure: bool = True
    ) -> str:
        """
        截取指定元素
        
        Args:
            locator: 元素定位器
            name: 截图名称
            attach_to_allure: 是否附加到 Allure 报告
        
        Returns:
            截图文件路径
        
        使用方法：
            # 截取图表元素
            screenshot_helper.capture_element(
                page.locator("#sales-chart"),
                "sales_chart"
            )
        """
        filepath = self._generate_filename(name)
        
        # self.logger.info(f"截取元素: {name}")
        
        # 确保元素可见
        locator.wait_for(state="visible", timeout=10000)
        
        # 截取元素
        locator.screenshot(path=str(filepath))
        
        # self.logger.info(f"元素截图已保存: {filepath}")
        
        if attach_to_allure:
            self._attach_to_allure(filepath, name)
        
        return str(filepath)
    
    def capture_on_failure(
        self, 
        name: str = "failure",
        test_name: Optional[str] = None
    ) -> str:
        """
        失败时截图
        
        用于测试失败时自动截图，通常在 conftest.py 的 fixture 中调用。
        
        Args:
            name: 截图名称前缀
            test_name: 测试用例名称
        
        Returns:
            截图文件路径
        
        使用方法（在 conftest.py 中）:
            @pytest.fixture(autouse=True)
            def capture_on_failure(request, page):
                yield
                if request.node.rep_call.failed:
                    screenshot_helper = ScreenshotHelper(page)
                    screenshot_helper.capture_on_failure(
                        test_name=request.node.name
                    )
        """
        # 如果提供了测试名称，添加到文件名中
        if test_name:
            name = f"FAIL_{test_name}"
        else:
            name = f"FAIL_{name}"
        
        self.logger.error(f"测试失败，正在截图: {name}")
        
        # 截取完整页面
        filepath = self.capture_full_page(name, attach_to_allure=True)
        
        return filepath
    
    def capture_with_highlight(
        self,
        locator: Locator,
        name: str = "highlighted",
        highlight_style: str = "border: 3px solid red; background: rgba(255,0,0,0.1);"
    ) -> str:
        """
        截图并高亮指定元素
        
        在截图前给元素添加高亮样式，截图后恢复。
        适用于文档或问题报告，突出显示关键元素。
        
        Args:
            locator: 要高亮的元素定位器
            name: 截图名称
            highlight_style: 高亮样式
        
        Returns:
            截图文件路径
        """
        self.logger.info(f"截取高亮元素: {name}")
        
        # 保存原始样式
        original_style = locator.evaluate("el => el.style.cssText")
        
        try:
            # 添加高亮样式
            locator.evaluate(
                f"el => el.style.cssText = el.style.cssText + '; {highlight_style}'"
            )
            
            # 截图
            filepath = self.capture_viewport(name)
            
        finally:
            # 恢复原始样式
            locator.evaluate(f"el => el.style.cssText = '{original_style}'")
        
        return filepath
    
    def _attach_to_allure(self, filepath: Path, name: str) -> None:
        """
        将截图附加到 Allure 报告
        
        Args:
            filepath: 截图文件路径
            name: 截图名称
        """
        try:
            allure.attach.file(
                str(filepath),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
            self.logger.debug(f"截图已附加到 Allure 报告: {name}")
        except Exception as e:
            self.logger.warning(f"无法附加截图到 Allure: {e}")
    
    def save_page_source(self, name: str = "page_source") -> str:
        """
        保存页面 HTML 源代码
        
        用于调试，保存当前页面的完整 HTML。
        
        Args:
            name: 文件名称
        
        Returns:
            文件路径
        """
        filepath = self._generate_filename(name, extension="html")
        
        self.logger.info(f"保存页面源代码: {name}")
        
        html_content = self.page.content()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"页面源代码已保存: {filepath}")
        
        # 也附加到 Allure
        try:
            allure.attach(
                html_content,
                name=f"{name}.html",
                attachment_type=allure.attachment_type.HTML
            )
        except:
            pass
        
        return str(filepath)
    
    def capture_console_logs(self, name: str = "console_logs") -> str:
        """
        保存浏览器控制台日志
        
        需要在页面加载前设置监听器。
        
        Args:
            name: 文件名称
        
        Returns:
            日志文件路径
        """
        filepath = self._generate_filename(name, extension="txt")
        
        # 注意：这需要在测试开始时就设置监听器
        # 这里只是保存已收集的日志的示例
        self.logger.info(f"保存控制台日志: {name}")
        
        # 这个方法需要配合 conftest.py 中的控制台日志收集使用
        return str(filepath)


class ConsoleLogCollector:
    """
    控制台日志收集器
    
    在测试开始时创建，收集页面的所有控制台输出。
    
    使用方法（在 conftest.py 中）:
        @pytest.fixture
        def console_logs(page):
            collector = ConsoleLogCollector(page)
            yield collector
            collector.save_logs()
    """
    
    def __init__(self, page: Page):
        """
        初始化控制台日志收集器
        
        Args:
            page: Playwright 的 Page 对象
        """
        self.page = page
        self.logs: list = []
        self.logger = Logger("ConsoleLogCollector")
        
        # 设置控制台消息监听器
        page.on("console", self._on_console_message)
    
    def _on_console_message(self, msg):
        """
        处理控制台消息
        
        Args:
            msg: 控制台消息对象
        """
        log_entry = {
            "type": msg.type,
            "text": msg.text,
            "location": msg.location,
        }
        self.logs.append(log_entry)
        
        # 记录到测试日志
        self.logger.debug(f"[Console {msg.type}] {msg.text}")
    
    def get_logs(self, log_type: Optional[str] = None) -> list:
        """
        获取收集的日志
        
        Args:
            log_type: 日志类型过滤（log/warning/error）
        
        Returns:
            日志列表
        """
        if log_type:
            return [log for log in self.logs if log["type"] == log_type]
        return self.logs
    
    def get_errors(self) -> list:
        """获取所有错误日志"""
        return self.get_logs("error")
    
    def save_logs(self, filepath: Optional[str] = None) -> str:
        """
        保存日志到文件
        
        Args:
            filepath: 文件路径，不传则自动生成
        
        Returns:
            日志文件路径
        """
        if not filepath:
            filepath = Settings.LOGS_DIR / f"console_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for log in self.logs:
                f.write(f"[{log['type']}] {log['text']}\n")
        
        self.logger.info(f"控制台日志已保存: {filepath}")
        
        return str(filepath)
    
    def clear(self) -> None:
        """清空已收集的日志"""
        self.logs.clear()
