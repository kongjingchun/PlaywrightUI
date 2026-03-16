# Playwright 定位方式使用指南

本文档整理项目中使用的所有定位方式，并说明**何时应使用**每种方式。推荐优先使用语义化定位器（`get_by_role`、`get_by_placeholder` 等），在无法满足时再使用 CSS/XPath。

---

## 一、定位方式总览

| 定位方式 | 项目中使用频率 | 推荐优先级 | 典型场景 |
|----------|----------------|------------|----------|
| `get_by_role` | 高 | ⭐⭐⭐ 首选 | 按钮、输入框、表格行、下拉选项等 |
| `get_by_placeholder` | 高 | ⭐⭐⭐ 首选 | 带占位符的输入框 |
| `get_by_label` | 中 | ⭐⭐⭐ 首选 | 表单项（配合 label 的输入框、下拉框） |
| `get_by_text` | 高 | ⭐⭐ 次选 | 按可见文本定位（链接、选项、提示文字） |
| `locator()` + CSS | 高 | ⭐ 备选 | 无语义属性时的后备方案 |
| `locator()` + XPath | 中 | ⭐ 备选 | 复杂层级、动态文本、Toast 提示 |
| `frame_locator` | 高 | 必须 | 页面包含 iframe 时 |
| `.filter(has_text=)` | 中 | ⭐⭐ | 在多个相似元素中按文本筛选 |
| `.nth()` / `.first` / `.last` | 高 | 按需 | 多个匹配元素时取第 N 个 |

---

## 二、各定位方式详解

### 1. get_by_role（按角色定位）——首选

**用法**：`page.get_by_role("role", name="可访问名称")`，`name` 可选，支持部分匹配，可加 `exact=True` 精确匹配。

---

#### 1.1 表单控件类（button / textbox / checkbox / radio / combobox / spinbutton / searchbox）

```python
# 按钮 - 最常用
self.iframe.get_by_role("button", name="新建行政班")
self.iframe.get_by_role("button", name="确定")
self.iframe.get_by_role("button", name="保存").last       # 多个同名取最后一个
self.iframe.get_by_role("button", name="创建", exact=True)  # 精确匹配，避免匹配到「创建并编辑」

# 单行文本输入框
self.iframe.get_by_role("textbox", name="行政班名称")
self.iframe.get_by_role("textbox", name="搜索：")
self.iframe.get_by_role("textbox", name="院系名称")
self.iframe.get_by_role("textbox", name="* 姓名")         # 必填项常带 * 前缀

# 复选框
page.get_by_role("checkbox", name="记住我")
page.get_by_role("checkbox", name="Subscribe")

# 单选框
page.get_by_role("radio", name="男")
page.get_by_role("radio", name="选项 A")

# 下拉选择框（可输入可选的 combobox）
self.iframe.get_by_role("combobox", name="选课开始时间")
self.iframe.get_by_role("combobox", name="课程负责人")
self.iframe.get_by_label("新建课程").get_by_role("combobox", name="课程负责人")

# 数字输入框（带增减按钮）
self.iframe.get_by_role("spinbutton", name="* 学分要求")
self.iframe.get_by_role("spinbutton", name="* 版本年份")

# 搜索框（type="search" 或 role="searchbox"）
page.get_by_role("searchbox", name="搜索")
```

---

#### 1.2 选项与列表类（option / menuitem / listitem）

```python
# 下拉选项
self.iframe.get_by_role("option", name=dept_name)
self.iframe.get_by_role("option", name=major_name)
self.iframe.get_by_role("option", name=level_name, exact=True)

# 菜单项（下拉菜单、右键菜单、更多操作菜单）
self.iframe.get_by_role("menuitem", name="编辑")
self.iframe.get_by_role("menuitem", name="绑定")
self.iframe.get_by_role("menuitem", name="添加节")
self.iframe.get_by_role("menuitem", name="添加学习单元")
self.page.get_by_role("menuitem", name=school_name)   # 学校切换
self.iframe.get_by_role("menuitem", name=question_type)  # 题型选择

# 列表项（ul/ol 下的 li）
page.get_by_role("listitem").filter(has_text="Product 2")
page.get_by_role("listitem", name="苹果")
```

---

#### 1.3 表格类（row / rowheader / columnheader / gridcell）

