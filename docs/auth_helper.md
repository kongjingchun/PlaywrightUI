# 免登录功能使用指南

## 快速开始

```python
from utils.auth_helper import AuthHelper

auth = AuthHelper()

# 保存登录状态
auth.save_auth_state(page, "用户标识")

# 加载登录状态（免登录）
auth.load_auth_state(page, "用户标识", base_url)
```

## 核心 API

| 方法 | 说明 |
|------|------|
| `save_auth_state(page, key)` | 保存当前登录状态 |
| `load_auth_state(page, key, base_url)` | 加载已保存的状态 |
| `is_auth_valid(key)` | 检查状态是否有效 |
| `clear_auth_state(key)` | 清除指定用户状态 |
| `clear_all_auth_states()` | 清除所有状态 |

## 使用示例

### 1. 手动控制免登录

```python
from utils.auth_helper import AuthHelper

auth = AuthHelper()
auth_key = "机构管理员"

# 检查是否有有效的缓存
if auth.is_auth_valid(auth_key):
    # 免登录
    auth.load_auth_state(page, auth_key, base_url)
else:
    # 正常登录
    login_page.login(username, password)
    # 保存状态
    auth.save_auth_state(page, auth_key)
```

### 2. 多用户管理

```python
auth = AuthHelper()

# 保存不同角色
auth.save_auth_state(page, "超级管理员")
auth.save_auth_state(page, "教师")
auth.save_auth_state(page, "学生")

# 使用指定角色
auth.load_auth_state(page, "教师", base_url)
```

### 3. 结合 TestContextHelper（本地化部署项目可用）

```python
from tests.gqtest import TestContextHelper
from utils.auth_helper import AuthHelper

helper = TestContextHelper()
auth = AuthHelper()

# 完全手动控制
helper.login_and_init(
    page, base_url, initial_admin["username"], initial_admin["password"],
    use_saved_auth=False,  # 不自动使用缓存
    save_auth=False        # 不自动保存
)

# 手动保存
auth.save_auth_state(page, "我的用户")
```

## 状态文件

保存位置：`项目根目录/.auth/`

```
.auth/
├── 机构管理员_state.json
├── 教师_state.json
└── 学生_state.json
```

默认有效期：24 小时

## 注意事项

1. `.auth/` 目录已加入 `.gitignore`，不会提交到 Git
2. 状态过期后会自动清除，需要重新登录
3. 不同环境（dev/test/prod）建议使用不同的用户标识



        # 定义用户标识（用于免登录）
        auth_key = "机构管理员"

        helper = TestContextHelper()
        auth = AuthHelper()

        # ========== 手动控制免登录 ==========
        with allure.step("登录用户"):
            # 检查是否有有效的认证状态
            if auth.is_auth_valid(auth_key):
                # 使用保存的认证状态（免登录）
                with allure.step(f"使用缓存登录: {auth_key}"):
                    auth.load_auth_state(page, auth_key, base_url)
            else:
                # 正常登录流程
                with allure.step("执行正常登录"):
                    helper.login_and_init(
                        page, base_url, initial_admin["username"], initial_admin["password"],
                        "智慧大学", "机构管理员",
                        use_saved_auth=False,  # 不自动尝试免登录（我们手动控制）
                        save_auth=False        # 不自动保存（我们手动保存）
                    )
                # 手动保存认证状态
                with allure.step(f"保存认证状态: {auth_key}"):
                    auth.save_auth_state(page, auth_key)