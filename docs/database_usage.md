# 数据库操作指南

## 功能概述

框架提供了 MySQL 和 Redis 的操作工具，用于：
- 🔧 测试前准备测试数据
- ✅ 测试后验证数据正确性
- 🗑️ 测试清理（删除测试数据）
- 🔍 直接查询数据库验证结果

## MySQL 操作

### 1. 配置 MySQL

在环境配置文件中启用并配置 MySQL：

```yaml
# config/environments/dev.yaml
mysql:
  enabled: true  # 启用 MySQL
  host: "localhost"
  port: 3306
  user: "root"
  password: "your_password"
  database: "test_db"
  charset: "utf8mb4"
```

### 2. 在测试中使用 MySQL

#### 方式一：使用 Fixture（推荐）

```python
import pytest

def test_user_query(mysql_helper):
    """使用 mysql_helper fixture"""
    if not mysql_helper:
        pytest.skip("MySQL 未启用")
    
    # 查询用户
    users = mysql_helper.query("SELECT * FROM users WHERE age > %s", (25,))
    assert len(users) > 0
    
    # 查询单条记录
    user = mysql_helper.query_one("SELECT * FROM users WHERE username = %s", ("admin",))
    assert user is not None
    assert user['username'] == 'admin'
```

#### 方式二：直接创建实例

```python
from utils.mysql_helper import MySQLHelper

def test_with_mysql():
    # 使用上下文管理器（推荐）
    with MySQLHelper(
        host="localhost",
        port=3306,
        user="root",
        password="password",
        database="test_db"
    ) as db:
        users = db.query("SELECT * FROM users")
        print(users)
```

### 3. MySQL 常用操作

#### 查询操作

```python
# 查询多条记录
users = mysql_helper.query("SELECT * FROM users WHERE age > %s", (25,))
for user in users:
    print(f"{user['name']}: {user['age']}")

# 查询单条记录
user = mysql_helper.query_one("SELECT * FROM users WHERE id = %s", (1001,))
if user:
    print(user['name'])

# 查询单个值
count = mysql_helper.query_value("SELECT COUNT(*) as count FROM users")
print(f"用户总数: {count}")

max_age = mysql_helper.query_value("SELECT MAX(age) as max_age FROM users")
print(f"最大年龄: {max_age}")
```

#### 插入操作

```python
# 插入单条记录
user_id = mysql_helper.insert("users", {
    "username": "test_user",
    "password": "123456",
    "age": 25,
    "email": "test@example.com"
})
print(f"插入成功，ID: {user_id}")

# 使用原始 SQL 插入
mysql_helper.execute(
    "INSERT INTO users (username, password, age) VALUES (%s, %s, %s)",
    ("user2", "pass2", 30)
)

# 批量插入
users_data = [
    ("user3", "pass3", 28),
    ("user4", "pass4", 32),
    ("user5", "pass5", 27)
]
mysql_helper.execute_many(
    "INSERT INTO users (username, password, age) VALUES (%s, %s, %s)",
    users_data
)
```

#### 更新操作

```python
# 更新记录
affected = mysql_helper.update(
    table="users",
    data={"age": 26, "email": "new@example.com"},
    where="username = %s",
    where_params=("test_user",)
)
print(f"更新了 {affected} 条记录")

# 使用原始 SQL 更新
mysql_helper.execute(
    "UPDATE users SET age = %s WHERE username = %s",
    (27, "test_user")
)
```

#### 删除操作

```python
# 删除记录
affected = mysql_helper.delete("users", "username = %s", ("test_user",))
print(f"删除了 {affected} 条记录")

# 使用原始 SQL 删除
mysql_helper.execute("DELETE FROM users WHERE age < %s", (18,))

# 清空表（谨慎使用）
mysql_helper.truncate_table("test_data")
```

#### 工具方法

```python
# 检查表是否存在
if mysql_helper.table_exists("users"):
    print("users 表存在")

# 获取表结构
table_info = mysql_helper.query("DESCRIBE users")
for column in table_info:
    print(f"{column['Field']}: {column['Type']}")
```

### 4. 测试用例示例

