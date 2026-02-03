# Playwright UI 自动化测试框架

一个功能完善、结构清晰的 Playwright UI 自动化测试框架，基于 Python + pytest 构建。

## 📁 项目结构

```
Playwright_Ui/
├── config/                          # 配置管理模块
│   ├── __init__.py                 # 模块初始化
│   ├── settings.py                 # 全局配置（浏览器、超时、路径等）
│   ├── env_config.py               # 环境配置加载器
│   └── environments/               # 环境配置文件目录
│       ├── dev.yaml                # 开发环境配置
│       ├── test.yaml               # 测试环境配置
│       └── prod.yaml               # 生产环境配置
│
├── pages/                          # Page Object Model (POM)
│   ├── __init__.py                 # 模块初始化
│   ├── base_page.py                # 基础页面类（所有页面的父类）
│   ├── login_page.py               # 登录页面
│   └── home_page.py                # 首页
│
├── utils/                          # 工具类模块
│   ├── __init__.py                 # 模块初始化
│   ├── logger.py                   # 日志管理（分级日志、彩色输出）
│   ├── data_loader.py              # 数据加载（YAML、JSON）
│   ├── wait_helper.py              # 等待助手（自定义等待、重试机制）
│   ├── screenshot_helper.py        # 截图助手（失败截图、元素截图）
│   └── allure_helper.py            # Allure 报告增强
│
├── data/                           # 测试数据目录
│   ├── login_data.yaml             # 登录测试数据
│   ├── search_data.yaml            # 搜索测试数据
│   └── common_data.yaml            # 通用测试数据
│
├── tests/                          # 测试用例目录
│   ├── __init__.py                 # 模块初始化
│   ├── test_demo.py                # 演示测试（框架功能展示）
│   ├── test_login.py               # 登录功能测试
│   └── test_search.py              # 搜索功能测试
│
├── reports/                        # 测试报告目录（自动创建）
│   └── allure-results/             # Allure 报告数据
├── logs/                           # 日志文件目录（自动创建）
├── screenshots/                    # 截图文件目录（自动创建）
├── videos/                         # 录屏文件目录（自动创建）
├── har/                            # HAR 网络日志目录（自动创建）
│
├── conftest.py                     # pytest 全局配置和 fixtures
├── pytest.ini                      # pytest 配置文件
├── .env                            # 环境变量配置
├── requirements.txt                # 项目依赖
└── README.md                       # 项目说明文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install
```

### 2. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_demo.py -v

# 运行冒烟测试
pytest -m smoke -v

# 使用有头模式（显示浏览器窗口）
pytest tests/test_demo.py -v --headed

# 使用慢动作模式调试
pytest tests/test_demo.py -v --headed --slow-mo=1000
```

### 3. 生成测试报告

```bash
# 运行测试并生成 Allure 报告数据
pytest --alluredir=reports/allure-results

# 启动 Allure 报告服务
allure serve reports/allure-results

# 或生成静态报告
allure generate reports/allure-results -o reports/allure-report --clean
```

## 🎯 核心功能

### 1. Page Object Model (POM)

框架采用 POM 设计模式，将页面元素和操作封装在独立的类中：

```python
# pages/login_page.py
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-btn")
    
    def login(self, username: str, password: str):
        """执行登录操作"""
        self.fill_input(self.username_input, username)
        self.fill_input(self.password_input, password)
        self.click_element(self.login_button)
```

**在测试中使用：**

```python
def test_login(page):
    login_page = LoginPage(page)
    login_page.navigate_to_login("https://example.com")
    login_page.login("admin", "password123")
    assert login_page.is_login_successful()
```

### 2. 配置管理

#### 全局配置 (config/settings.py)

```python
from config.settings import Settings

# 获取浏览器配置
browser_type = Settings.BROWSER_TYPE  # chromium/firefox/webkit
headless = Settings.HEADLESS          # True/False