```python
# 表头行（常用于全选 checkbox 所在行）
self.iframe.get_by_role("row", name="题目内容 题目类型 分数 最后修改时间")
self.iframe.get_by_role("row", name="标题 类型 创建人 创建时间 状态")

# 数据行（name 为行内单元格文本拼接）
self.iframe.get_by_role("row", name=course_name)
self.iframe.get_by_role("row", name=learning_unit_name)

# 单元格（按单元格内容定位）
self.iframe.get_by_role("cell", name="C语言程序设计031")

# 行内再定位子元素
self.iframe.get_by_role("row", name=name_or_id).get_by_role("button")
self.iframe.get_by_role("row", name=learning_unit_name).locator("label span").nth(1)
```

---

#### 1.4 导航与标签类（tab / link / treeitem / tree）

```python
# 标签页
self.iframe.get_by_role("tab", name=tab_name)

# 链接
self.iframe_3005.get_by_role("link", name="打开专业门户")

# 树形菜单项
self.base_iframe.get_by_role("treeitem", name=menu_name)

# 树形结构（再配合 get_by_text 定位节点）
self.directory_iframe.get_by_role("tree").get_by_text(type_name, exact=True)
```

---

#### 1.5 结构与展示类（heading / img / dialog）

```python
# 标题（h1-h6）
self.iframe.get_by_role("heading").nth(1)
self.iframe.get_by_role("heading", name="新建课程")
self.iframe.get_by_role("heading", name=ability_name)

# 图片
self.base_iframe.get_by_role("img").first
self.iframe_3005.get_by_role("img", name="logo")

# 弹窗/对话框
self.iframe.get_by_role("dialog", name="模板导入&更新")
self.iframe.get_by_label("发布确认").get_by_role("button", name="确定")  # 弹窗内按钮
```

---

#### 1.6 完整 role 速查表（常用 ARIA 角色）

| role                 | 对应元素/场景             | 示例                                         |
| -------------------- | ----------------------- | ------------------------------------------- |
| `button`             | 按钮、可点击的 div/span   | `get_by_role("button", name="提交")`         |
| `textbox`            | 单行输入、textarea       | `get_by_role("textbox", name="用户名")`       |
| `checkbox`           | 复选框                  | `get_by_role("checkbox", name="同意协议")`     |
| `radio`              | 单选框                  | `get_by_role("radio", name="选项A")`          |
| `combobox`           | 下拉选择（可输入）        | `get_by_role("combobox", name="城市")`        |
| `listbox`            | 下拉列表（不可输入）      | `get_by_role("listbox", name="...")`          |
| `option`             | 下拉选项                 | `get_by_role("option", name="北京")`         |
| `spinbutton`         | 数字输入框               | `get_by_role("spinbutton", name="数量")`      |
| `searchbox`          | 搜索框                  | `get_by_role("searchbox", name="搜索")`       |
| `slider`             | 滑块                    | `get_by_role("slider", name="音量")`          |
| `switch`             | 开关                    | `get_by_role("switch", name="启用")`          |
| `link`               | 链接                    | `get_by_role("link", name="帮助中心")`        |
| `menuitem`           | 菜单项                  | `get_by_role("menuitem", name="删除")`        |
| `menuitemcheckbox`   | 可勾选菜单项             | `get_by_role("menuitemcheckbox", name="...")`|
| `tab`                | 标签页                  | `get_by_role("tab", name="详情")`             |
| `tabpanel`           | 标签页内容区             | `get_by_role("tabpanel")`                    |
| `row`                | 表格行                  | `get_by_role("row", name="...")`             |
| `columnheader`       | 表头列                  | `get_by_role("columnheader", name="姓名")`    |
| `rowheader`          | 表头行                  | `get_by_role("rowheader", name="...")`       |
| `gridcell`           | 表格单元格              | `get_by_role("gridcell", name="...")`         |
| `treeitem`           | 树节点                  | `get_by_role("treeitem", name="第一章")`      |
| `tree`               | 树容器                  | `get_by_role("tree")`                        |
| `heading`            | 标题 h1-h6              | `get_by_role("heading", name="登录")`        |
| `img`                | 图片                    | `get_by_role("img", name="logo")`            |
| `dialog`             | 弹窗                    | `get_by_role("dialog", name="确认删除")`      |
| `alertdialog`        | 警告弹窗                | `get_by_role("alertdialog")`                  |
| `alert`              | 提示信息                | `get_by_role("alert")`                        |
| `status`             | 状态栏                  | `get_by_role("status")`                       |
| `progressbar`        | 进度条                  | `get_by_role("progressbar")`                  |
| `listitem`           | 列表项                  | `get_by_role("listitem", name="...")`         |
| `article`            | 文章区域                | `get_by_role("article")`                      |
| `main`               | 主内容区                | `get_by_role("main")`                         |
| `navigation`         | 导航区                  | `get_by_role("navigation")`                   |
| `form`               | 表单                    | `get_by_role("form", name="...")`             |