```python
import pytest
import allure

@allure.feature("用户管理")
class TestUserManagement:
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, mysql_helper):
        """测试前准备数据"""
        if not mysql_helper:
            pytest.skip("MySQL 未启用")
        
        # 清理旧数据
        mysql_helper.delete("users", "username LIKE %s", ("test_%",))
        
        # 插入测试数据
        self.test_user_id = mysql_helper.insert("users", {
            "username": "test_user",
            "password": "123456",
            "age": 25,
            "email": "test@example.com"
        })
        
        yield
        
        # 测试后清理
        mysql_helper.delete("users", "id = %s", (self.test_user_id,))
    
    @allure.story("用户查询")
    def test_query_user(self, mysql_helper):
        """测试查询用户"""
        user = mysql_helper.query_one(
            "SELECT * FROM users WHERE username = %s",
            ("test_user",)
        )
        
        assert user is not None
        assert user['username'] == 'test_user'
        assert user['age'] == 25
    
    @allure.story("用户更新")
    def test_update_user(self, mysql_helper):
        """测试更新用户"""
        # 更新用户年龄
        affected = mysql_helper.update(
            table="users",
            data={"age": 26},
            where="username = %s",
            where_params=("test_user",)
        )
        
        assert affected == 1
        
        # 验证更新结果
        user = mysql_helper.query_one(
            "SELECT * FROM users WHERE username = %s",
            ("test_user",)
        )
        assert user['age'] == 26
```

## Redis 操作

### 1. 配置 Redis

在环境配置文件中启用并配置 Redis：

```yaml
# config/environments/dev.yaml
redis:
  enabled: true  # 启用 Redis
  host: "localhost"
  port: 6379
  db: 0  # 数据库编号
  password: ""  # 密码（如果有）
```

### 2. 在测试中使用 Redis

#### 方式一：使用 Fixture（推荐）

```python
import pytest

def test_cache(redis_helper):
    """使用 redis_helper fixture"""
    if not redis_helper:
        pytest.skip("Redis 未启用")
    
    # 设置缓存
    redis_helper.set("user_token", "abc123", ex=3600)
    
    # 获取缓存
    token = redis_helper.get("user_token")
    assert token == "abc123"
```

#### 方式二：直接创建实例

```python
from utils.redis_helper import RedisHelper

def test_with_redis():
    # 使用上下文管理器（推荐）
    with RedisHelper(host="localhost", port=6379, db=0) as redis_client:
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        print(value)
```

### 3. Redis 常用操作

#### 字符串操作

```python
# 设置键值
redis_helper.set("username", "admin")
redis_helper.set("token", "abc123", ex=3600)  # 1小时后过期

# 获取键值
username = redis_helper.get("username")
print(username)

# 设置复杂对象（自动 JSON 序列化）
redis_helper.set("user_info", {
    "name": "张三",
    "age": 25,
    "email": "zhangsan@example.com"
})

# 获取并解析 JSON
user_info = redis_helper.get("user_info", parse_json=True)
print(user_info['name'])

# 删除键
redis_helper.delete("username")
redis_helper.delete("key1", "key2", "key3")  # 批量删除

# 检查键是否存在
if redis_helper.exists("token"):
    print("token 存在")

# 设置过期时间
redis_helper.expire("session", 1800)  # 30分钟后过期

# 获取剩余生存时间
ttl = redis_helper.ttl("session")
print(f"还剩 {ttl} 秒")
```

#### 哈希操作

```python
# 设置哈希字段
redis_helper.hset("user:1001", "name", "张三")
redis_helper.hset("user:1001", "age", 25)
redis_helper.hset("user:1001", "email", "zhangsan@example.com")

# 获取哈希字段
name = redis_helper.hget("user:1001", "name")
print(name)

# 获取所有字段
user_info = redis_helper.hgetall("user:1001")
print(user_info)  # {"name": "张三", "age": "25", "email": "..."}
```

#### 列表操作

```python
# 从左侧插入
redis_helper.lpush("tasks", "task1", "task2", "task3")

# 从右侧插入
redis_helper.rpush("logs", "log1", "log2")

# 获取列表范围
tasks = redis_helper.lrange("tasks", 0, -1)  # 获取所有
print(tasks)

recent_tasks = redis_helper.lrange("tasks", 0, 9)  # 获取前10个
```

#### 工具方法

```python
# 获取所有键
all_keys = redis_helper.keys()
print(all_keys)

# 获取匹配的键
user_keys = redis_helper.keys("user:*")
session_keys = redis_helper.keys("session:*")

# 清空数据库（谨慎使用）
redis_helper.flushdb()

# 获取服务器信息
info = redis_helper.info()
print(info['redis_version'])
```

### 4. 测试用例示例

