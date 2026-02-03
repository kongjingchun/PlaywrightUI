# ========================================
# Redis 操作工具
# ========================================
# 封装 Redis 操作，提供便捷的缓存管理功能
# ========================================

import redis
import json
from typing import Optional, Any, List, Dict, Union
from utils.logger import Logger


class RedisHelper:
    """Redis 操作辅助类"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 decode_responses: bool = True):
        """
        初始化 Redis 连接
        
        Args:
            host: Redis 服务器地址
            port: 端口号
            db: 数据库编号（0-15）
            password: 密码（如果有）
            decode_responses: 是否自动解码响应为字符串
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        self.logger = Logger(self.__class__.__name__)
        self.client = None
    
    def connect(self) -> bool:
        """
        连接 Redis
        
        Returns:
            是否连接成功
        """
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses
            )
            # 测试连接
            self.client.ping()
            self.logger.info(f"✓ 连接 Redis 成功: {self.host}:{self.port}/{self.db}")
            return True
        except Exception as e:
            self.logger.error(f"✗ 连接 Redis 失败: {e}")
            return False
    
    def close(self):
        """关闭 Redis 连接"""
        try:
            if self.client:
                self.client.close()
                self.client = None
            self.logger.info("✓ Redis 连接已关闭")
        except Exception as e:
            self.logger.error(f"✗ 关闭 Redis 连接失败: {e}")
    
    # ==================== 字符串操作 ====================
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        设置键值
        
        Args:
            key: 键名
            value: 值（会自动序列化复杂对象）
            ex: 过期时间（秒）
        
        Returns:
            是否成功
        
        示例：
            redis.set("username", "admin")
            redis.set("user_info", {"name": "张三", "age": 25}, ex=3600)
        """
        try:
            if not self.client:
                self.connect()
            
            # 如果是复杂对象，序列化为 JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = self.client.set(key, value, ex=ex)
            self.logger.info(f"✓ 设置键值成功: {key}")
            return result
        except Exception as e:
            self.logger.error(f"✗ 设置键值失败 {key}: {e}")
            return False
    
    def get(self, key: str, parse_json: bool = False) -> Optional[Any]:
        """
        获取键值
        
        Args:
            key: 键名
            parse_json: 是否尝试解析为 JSON
        
        Returns:
            键值，不存在返回 None
        
        示例：
            username = redis.get("username")
            user_info = redis.get("user_info", parse_json=True)
        """
        try:
            if not self.client:
                self.connect()
            
            value = self.client.get(key)
            
            if value and parse_json:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    self.logger.warning(f"无法解析 JSON: {key}")
            
            if value:
                self.logger.info(f"✓ 获取键值成功: {key}")
            else:
                self.logger.info(f"✓ 键不存在: {key}")
            
            return value
        except Exception as e:
            self.logger.error(f"✗ 获取键值失败 {key}: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """
        删除一个或多个键
        
        Args:
            *keys: 键名列表
        
        Returns:
            删除的键数量
        
        示例：
            redis.delete("key1")
            redis.delete("key1", "key2", "key3")
        """
        try:
            if not self.client:
                self.connect()
            
            count = self.client.delete(*keys)
            self.logger.info(f"✓ 删除键成功: {keys}，删除 {count} 个")
            return count
        except Exception as e:
            self.logger.error(f"✗ 删除键失败 {keys}: {e}")
            return 0
    
    def exists(self, *keys: str) -> int:
        """
        检查键是否存在
        
        Args:
            *keys: 键名列表
        
        Returns:
            存在的键数量
        
        示例：
            if redis.exists("username"):
                print("用户名存在")
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.exists(*keys)
        except Exception as e:
            self.logger.error(f"✗ 检查键存在失败: {e}")
            return 0
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间
        
        Args:
            key: 键名
            seconds: 秒数
        
        Returns:
            是否成功
        
        示例：
            redis.expire("session_token", 3600)  # 1小时后过期
        """
        try:
            if not self.client:
                self.connect()
            
            result = self.client.expire(key, seconds)
            self.logger.info(f"✓ 设置过期时间成功: {key} -> {seconds}秒")
            return result
        except Exception as e:
            self.logger.error(f"✗ 设置过期时间失败 {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间
        
        Args:
            key: 键名
        
        Returns:
            剩余秒数（-1 表示永久，-2 表示不存在）
        
        示例：
            remaining = redis.ttl("session_token")
            if remaining > 0:
                print(f"还剩 {remaining} 秒")
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.ttl(key)
        except Exception as e:
            self.logger.error(f"✗ 获取 TTL 失败 {key}: {e}")
            return -2
    
    # ==================== 哈希操作 ====================
    
    def hset(self, name: str, key: str, value: Any) -> int:
        """
        设置哈希字段
        
        Args:
            name: 哈希表名
            key: 字段名
            value: 值
        
        Returns:
            新增字段数量
        
        示例：
            redis.hset("user:1001", "name", "张三")
            redis.hset("user:1001", "age", 25)
        """
        try:
            if not self.client:
                self.connect()
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = self.client.hset(name, key, value)
            self.logger.info(f"✓ 设置哈希字段成功: {name}.{key}")
            return result
        except Exception as e:
            self.logger.error(f"✗ 设置哈希字段失败 {name}.{key}: {e}")
            return 0
    
    def hget(self, name: str, key: str, parse_json: bool = False) -> Optional[Any]:
        """
        获取哈希字段值
        
        Args:
            name: 哈希表名
            key: 字段名
            parse_json: 是否解析 JSON
        
        Returns:
            字段值
        
        示例：
            name = redis.hget("user:1001", "name")
        """
        try:
            if not self.client:
                self.connect()
            
            value = self.client.hget(name, key)
            
            if value and parse_json:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            
            return value
        except Exception as e:
            self.logger.error(f"✗ 获取哈希字段失败 {name}.{key}: {e}")
            return None
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """
        获取哈希表所有字段
        
        Args:
            name: 哈希表名
        
        Returns:
            字段字典
        
        示例：
            user_info = redis.hgetall("user:1001")
            print(user_info)  # {"name": "张三", "age": "25"}
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.hgetall(name)
        except Exception as e:
            self.logger.error(f"✗ 获取哈希表失败 {name}: {e}")
            return {}
    
    # ==================== 列表操作 ====================
    
    def lpush(self, key: str, *values: Any) -> int:
        """
        从列表左侧插入元素
        
        Args:
            key: 列表键名
            *values: 值列表
        
        Returns:
            列表长度
        
        示例：
            redis.lpush("tasks", "task1", "task2")
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.lpush(key, *values)
        except Exception as e:
            self.logger.error(f"✗ 列表左插入失败 {key}: {e}")
            return 0
    
    def rpush(self, key: str, *values: Any) -> int:
        """
        从列表右侧插入元素
        
        Args:
            key: 列表键名
            *values: 值列表
        
        Returns:
            列表长度
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.rpush(key, *values)
        except Exception as e:
            self.logger.error(f"✗ 列表右插入失败 {key}: {e}")
            return 0
    
    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        获取列表范围内的元素
        
        Args:
            key: 列表键名
            start: 起始索引
            end: 结束索引（-1 表示到末尾）
        
        Returns:
            元素列表
        
        示例：
            tasks = redis.lrange("tasks", 0, 9)  # 获取前10个
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.lrange(key, start, end)
        except Exception as e:
            self.logger.error(f"✗ 获取列表范围失败 {key}: {e}")
            return []
    
    # ==================== 工具方法 ====================
    
    def keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的所有键
        
        Args:
            pattern: 匹配模式（支持通配符 *）
        
        Returns:
            键列表
        
        示例：
            all_keys = redis.keys()
            user_keys = redis.keys("user:*")
        
        注意：生产环境慎用，大量键时会阻塞 Redis
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.keys(pattern)
        except Exception as e:
            self.logger.error(f"✗ 获取键列表失败: {e}")
            return []
    
    def flushdb(self):
        """
        清空当前数据库
        
        警告：此操作会删除当前 DB 的所有数据，请谨慎使用
        """
        try:
            if not self.client:
                self.connect()
            
            self.client.flushdb()
            self.logger.warning(f"⚠️ 已清空 Redis 数据库 {self.db}")
        except Exception as e:
            self.logger.error(f"✗ 清空数据库失败: {e}")
    
    def info(self) -> Dict[str, Any]:
        """
        获取 Redis 服务器信息
        
        Returns:
            服务器信息字典
        """
        try:
            if not self.client:
                self.connect()
            
            return self.client.info()
        except Exception as e:
            self.logger.error(f"✗ 获取服务器信息失败: {e}")
            return {}
    
    def __enter__(self):
        """支持上下文管理器"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.close()


if __name__ == '__main__':
    # 使用示例
    # redis_client = RedisHelper(host="localhost", port=6379, db=0)
    # 
    # # 方式一：手动管理连接
    # redis_client.connect()
    # redis_client.set("test_key", "test_value", ex=60)
    # value = redis_client.get("test_key")
    # redis_client.close()
    # 
    # # 方式二：使用上下文管理器（推荐）
    # with RedisHelper() as redis_client:
    #     redis_client.set("user:1001", {"name": "张三", "age": 25})
    #     user_info = redis_client.get("user:1001", parse_json=True)
    #     print(user_info)
    
    print("Redis 工具模块已加载")
