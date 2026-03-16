# BasePage 简述

## 概述

`BasePage` 是页面对象的基类，封装了通用的页面操作方法、等待机制、异常处理和日志记录。所有具体页面类都应继承此类。

---

## 1. 导航方法

| 方法 | 说明 |
|------|------|
| `navigate_to(url)` | 导航到指定 URL |
| `refresh()` | 刷新页面 |
| `go_back()` | 返回上一页 |
| `get_current_url()` | 获取当前 URL |
| `get_title()` | 获取页面标题 |

---

## 2. 元素交互方法

| 方法 | 说明 |
|------|------|
| `click_element(locator, timeout, force, multi)` | 点击元素 |
| `double_click_element(...)` | 双击元素 |
| `fill_element(locator, text, clear_first, press_enter, ...)` | 输入文本 |
| `clear_input(...)` | 清空输入框 |
| `upload_file_via_chooser(upload_trigger, file_path, ...)` | 通过 FileChooser 上传文件 |
| `select_option(locator, value/label/index, ...)` | 选择下拉选项 |
| `check_checkbox(locator, check, force, ...)` | 勾选/取消勾选复选框 |
| `hover_element(...)` | 悬停 |
| `drag_element_to(source, target, ...)` | 拖拽元素 |

---

## 3. 获取元素信息

| 方法 | 说明 |
|------|------|
| `get_text(locator, multi)` | 获取元素文本 |
| `get_input_value(...)` | 获取输入框值 |
| `get_attribute(locator, attribute, multi)` | 获取属性值 |
| `get_element_count(locator)` | 获取匹配元素数量 |
| `has_text(text, scope, exact)` | 判断页面/iframe 是否包含某段文字 |

---

## 4. 元素状态检查

| 方法 | 说明 |
|------|------|
| `is_visible(locator, timeout, multi)` | 是否可见 |
| `is_enabled(...)` | 是否启用 |
| `is_checked(...)` | 是否选中 |

---

## 5. 等待方法

| 方法 | 说明 |
|------|------|
| `wait_for_element_visible(...)` | 等待元素可见 |
| `wait_for_element_hidden(...)` | 等待元素隐藏 |
| `wait_for_load_state(state)` | 等待 load / domcontentloaded / networkidle |
| `wait_for_url(url_part, timeout)` | 等待 URL 包含某段文本 |
| `wait_for_timeout(ms)` | 强制等待（不推荐） |

---

## 6. 截图与弹窗

| 方法 | 说明 |
|------|------|
| `take_screenshot(name)` | 全页截图并附加到 Allure |
| `handle_alert(accept, prompt_text)` | 处理 alert / confirm / prompt |

---

## 7. 辅助能力

- **`multi` 参数**：`None` / `"first"` / `"last"` / `int`，用于多元素时指定目标
- **`_resolve_locator(locator, multi)`**：按 `multi` 解析定位器
- **`_get_locator(locator)`**：字符串转 Locator
- **`get_position_in_element(locator, x_ratio, y_ratio)`**：获取元素内相对坐标，用于拖拽

---

## 8. PageAssertions 断言类

| 方法 | 说明 |
|------|------|
| `assert_title_contains(expected)` | 断言标题包含 |
| `assert_url_contains(expected)` | 断言 URL 包含 |
| `assert_element_visible(locator)` | 断言元素可见 |
| `assert_element_has_text(locator, expected)` | 断言元素包含文本 |
| `assert_input_value(locator, expected)` | 断言输入框值 |

---

## 9. 设计要点

- 所有交互方法返回 `self`，支持链式调用
- 使用 `@allure.step` 记录步骤
- 失败时自动截图
- 统一通过 `_resolve_locator` 支持 `multi` 参数