---

**何时使用**：

- 元素有**可访问名称**（aria-label、label 关联、按钮文字等）时
- 按钮、链接、输入框、表格、下拉框等**标准控件**
- 需要**贴近用户视角**（用户看到的文字/标签）时
- 页面结构变化时，角色定位通常比 CSS 更稳定

**注意**：`name` 支持**部分匹配**，可用 `exact=True` 精确匹配；多个匹配时用 `.first`、`.last`、`.nth(n)` 限定。

---

### 2. get_by_placeholder（按占位符定位）——首选

**用法**：`page.get_by_placeholder("占位符文本")`

**项目中的使用示例**：

```python
self.iframe.get_by_placeholder("请输入作业标题")
self.iframe.get_by_placeholder("请选择建设时间")
self.iframe.get_by_placeholder("指标点名称").last  # 多个同名输入框时取最后一个
self.iframe.get_by_label("选择课程").get_by_placeholder("搜索课程名称或代码")
```

**何时使用**：

- 输入框有**明确的 placeholder** 且不常变动时
- 占位符能**唯一区分**该输入框时
- 表单项没有 label 或 label 不清晰时

**注意**：占位符易随产品文案调整，若经常变化，可考虑 `get_by_label` 或 `get_by_role`。

---

### 3. get_by_label（按标签定位）——首选

**用法**：`page.get_by_label("标签文本")`

**项目中的使用示例**：

```python
# 在指定表单区域内定位
self.iframe.get_by_label("新建行政班").get_by_text("请选择学院")
self.iframe.get_by_label("新建培养方案").get_by_text("请选择专业")
self.iframe.get_by_label("是否允许学生自选").get_by_text("是")
self.confirm_new_semester_button = self.iframe.get_by_label("确认新增").get_by_role("button", name="确定")
```

**何时使用**：

- 表单项有**关联的 label**（`<label for="...">` 或包裹关系）时
- 需要**先限定在某个表单/区域**内再定位子元素时
- 多个表单有相似结构，需按表单标题区分时

**注意**：`get_by_label` 常与 `get_by_text`、`get_by_role` 组合，先缩小范围再定位。

---

### 4. get_by_text（按可见文本定位）——次选

**用法**：`page.get_by_text("文本", exact=True/False)`

**项目中的使用示例**：

```python
# 精确匹配
return self.iframe.get_by_text(class_name, exact=True)

# 部分匹配（默认）
self.iframe.get_by_text("请选择所属学年")
self.iframe.get_by_text("无限制")
self.iframe.get_by_text("选择")
self.iframe.get_by_text("设置主讲教师")
self.iframe.get_by_text("拖拽组件到这里")
```

**何时使用**：

- 按**可见文本**定位（链接、选项、提示、占位符等）
- 元素没有合适的 role、placeholder、label 时
- 需要按**用户可见文案**定位时

**注意**：文本易随产品改版变化；`exact=True` 可避免误匹配子串。

---

### 5. locator() + CSS 选择器——备选

**用法**：`page.locator("CSS选择器")`

**项目中的使用示例**：

```python
# ID
page.locator("#username")
self.ability_description_input = self.iframe.locator("#w-e-textarea-1")

# class、属性
page.locator("[data-testid='logo'], .logo, #logo")
page.locator("input[name='custname']")
page.locator("button[type='submit']")
page.locator("[class*='search'], .DocSearch")

# 标签 + 属性
page.locator("form")
page.locator("nav a, .nav-item")
page.locator("textarea[name='comments']")

# 组合、后代
self.iframe.get_by_role("row", name="...").locator("span")
self.iframe.get_by_role("row", name="...").locator(".el-checkbox")
self.iframe.get_by_label("新建课程").locator(".el-upload, [class*='upload']").first
```

**何时使用**：