# 获取超时配置
timeout = Settings.DEFAULT_TIMEOUT    # 30000ms
nav_timeout = Settings.NAVIGATION_TIMEOUT  # 60000ms

# 获取路径配置
screenshots_dir = Settings.SCREENSHOTS_DIR
```

#### 环境配置 (config/env_config.py)

```python
from config.env_config import EnvConfig

# 加载当前环境配置（默认 test）
config = EnvConfig()

# 获取配置项
base_url = config.base_url
username = config.get("credentials.username")
api_key = config.get("api.api_key")

# 指定环境加载
prod_config = EnvConfig("prod")
```

#### 环境变量 (.env)

```bash
# 切换环境
ENV=test

# 浏览器配置
BROWSER=chromium
HEADLESS=true
SLOW_MO=0

# 超时配置
DEFAULT_TIMEOUT=30000
```

### 3. 数据驱动测试

#### 从 YAML 加载数据

```yaml
# data/login_data.yaml
login_cases:
  - id: "valid_login"
    username: "admin"
    password: "admin123"
    expected: "success"
  - id: "invalid_password"
    username: "admin"
    password: "wrong"
    expected: "error"
```

```python
from utils.data_loader import DataLoader

loader = DataLoader()
login_data = loader.load_yaml("login_data.yaml")
cases = loader.get_parametrize_data("login_data.yaml", "login_cases")
```

#### 参数化测试

```python
import pytest

@pytest.mark.parametrize(
    "test_case",
    [
        {"id": "case_1", "input": "hello", "expected": True},
        {"id": "case_2", "input": "", "expected": False},
    ],
    ids=lambda x: x["id"]
)
def test_with_data(test_case):
    assert bool(test_case["input"]) == test_case["expected"]
```

### 4. 日志系统

```python
from utils.logger import Logger

logger = Logger("MyTest")

# 不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")

# 测试步骤记录
logger.step("开始登录")
logger.test_start("test_login")
logger.test_end("test_login", passed=True)
```

### 5. 等待机制

```python
from utils.wait_helper import WaitHelper

wait_helper = WaitHelper(page)

# 自定义条件等待
wait_helper.wait_for_condition(
    lambda: page.locator("#result").count() > 0,
    timeout=10000,
    message="等待搜索结果"
)

# 等待元素数量
wait_helper.wait_for_element_count(
    page.locator(".item"),
    expected_count=5,
    comparison=">="
)

# 等待文本变化
new_text = wait_helper.wait_for_text_change(
    page.locator("#counter"),
    original_text="0"
)

# 带重试的操作
wait_helper.retry_on_failure(
    lambda: page.click("#flaky-button"),
    max_retries=3
)
```

### 6. 截图功能

```python
from utils.screenshot_helper import ScreenshotHelper

screenshot_helper = ScreenshotHelper(page)

# 截取完整页面
screenshot_helper.capture_full_page("homepage")

# 截取可视区域
screenshot_helper.capture_viewport("current_view")

# 截取指定元素
screenshot_helper.capture_element(
    page.locator("#chart"),
    "sales_chart"
)

# 失败时截图（自动集成到 Allure）
screenshot_helper.capture_on_failure(test_name="test_login")
```

### 7. Allure 报告集成

```python
import allure
from utils.allure_helper import AllureHelper, allure_step

# 使用装饰器
@allure.feature("用户认证")
@allure.story("登录功能")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("验证用户登录成功")
def test_login():
    pass

# 使用 with 语句
with allure.step("输入用户名"):
    page.fill("#username", "admin")

