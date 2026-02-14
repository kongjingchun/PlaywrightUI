# ========================================
# 基础页面类 - BasePage
# ========================================
# 这是所有页面对象的基类，封装了通用的页面操作方法。
# 所有具体的页面类都应该继承此类。
#
# 主要功能：
# 1. 封装通用的元素交互方法（点击、输入、选择等）
# 2. 提供健壮的等待机制
# 3. 统一的异常处理和日志记录
# 4. 截图和调试支持
# ========================================

from config.settings import Settings
from utils.logger import Logger
import allure
import re
from playwright.sync_api import Page, Locator, expect
from typing import Optional, List, Union, Literal

# 多元素索引类型：None 不处理；"first"/"last" 或 int 取第 n 个
MultiIndex = Optional[Union[Literal["first", "last"], int]]


class BasePage:
    """
    基础页面类

    所有页面对象都应继承此类，它提供了：
    - 通用的元素定位和交互方法
    - 等待机制
    - 异常处理
    - 日志记录
    - 截图功能

    使用方法：
        class LoginPage(BasePage):
            def __init__(self, page: Page):
                super().__init__(page)
                # 定义页面特有的元素定位器
                self.username_input = page.locator("#username")

            def login(self, username: str, password: str):
                self.fill_element(self.username_input, username)
                # ...
    """

    def __init__(self, page: Page):
        """
        初始化基础页面

        Args:
            page: Playwright 的 Page 对象
        """
        # 保存 page 对象，子类可以通过 self.page 访问
        self.page = page

        # 创建日志记录器，使用类名作为日志名称
        self.logger = Logger(self.__class__.__name__)

        # 设置默认超时时间
        self.page.set_default_timeout(Settings.DEFAULT_TIMEOUT)
        self.page.set_default_navigation_timeout(Settings.NAVIGATION_TIMEOUT)

    # ==================== 导航方法 ====================

    @allure.step("导航到: {url}")
    def navigate_to(self, url: str) -> None:
        """
        导航到指定 URL

        Args:
            url: 目标 URL 地址

        使用方法：
            page.navigate_to("https://example.com/login")
        """
        self.logger.info(f"导航到: {url}")
        try:
            self.page.goto(url, wait_until="domcontentloaded")
            self.logger.info(f"导航成功，当前URL: {self.page.url}")
        except Exception as e:
            self.logger.error(f"导航失败: {url}, 错误: {str(e)}")
            self.take_screenshot("navigation_failed")
            raise

    @allure.step("刷新页面")
    def refresh(self) -> None:
        """刷新当前页面"""
        self.logger.info("刷新页面")
        self.page.reload(wait_until="domcontentloaded")

    @allure.step("返回上一页")
    def go_back(self) -> None:
        """返回上一页"""
        self.logger.info("返回上一页")
        self.page.go_back()

    def get_current_url(self) -> str:
        """
        获取当前页面 URL

        Returns:
            当前页面的 URL 字符串
        """
        return self.page.url

    def get_title(self) -> str:
        """
        获取页面标题

        Returns:
            页面 title 标签的内容
        """
        return self.page.title()

    # ==================== 元素交互方法 ====================

    @allure.step("点击元素")
    def click_element(
        self,
        locator: Union[Locator, str],
        timeout: Optional[int] = None,
        force: bool = False,
        multi: MultiIndex = None
    ) -> "BasePage":
        """
        点击元素（带有健壮的等待和错误处理，支持链式调用）

        该方法会：
        1. 等待元素可见
        2. 等待元素可点击
        3. 执行点击操作
        4. 如果失败，记录错误并截图

        Args:
            locator: 元素定位器（Locator 对象或选择器字符串）
            timeout: 超时时间（毫秒），不传则使用默认值
            force: 是否强制点击（跳过可操作性检查）
            multi: 多元素时取哪个，默认 None 不处理；"first" 取第一个；"last" 取最后一个；数字取第几个（从 0 开始）

        Returns:
            self，支持链式调用

        使用方法：
            self.click_element(self.submit_button)
            self.click_element(btn_locator, multi="last")
            self.click_element(btn_locator, multi=2)  # 取第 3 个
        """
        element = self._resolve_locator(locator, multi)

        try:
            # 等待元素可见（确保元素已加载到DOM并显示）
            element.wait_for(state="visible", timeout=timeout)

            self.logger.info(f"点击元素: {self._locator_to_log_str(locator)}")

            # 执行点击操作
            element.click(timeout=timeout, force=force)

        except Exception as e:
            self.logger.error(f"点击元素失败: {self._locator_to_log_str(locator)}, 错误: {str(e)}")
            self.take_screenshot("click_failed")
            raise

        return self

    @allure.step("双击元素")
    def double_click_element(
        self,
        locator: Union[Locator, str],
        timeout: Optional[int] = None,
        multi: MultiIndex = None
    ) -> "BasePage":
        """
        双击元素（支持链式调用）

        Args:
            locator: 元素定位器
            timeout: 超时时间
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        try:
            element.wait_for(state="visible", timeout=timeout)
            self.logger.info(f"双击元素: {self._locator_to_log_str(locator)}")
            element.dblclick(timeout=timeout)
        except Exception as e:
            self.logger.error(f"双击元素失败: {self._locator_to_log_str(locator)}, 错误: {str(e)}")
            self.take_screenshot("double_click_failed")
            raise

        return self

    @allure.step("在输入框中填入: {text}")
    def fill_element(
        self,
        locator: Union[Locator, str],
        text: Union[str, int, float, None],
        clear_first: bool = True,
        timeout: Optional[int] = None,
        multi: MultiIndex = None
    ) -> "BasePage":
        """
        在输入框中填入文本（支持链式调用）

        Args:
            locator: 输入框元素定位器
            text: 要输入的文本
            clear_first: 是否先清空输入框（默认True）
            timeout: 超时时间
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        # Playwright fill() 要求字符串，兼容传入数字（如 API 返回的 user_id）
        text_str = str(text) if text is not None else ""

        try:
            element.wait_for(state="visible", timeout=timeout)

            if clear_first:
                # 使用 fill() 方法会自动清空再输入
                self.logger.info(f"填入文本: {text_str}")
                element.fill(text_str, timeout=timeout)
            else:
                # 使用 type() 方法追加输入
                self.logger.info(f"追加输入文本: {text_str}")
                element.type(text_str, timeout=timeout)

        except Exception as e:
            self.logger.error(f"输入文本失败: {text_str}, 错误: {str(e)}")
            self.take_screenshot("fill_element_failed")
            raise

        return self

    @allure.step("清空输入框")
    def clear_input(self, locator: Union[Locator, str], multi: MultiIndex = None) -> "BasePage":
        """
        清空输入框内容（支持链式调用）

        Args:
            locator: 输入框元素定位器
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        self.logger.info(f"清空输入框: {self._locator_to_log_str(locator)}")
        element.clear()
        return self

    @allure.step("通过 FileChooser 上传文件")
    def upload_file_via_chooser(
        self,
        upload_trigger: Union[Locator, str],
        file_path: Union[str, List[str]],
        multi: MultiIndex = None
    ) -> "BasePage":
        """
        通过 FileChooser 上传文件。先监听 filechooser，再点击触发元素。
        适用于 Element UI el-upload 等“点击区域”触发的上传（非直接 input[type=file]）。

        Args:
            upload_trigger: 上传触发元素定位器（可来自 page 或 frame）
            file_path: 文件路径，或路径列表（多文件）

        Returns:
            self，支持链式调用
        """
        trigger = self._resolve_locator(upload_trigger, multi)
        with self.page.expect_file_chooser() as fc_info:
            trigger.click()
        fc_info.value.set_files(file_path)
        self.logger.info(f"已通过 FileChooser 设置文件: {file_path}")
        return self

    @allure.step("选择下拉选项: {value}")
    def select_option(
        self,
        locator: Union[Locator, str],
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None,
        multi: MultiIndex = None
    ) -> "BasePage":
        """
        选择下拉框选项（支持链式调用）

        Args:
            locator: 下拉框元素定位器
            value: 按 value 属性选择
            label: 按显示文本选择
            index: 按索引选择（从0开始）
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)

        try:
            if value is not None:
                self.logger.info(f"按value选择: {value}")
                element.select_option(value=value)
            elif label is not None:
                self.logger.info(f"按label选择: {label}")
                element.select_option(label=label)
            elif index is not None:
                self.logger.info(f"按index选择: {index}")
                element.select_option(index=index)
            else:
                raise ValueError("必须提供 value、label 或 index 之一")
        except Exception as e:
            self.logger.error(f"选择下拉选项失败, 错误: {str(e)}")
            self.take_screenshot("select_option_failed")
            raise

        return self

    @allure.step("勾选复选框")
    def check_checkbox(
        self,
        locator: Union[Locator, str],
        check: bool = True,
        multi: MultiIndex = None
    ) -> "BasePage":
        """
        勾选或取消勾选复选框（支持链式调用）

        Args:
            locator: 复选框元素定位器
            check: True=勾选，False=取消勾选
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        self.logger.info(f"{'勾选' if check else '取消勾选'}复选框")

        if check:
            element.check()
        else:
            element.uncheck()

        return self

    @allure.step("悬停在元素上")
    def hover_element(self, locator: Union[Locator, str], multi: MultiIndex = None) -> "BasePage":
        """
        鼠标悬停在元素上（支持链式调用）

        Args:
            locator: 元素定位器
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        self.logger.info(f"悬停在元素: {self._locator_to_log_str(locator)}")
        element.hover()
        return self

    # ==================== 获取元素信息 ====================

    def get_text(self, locator: Union[Locator, str], multi: MultiIndex = None) -> str:
        """
        获取元素的文本内容

        Args:
            locator: 元素定位器
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        text = element.inner_text()
        self.logger.info(f"获取元素文本: {self._locator_to_log_str(locator)}, 文本: {text}")
        return text

    def get_input_value(self, locator: Union[Locator, str], multi: MultiIndex = None) -> str:
        """
        获取输入框的值

        Args:
            locator: 输入框元素定位器
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        return element.input_value()

    def get_attribute(
        self,
        locator: Union[Locator, str],
        attribute: str,
        multi: MultiIndex = None
    ) -> Optional[str]:
        """
        获取元素的属性值

        Args:
            locator: 元素定位器
            attribute: 属性名称
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        return element.get_attribute(attribute)

    def get_element_count(self, locator: Union[Locator, str]) -> int:
        """
        获取匹配元素的数量

        Args:
            locator: 元素定位器

        Returns:
            匹配的元素数量
        """
        element = self._get_locator(locator)
        return element.count()

    # ==================== 元素状态检查 ====================

    def is_visible(
        self,
        locator: Union[Locator, str],
        timeout: Optional[int] = None,
        multi: MultiIndex = None
    ) -> bool:
        """
        检查元素是否可见

        Args:
            locator: 元素定位器
            timeout: 超时时间
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        try:
            element.wait_for(state="visible", timeout=timeout or 5000)
            return True
        except BaseException:
            return False

    def is_enabled(self, locator: Union[Locator, str], multi: MultiIndex = None) -> bool:
        """
        检查元素是否启用（非禁用状态）

        Args:
            locator: 元素定位器
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        return element.is_enabled()

    def is_checked(self, locator: Union[Locator, str], multi: MultiIndex = None) -> bool:
        """
        检查复选框/单选框是否被选中

        Args:
            locator: 元素定位器
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        return element.is_checked()

    # ==================== 等待方法 ====================

    @allure.step("等待元素可见")
    def wait_for_element_visible(
        self,
        locator: Union[Locator, str],
        timeout: Optional[int] = None,
        multi: MultiIndex = None
    ) -> Locator:
        """
        等待元素变为可见状态

        Args:
            locator: 元素定位器
            timeout: 超时时间
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        self.logger.info(f"等待元素可见: {self._locator_to_log_str(locator)}")
        element.wait_for(state="visible", timeout=timeout)
        return element

    @allure.step("等待元素隐藏")
    def wait_for_element_hidden(
        self,
        locator: Union[Locator, str],
        timeout: Optional[int] = None,
        multi: MultiIndex = None
    ) -> None:
        """
        等待元素隐藏或从DOM中移除

        Args:
            locator: 元素定位器
            timeout: 超时时间
            multi: 多元素时取哪个，None/"first"/"last"/int
        """
        element = self._resolve_locator(locator, multi)
        self.logger.info(f"等待元素隐藏: {self._locator_to_log_str(locator)}")
        element.wait_for(state="hidden", timeout=timeout)

    @allure.step("等待页面加载完成")
    def wait_for_load_state(self, state: str = "load") -> None:
        """
        等待页面达到指定的加载状态

        Args:
            state: 加载状态，可选值：
                   - "load": 等待 load 事件触发
                   - "domcontentloaded": 等待 DOMContentLoaded 事件
                   - "networkidle": 等待网络空闲（至少500ms无网络请求）
        """
        self.logger.info(f"等待页面加载状态: {state}")
        self.page.wait_for_load_state(state)

    @allure.step("等待URL包含: {url_part}")
    def wait_for_url(self, url_part: str, timeout: Optional[int] = None) -> None:
        """
        等待URL包含指定的字符串

        Args:
            url_part: URL中应包含的字符串
            timeout: 超时时间
        """
        self.logger.info(f"等待URL包含: {url_part}")
        self.page.wait_for_url(f"**{url_part}**", timeout=timeout)

    def wait_for_timeout(self, milliseconds: int) -> None:
        """
        强制等待指定时间（不推荐使用，仅在特殊情况下使用）

        ⚠️ 警告：应尽量避免使用硬编码等待，
        优先使用 wait_for_element_visible 等智能等待方法。

        Args:
            milliseconds: 等待时间（毫秒）
        """
        self.logger.warning(f"强制等待 {milliseconds}ms（建议使用智能等待替代）")
        self.page.wait_for_timeout(milliseconds)

    # ==================== 截图方法 ====================

    @allure.step("截取屏幕截图")
    def take_screenshot(self, name: str = "screenshot") -> str:
        """
        截取当前页面截图

        截图会保存到 screenshots 目录，并附加到 Allure 报告。

        Args:
            name: 截图文件名（不含扩展名）

        Returns:
            截图文件的完整路径
        """
        import datetime

        # 确保截图目录存在
        Settings.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        # 生成带时间戳的文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = Settings.SCREENSHOTS_DIR / filename

        # 截图
        self.page.screenshot(path=str(filepath), full_page=True)
        self.logger.info(f"截图已保存: {filepath}")

        # 附加到 Allure 报告
        allure.attach.file(
            str(filepath),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )

        return str(filepath)

    # ==================== 弹窗处理 ====================

    @allure.step("处理 Alert 弹窗")
    def handle_alert(self, accept: bool = True, prompt_text: Optional[str] = None) -> str:
        """
        处理 JavaScript 弹窗（alert/confirm/prompt）

        Args:
            accept: True=点击确定，False=点击取消
            prompt_text: 如果是 prompt 弹窗，要输入的文本

        Returns:
            弹窗的消息文本
        """
        def handle_dialog(dialog):
            self.logger.info(f"检测到弹窗，类型: {dialog.type}, 消息: {dialog.message}")
            if accept:
                if prompt_text and dialog.type == "prompt":
                    dialog.accept(prompt_text)
                else:
                    dialog.accept()
            else:
                dialog.dismiss()

        self.page.on("dialog", handle_dialog)
        return ""

    # ==================== iframe 处理 ====================

    def switch_to_frame(self, frame_locator: str) -> "BasePage":
        """
        切换到 iframe

        Args:
            frame_locator: iframe 的选择器

        Returns:
            返回 self 以支持链式调用

        使用方法：
            # 切换到 iframe 并操作其中的元素
            self.switch_to_frame("#my-iframe")
            self.click_element("#btn-in-iframe")
        """
        self.logger.info(f"切换到 iframe: {frame_locator}")
        frame = self.page.frame_locator(frame_locator)
        return frame

    # ==================== 私有辅助方法 ====================

    def _get_locator(self, locator: Union[Locator, str]) -> Locator:
        """
        统一处理定位器

        如果传入的是字符串，转换为 Locator 对象。
        如果已经是 Locator 对象，直接返回。

        Args:
            locator: 字符串选择器或 Locator 对象

        Returns:
            Locator 对象
        """
        if isinstance(locator, str):
            return self.page.locator(locator)
        return locator

    def _resolve_locator(
        self,
        locator: Union[Locator, str],
        multi: MultiIndex
    ) -> Locator:
        """
        根据 multi 参数缩小多元素定位器

        Args:
            locator: 元素定位器
            multi: None 不处理；"first" 取第一个；"last" 取最后一个；int 取第 n 个（从 0 开始）

        Returns:
            Locator
        """
        element = self._get_locator(locator)
        if multi is None:
            return element
        if multi == "first":
            return element.first
        if multi == "last":
            return element.last
        if isinstance(multi, int):
            return element.nth(multi)
        return element

    def _locator_to_log_str(self, locator: Union[Locator, str]) -> str:
        """
        提取定位器的 selector 部分用于日志（不包含 frame 信息），
        并将 \\uXXXX 转义解码为实际字符以解决日志乱码。
        """
        if isinstance(locator, str):
            return self._decode_unicode_escapes(locator)
        s = str(locator)
        m = re.search(r'selector="([^"]*)"', s) or re.search(r"selector='([^']*)'", s)
        result = m.group(1) if m else s
        return self._decode_unicode_escapes(result)

    def _decode_unicode_escapes(self, s: str) -> str:
        """将 \\uXXXX 转义序列解码为实际字符，便于日志可读"""
        def _replace(match: re.Match) -> str:
            try:
                return chr(int(match.group(1), 16))
            except (ValueError, OverflowError):
                return match.group(0)
        return re.sub(r'\\u([0-9a-fA-F]{4})', _replace, s)


# ==================== 断言辅助类 ====================

class PageAssertions:
    """
    页面断言辅助类

    封装常用的页面断言方法，提供更清晰的断言语义。

    使用方法：
        assertions = PageAssertions(page)
        assertions.assert_title_contains("登录")
        assertions.assert_url_contains("/login")
        assertions.assert_element_visible("#username")
    """

    def __init__(self, page: Page):
        """
        初始化断言辅助类

        Args:
            page: Playwright 的 Page 对象
        """
        self.page = page
        self.logger = Logger("PageAssertions")

    @allure.step("断言：页面标题包含 '{expected}'")
    def assert_title_contains(self, expected: str) -> None:
        """
        断言页面标题包含指定文本

        Args:
            expected: 期望标题包含的文本
        """
        self.logger.info(f"断言标题包含: {expected}")
        expect(self.page).to_have_title(expected, timeout=Settings.EXPECT_TIMEOUT)

    @allure.step("断言：URL包含 '{expected}'")
    def assert_url_contains(self, expected: str) -> None:
        """
        断言当前URL包含指定文本

        Args:
            expected: 期望URL包含的文本
        """
        self.logger.info(f"断言URL包含: {expected}")
        expect(self.page).to_have_url(f"**{expected}**", timeout=Settings.EXPECT_TIMEOUT)

    @allure.step("断言：元素可见")
    def assert_element_visible(self, locator: Union[Locator, str]) -> None:
        """
        断言元素可见

        Args:
            locator: 元素定位器
        """
        element = locator if isinstance(locator, Locator) else self.page.locator(locator)
        self.logger.info(f"断言元素可见: {self._locator_to_log_str(locator)}")
        expect(element).to_be_visible(timeout=Settings.EXPECT_TIMEOUT)

    @allure.step("断言：元素包含文本 '{expected}'")
    def assert_element_has_text(self, locator: Union[Locator, str], expected: str) -> None:
        """
        断言元素包含指定文本

        Args:
            locator: 元素定位器
            expected: 期望的文本
        """
        element = locator if isinstance(locator, Locator) else self.page.locator(locator)
        self.logger.info(f"断言元素包含文本: {expected}")
        expect(element).to_contain_text(expected, timeout=Settings.EXPECT_TIMEOUT)

    @allure.step("断言：输入框值为 '{expected}'")
    def assert_input_value(self, locator: Union[Locator, str], expected: str) -> None:
        """
        断言输入框的值

        Args:
            locator: 输入框定位器
            expected: 期望的值
        """
        element = locator if isinstance(locator, Locator) else self.page.locator(locator)
        self.logger.info(f"断言输入框值: {expected}")
        expect(element).to_have_value(expected, timeout=Settings.EXPECT_TIMEOUT)