- 元素**没有**合适的 role、placeholder、label、text 时
- 有稳定的 **data-testid**、**id**、**name** 等属性时
- 需要按 **class**、**属性** 定位时
- 在**已有 locator 基础上**再定位子元素时（`.locator("span")`）

**注意**：CSS 依赖 DOM 结构，结构变动时易失效；优先用 `data-testid`，其次 id/name。

---

### 6. locator() + XPath——备选

**用法**：`page.locator("xpath=//...")`

**项目中的使用示例**：

```python
# 按文本内容（Toast、提示消息）
self.iframe.locator("xpath=//p[contains(text(),'保存成功')]")
self.iframe.locator("xpath=//p[contains(text(),'创建成功')]").last
self.iframe.locator("xpath=//p[contains(text(),'已成功将') and contains(text(),'添加到课程智能体列表')]").last

# 按标签 + 兄弟节点
self.iframe.locator("xpath=//div[text()='标签']/following-sibling::div//input")
self.iframe.locator("xpath=//div[./label[text()='标题']]//input")

# 按 class、层级
self.iframe.locator("xpath=//div[@class='root-node-actions']//button[1]")
self.iframe.locator("xpath=//span[text()=' 无结课时间 ']/preceding-sibling::span")

# 复杂条件
self.iframe.locator(f"xpath=//div[./div/h5[text()='{ability_name}']]/div/button[3]")
```

**何时使用**：

- **Toast、消息提示**等动态文本（`contains(text(),'...')`）
- **复杂层级**、兄弟节点、前后关系（following-sibling、preceding-sibling）
- CSS 难以表达的**结构关系**时
- 需要**取第 N 个子元素**（`button[1]`、`button[2]`）时

**注意**：XPath 可读性差、维护成本高，仅在 CSS 和语义化定位无法满足时使用。

---

### 7. frame_locator（iframe 定位）——必须

**用法**：`page.frame_locator("iframe选择器")`

**项目中的使用示例**：

```python
self.iframe = page.frame_locator("iframe#app-iframe-4009")
self.iframe = page.frame_locator("iframe#app-iframe-2008")
self.iframe = self.base_iframe.frame_locator("iframe#course-workspace-iframe")
```

**何时使用**：

- 页面包含 **iframe**，且目标元素在 iframe 内时
- 必须先进入 iframe，再在其内部使用 `get_by_*` 或 `locator`

**注意**：进入 iframe 后，所有定位都在该 frame 内进行；嵌套 iframe 需链式调用 `frame_locator`。

---

### 8. filter(has_text=)（按文本筛选）——次选

**用法**：`locator.filter(has_text="文本")`

**项目中的使用示例**：

```python
return self.iframe.locator("div.agent-square-card").filter(has_text=agent_name).get_by_role("button", name="加入")
return self.iframe.locator(".tab-item", has_text=menu_name)
```

**何时使用**：

- 有**多个结构相似**的元素，需按**包含的文本**筛选
- 表格行、卡片列表中，按某列/某块文字定位整行/整卡

**注意**：`has_text` 为**子串匹配**；可与 `get_by_role` 等组合使用。

---

### 9. locator("selector", has_text=)（选择器 + 文本）——次选

**用法**：`page.locator("selector", has_text="文本")`

**项目中的使用示例**：

```python
return self.iframe.locator("tr", has_text=role_name).get_by_role("button", name="分配")
return self.iframe.locator("tr", has_text=semester_value).get_by_role("button", name="设为当前学期")
return self.iframe.locator("tr", has_text=code).locator("i")
return self.iframe_2104.locator("tr", has_text=major_name).get_by_role("button", name="编辑")
```

**何时使用**：

- 表格、列表中，先按**行内文本**找到整行，再定位行内按钮/图标
- 与 `get_by_role` 组合：`locator("tr", has_text=x).get_by_role("button", name="编辑")`

---

### 10. :has-text()（CSS 文本选择器）——备选

**用法**：`page.locator("selector:has-text('文本')")`

**项目中的使用示例**：

```python
nav_item = self.page.locator(f"nav a:has-text('{category_name}')")
submit_by_text = page.locator("button:has-text('Submit')")
self.logout_button = page.locator("button:has-text('退出')")
```

**何时使用**：

- 需要**在 CSS 选择器内**直接按文本筛选时
- 与 `locator()` 配合，写法比 `filter(has_text=)` 更紧凑

**注意**：`has-text` 为子串匹配；复杂场景建议用 `filter(has_text=)` 更清晰。