```python
import pytest
import allure

@allure.feature("缓存管理")
class TestCache:
    
    @pytest.fixture(autouse=True)
    def setup_redis(self, redis_helper):
        """测试前清理 Redis"""
        if not redis_helper:
            pytest.skip("Redis 未启用")
        
        # 删除测试相关的键
        test_keys = redis_helper.keys("test:*")
        if test_keys:
            redis_helper.delete(*test_keys)
        
        yield
        
        # 测试后清理
        test_keys = redis_helper.keys("test:*")
        if test_keys:
            redis_helper.delete(*test_keys)
    
    @allure.story("缓存设置")
    def test_set_cache(self, redis_helper):
        """测试设置缓存"""
        # 设置缓存
        result = redis_helper.set("test:token", "abc123", ex=60)
        assert result is True
        
        # 验证缓存
        token = redis_helper.get("test:token")
        assert token == "abc123"
        
        # 验证过期时间
        ttl = redis_helper.ttl("test:token")
        assert 0 < ttl <= 60
    
    @allure.story("缓存过期")
    def test_cache_expire(self, redis_helper):
        """测试缓存过期"""
        import time
        
        # 设置 2 秒过期的缓存
        redis_helper.set("test:temp", "value", ex=2)
        assert redis_helper.exists("test:temp") == 1
        
        # 等待过期
        time.sleep(3)
        assert redis_helper.exists("test:temp") == 0
    
    @allure.story("复杂对象缓存")
    def test_cache_object(self, redis_helper):
        """测试缓存复杂对象"""
        user_data = {
            "id": 1001,
            "name": "张三",
            "age": 25,
            "roles": ["admin", "user"]
        }
        
        # 缓存对象
        redis_helper.set("test:user", user_data)
        
        # 获取并验证
        cached_user = redis_helper.get("test:user", parse_json=True)
        assert cached_user['name'] == "张三"
        assert cached_user['age'] == 25
        assert "admin" in cached_user['roles']
```

## 注意事项

### 安全性

1. **敏感信息保护**：
   - 不要将数据库密码提交到代码仓库
   - 使用环境变量或 `.env` 文件存储敏感信息
   - 生产环境建议关闭直接数据库访问

2. **权限控制**：
   - 测试账号使用最小权限原则
   - 只授予必要的数据库操作权限
   - 禁止在生产环境执行危险操作（DROP, TRUNCATE）

### 性能优化

1. **连接管理**：
   - 使用连接池（框架已实现）
   - 及时关闭连接（使用 `with` 语句）
   - 避免频繁创建/销毁连接

2. **查询优化**：
   - 使用参数化查询（防止 SQL 注入）
   - 避免 `SELECT *`，只查询需要的字段
   - 合理使用索引
   - 批量操作使用 `execute_many`

3. **缓存策略**：
   - 合理设置过期时间
   - 避免缓存过大的对象
   - 使用 Redis 键命名规范（如 `user:1001`）

### 测试最佳实践

1. **数据隔离**：
   - 每个测试使用独立的测试数据
   - 测试前清理，测试后清理
   - 使用特殊前缀标识测试数据（如 `test_`）

2. **事务管理**：
   - 测试中使用事务，失败时回滚
   - 确保测试不影响其他数据

3. **环境区分**：
   - 开发/测试/生产环境使用不同的数据库
   - 通过配置文件管理环境差异

4. **错误处理**：
   - 数据库操作要有错误处理
   - 连接失败时优雅降级
   - 记录详细的错误日志

## 故障排查

### MySQL 连接失败

```
✗ 连接 MySQL 数据库失败: (2003, "Can't connect to MySQL server...")
```

**检查项**：
- ✅ 确认 MySQL 服务已启动
- ✅ 确认 host 和 port 正确
- ✅ 确认用户名和密码正确
- ✅ 确认数据库存在
- ✅ 确认网络可达（防火墙规则）

### Redis 连接失败

```
✗ 连接 Redis 失败: Error 111 connecting to localhost:6379. Connection refused.
```

**检查项**：
- ✅ 确认 Redis 服务已启动
- ✅ 确认 host 和 port 正确
- ✅ 确认密码正确（如果设置了）
- ✅ 确认 Redis 绑定地址（bind 127.0.0.1）
- ✅ 确认防火墙规则

### 权限错误

```
✗ 执行 SQL 失败: (1142, "SELECT command denied...")
```

**解决方案**：
- 授予测试账号必要的权限
- 使用具有足够权限的账号

```sql
-- 授予权限示例
GRANT SELECT, INSERT, UPDATE, DELETE ON test_db.* TO 'test_user'@'localhost';
FLUSH PRIVILEGES;
```

## 相关资源

- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [Redis 官方文档](https://redis.io/documentation)
- [PyMySQL 文档](https://pymysql.readthedocs.io/)
- [redis-py 文档](https://redis-py.readthedocs.io/)
