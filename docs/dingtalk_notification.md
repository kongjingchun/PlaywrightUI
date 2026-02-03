# 钉钉通知配置指南

## 功能说明

测试执行完成后，可以自动发送测试结果到钉钉群聊，包含以下信息：
- 📊 测试结果统计（总数、通过、失败、跳过）
- ⏱️ 执行时长
- ❌ 失败用例列表
- 🎯 环境信息

## 配置步骤

### 1. 创建钉钉机器人

1. 打开钉钉群聊，点击右上角 `...` → `智能群助手` → `添加机器人`
2. 选择 `自定义机器人`，点击 `添加`
3. 设置机器人名称（如：测试报告通知）
4. 选择安全设置：
   - **推荐**：勾选 `加签` 方式（更安全）
   - 也可选择 `自定义关键词`（需包含：测试、报告等关键词）
5. 点击 `完成`，复制 `Webhook` 地址和加签密钥（如果选择了加签）

**Webhook 地址示例：**
```
https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**加签密钥示例：**
```
SECxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. 配置环境文件

打开对应环境的配置文件（如 `config/environments/test.yaml`），添加或修改钉钉配置：

```yaml
# 钉钉通知配置
dingtalk:
  enabled: true  # 启用钉钉通知
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=你的token"
  secret: "SEC你的加签密钥"  # 如果没有使用加签，留空即可
```

**配置说明：**
- `enabled`: 是否启用钉钉通知（true/false）
- `webhook`: 钉钉机器人的 webhook 地址（必填，如果启用）
- `secret`: 加签密钥（选填，推荐配置以提高安全性）

### 3. 测试配置

配置完成后，运行一次测试验证：

```bash
# 运行测试
pytest tests/test_gqkt_login.py -v

# 测试完成后会自动发送钉钉通知
```

## 通知内容示例

### 成功通知（全部通过）

```
✅ 自动化测试报告
---

📊 测试结果
- 环境: 测试环境
- 状态: 全部通过
- 总数: 10
- 通过: 10
- 失败: 0
- 跳过: 0
- 通过率: 100.00%
- 耗时: 2分30秒

---
2026-02-03 18:45:30
```

### 失败通知（有失败用例）

```
❌ 自动化测试报告
---

📊 测试结果
- 环境: 测试环境
- 状态: 测试失败
- 总数: 10
- 通过: 8
- 失败: 2
- 跳过: 0
- 通过率: 80.00%
- 耗时: 2分30秒

❌ 失败用例
1. test_gqkt_login.py::TestGqktLogin::test_001_login_success
2. test_search.py::TestSearch::test_search_invalid

---
2026-02-03 18:45:30
```

## 高级配置

### 多环境配置

不同环境可以配置不同的钉钉群聊：

**开发环境（dev.yaml）：**
```yaml
dingtalk:
  enabled: true
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=dev_token"
  secret: "SEC_dev_secret"
```

**测试环境（test.yaml）：**
```yaml
dingtalk:
  enabled: true
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=test_token"
  secret: "SEC_test_secret"
```

**生产环境（prod.yaml）：**
```yaml
dingtalk:
  enabled: true  # 生产环境建议启用，及时通知测试结果
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=prod_token"
  secret: "SEC_prod_secret"
```

### 禁用钉钉通知

如果临时不需要钉钉通知，只需将 `enabled` 设置为 `false`：

```yaml
dingtalk:
  enabled: false  # 禁用钉钉通知
  webhook: ""
  secret: ""
```

## 故障排查

### 1. 没有收到通知

**检查项：**
- ✅ 确认 `enabled: true`
- ✅ 确认 webhook 地址正确
- ✅ 确认机器人在群聊中
- ✅ 查看控制台或日志中的错误信息

**日志示例：**
```
INFO     📤 开始发送钉钉通知...
INFO     ✓ 钉钉消息发送成功
INFO     ✅ 钉钉通知发送成功
```

### 2. 收到"安全设置"错误

**错误示例：**
```
ERROR    ✗ 钉钉消息发送失败: sign not match
```

**解决方案：**
- 检查 `secret` 是否正确
- 确认使用了 `加签` 安全设置
- 如果使用关键词安全设置，请将 `secret` 留空

### 3. 通知内容不完整

**原因：** 钉钉单条消息有字符限制

**解决方案：**
- 代码已自动处理，失败用例最多显示 10 个
- 如需查看完整列表，请查看日志文件或 Allure 报告

## API 使用示例

如果需要在自定义脚本中使用钉钉通知：

```python
from utils.dingtalk_notification import DingTalkNotification, send_dingtalk_report

# 方式一：使用类
notifier = DingTalkNotification(
    webhook="https://oapi.dingtalk.com/robot/send?access_token=xxx",
    secret="SECxxx"
)

# 发送测试报告
notifier.send_test_report(
    total=10,
    passed=8,
    failed=2,
    skipped=0,
    duration="2分30秒",
    failed_cases=["test_login_failed", "test_search_error"],
    environment="测试环境"
)

# 发送自定义文本消息
notifier.send_text("测试开始执行", at_all=True)

# 发送自定义 Markdown 消息
notifier.send_markdown(
    title="自定义标题",
    text="## 标题\n- 列表项1\n- 列表项2"
)

# 方式二：使用便捷函数
send_dingtalk_report(
    webhook="https://oapi.dingtalk.com/robot/send?access_token=xxx",
    secret="SECxxx",
    total=10,
    passed=8,
    failed=2,
    skipped=0,
    duration="2分30秒",
    failed_cases=["test_login_failed"],
    environment="测试环境"
)
```

## 注意事项

1. **安全性**：
   - 不要将 webhook 和 secret 提交到公开仓库
   - 建议使用环境变量或 `.env` 文件存储敏感信息
   - 推荐使用加签方式，避免机器人被滥用

2. **频率限制**：
   - 钉钉机器人有频率限制（每分钟最多 20 条）
   - 正常测试场景不会触发限制

3. **网络要求**：
   - 需要能访问钉钉 API（oapi.dingtalk.com）
   - 如在内网环境，需要配置代理

4. **错误处理**：
   - 发送失败不会影响测试执行
   - 错误信息会记录在日志中
   - 可以在日志中查看详细的错误原因

## 相关链接

- [钉钉机器人官方文档](https://open.dingtalk.com/document/robots/custom-robot-access)
- [自定义机器人安全设置](https://open.dingtalk.com/document/robots/customize-robot-security-settings)