---

### 11. .nth() / .first / .last（多元素取序）——按需

**用法**：`locator.nth(index)`、`locator.first`、`locator.last`

**项目中的使用示例**：

```python
# 取第一个
self.upload_file_button = self.iframe.get_by_role("button", name="上传文件").first
self.learning_unit_all_select_button = self.iframe.get_by_role("row", name="...").locator("span").first

# 取最后一个（常用于 Toast、动态新增的提示）
self.create_chapter_success_message = self.iframe.locator("xpath=//p[contains(text(),'章节成功')]").last
self.confirm_edit_button = self.iframe.get_by_role("button", name="保存").last

# 取第 N 个
return self.iframe.get_by_role("row", name=learning_unit_name).locator("label span").nth(1)
self.root_node_locator = self.iframe.get_by_role("heading").nth(1)
```

**何时使用**：

- 同一选择器匹配**多个元素**，需指定第几个时
- **Toast、消息提示**可能有多条，取 `.last` 表示最新一条
- 表格/列表中，取某行的第 N 列（如 `.nth(1)`）

**注意**：`nth` 从 0 开始；优先考虑用更精确的选择器减少多匹配，再考虑 `.first`/`.last`/`.nth`。

---

### 12. 组合定位（链式调用）

**项目中的使用示例**：

```python
# 先按区域，再按角色
self.iframe.get_by_label("新建行政班").get_by_text("请选择学院")

# 先按行，再按按钮
self.iframe.locator("tr", has_text=role_name).get_by_role("button", name="分配")

# 先按角色，再按 CSS 子元素
self.iframe.get_by_role("row", name="...").locator("span").first

# 先按文本，再找父级，再找按钮
return self.iframe.get_by_text(node_name).locator("..").get_by_role("button").nth(1)
```

**何时使用**：

- 需要**先缩小范围**（表单、行、卡片）再定位具体元素时
- 单一定位方式无法唯一确定元素时

---

## 三、使用优先级建议

```
1. get_by_role     → 有可访问名称的按钮、输入框、表格、选项等
2. get_by_placeholder → 有占位符的输入框
3. get_by_label    → 有 label 的表单项
4. get_by_text     → 按可见文本（链接、选项、提示）
5. locator(CSS)    → 有 data-testid、id、稳定 class/属性
6. locator(XPath)  → Toast、复杂层级、动态文本
7. filter/has_text → 多相似元素按文本筛选
8. .first/.last/.nth → 多匹配时取序
```

---

## 四、项目中的典型场景对照

| 场景 | 推荐定位方式 | 示例 |
|------|--------------|------|
| 按钮 | `get_by_role("button", name="...")` | 新建、保存、确定 |
| 输入框（有 placeholder） | `get_by_placeholder("...")` | 请输入作业标题 |
| 输入框（有 label） | `get_by_label("...").get_by_role("textbox")` 或 `get_by_text` | 请选择学院 |
| 表格行内按钮 | `locator("tr", has_text=行标识).get_by_role("button", name="...")` | 分配、编辑 |
| 下拉选项 | `get_by_role("option", name="...")` | 学院、专业选项 |
| Toast/成功提示 | `locator("xpath=//p[contains(text(),'...')]").last` | 保存成功、创建成功 |
| iframe 内元素 | `frame_locator("iframe#...")` 后再用上述方式 | 业务系统 iframe |
| 多个同名按钮 | `get_by_role("button", name="...").last` 或 `.nth(n)` | 多个「保存」按钮 |
| 卡片/列表中按名称 | `locator("...").filter(has_text=name).get_by_role(...)` | 智能体卡片 |

---

## 五、不推荐的做法

1. **过度依赖 XPath**：可读性差，结构变动易失效，优先用语义化定位。
2. **纯 class 定位**：class 常随样式调整，除非稳定且唯一。
3. **过长链式 XPath**：如 `//div/div/div/span/...`，维护困难。
4. **按位置取元素**：如 `.nth(5)` 而无业务含义，列表顺序变化会失败。
5. **忽略 iframe**：元素在 iframe 内时，必须先 `frame_locator` 再定位。

---

## 六、参考资源

- [Playwright 官方 Locators 文档](https://playwright.dev/python/docs/locators)
- [Playwright 定位器最佳实践](https://playwright.dev/python/docs/locators#locator-best-practices)