# 附加信息
helper = AllureHelper()
helper.attach_json("API响应", response_data)
helper.attach_text("SQL查询", query)
```

## 🏷️ 测试标记

框架预定义了以下测试标记：

| 标记 | 说明 | 运行命令 |
|------|------|----------|
| `@pytest.mark.smoke` | 冒烟测试 | `pytest -m smoke` |
| `@pytest.mark.regression` | 回归测试 | `pytest -m regression` |
| `@pytest.mark.slow` | 慢速测试 | `pytest -m slow` |
| `@pytest.mark.wip` | 开发中 | `pytest -m wip` |
| `@pytest.mark.login` | 登录相关 | `pytest -m login` |
| `@pytest.mark.search` | 搜索相关 | `pytest -m search` |

**组合使用：**

```bash
# 运行冒烟测试或回归测试
pytest -m "smoke or regression"

# 排除慢速测试
pytest -m "not slow"

# 运行登录相关的冒烟测试
pytest -m "smoke and login"
```

## 📋 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--browser` | 浏览器类型 | `--browser=firefox` |
| `--headed` | 有头模式 | `--headed` |
| `--env` | 测试环境 | `--env=prod` |
| `--base-url` | 基础URL | `--base-url=https://example.com` |
| `--slow-mo` | 慢动作延迟 | `--slow-mo=1000` |

**示例：**

```bash
# 使用 Firefox 在生产环境运行
pytest --browser=firefox --env=prod

# 有头模式带慢动作调试
pytest --headed --slow-mo=500

# 指定基础URL
pytest --base-url=https://staging.example.com
```

## 🔧 Fixtures 说明

框架在 `conftest.py` 中定义了以下常用 fixtures：

| Fixture | Scope | 说明 |
|---------|-------|------|
| `page` | function | 干净的页面实例 |
| `context` | function | 浏览器上下文 |
| `browser` | session | 浏览器实例 |
| `base_url` | session | 基础URL |
| `env_config` | session | 环境配置 |
| `data_loader` | session | 数据加载器 |
| `screenshot_helper` | function | 截图助手 |
| `login_data` | session | 登录测试数据 |
| `search_data` | session | 搜索测试数据 |

**使用示例：**

```python
def test_login(page, base_url, login_data):
    """
    page: 自动创建的页面实例
    base_url: 从环境配置获取的基础URL
    login_data: 从 YAML 加载的登录数据
    """
    page.goto(f"{base_url}/login")
    username = login_data["valid_credentials"]["username"]
    # ...
```

## 📊 查看测试报告

### Allure 报告

```bash
# 方式1：启动本地服务查看
allure serve reports/allure-results

# 方式2：生成静态HTML报告
allure generate reports/allure-results -o reports/allure-report --clean
# 然后用浏览器打开 reports/allure-report/index.html
```

### 日志文件

测试日志自动保存在 `logs/` 目录：
- `logs/test_2024-01-15.log` - 按日期分割的日志文件
- `logs/pytest.log` - pytest 运行日志

### 截图和录屏

- 截图保存在 `screenshots/` 目录
- 录屏（如启用）保存在 `videos/` 目录
- HAR 网络日志保存在 `har/` 目录

## 🔍 常见问题

### Q: 如何在 CI/CD 中运行？

```yaml
# GitHub Actions 示例
- name: Run Tests
  run: |
    pip install -r requirements.txt
    playwright install
    pytest --alluredir=reports/allure-results
```

### Q: 如何添加新的测试页面？

1. 在 `pages/` 目录创建新的页面类，继承 `BasePage`
2. 定义页面元素和操作方法
3. 在测试中导入使用

### Q: 如何添加新的测试数据？

1. 在 `data/` 目录创建 YAML 或 JSON 文件
2. 使用 `DataLoader` 加载数据
3. 或在 `conftest.py` 中添加新的 fixture

## 📝 开发规范

1. **命名规范**
   - 测试文件：`test_*.py`
   - 测试类：`Test*`
   - 测试方法：`test_*`
   - 页面类：`*Page`

2. **注释规范**
   - 每个模块、类、方法都要有文档字符串
   - 复杂逻辑添加行内注释

3. **提交规范**
   - 提交前运行 `pytest -m smoke` 确保冒烟测试通过
   - 使用有意义的提交信息

## 📄 License

MIT License
