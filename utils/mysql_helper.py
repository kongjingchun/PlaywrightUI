# ========================================
# MySQL 数据库操作工具
# ========================================
# 封装 MySQL 数据库操作，提供便捷的增删改查功能
# ========================================

import pymysql
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from utils.logger import Logger


class MySQLHelper:
    """MySQL 数据库操作辅助类"""
    
    def __init__(self, host: str, port: int, user: str, password: str, 
                 database: str, charset: str = 'utf8mb4'):
        """
        初始化 MySQL 连接
        
        Args:
            host: 数据库主机地址
            port: 端口号
            user: 用户名
            password: 密码
            database: 数据库名
            charset: 字符集，默认 utf8mb4
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.logger = Logger(self.__class__.__name__)
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        连接数据库
        
        Returns:
            是否连接成功
        """
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor  # 返回字典格式
            )
            self.logger.info(f"✓ 连接 MySQL 数据库成功: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            self.logger.error(f"✗ 连接 MySQL 数据库失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            if self.connection:
                self.connection.close()
                self.connection = None
            self.logger.info("✓ MySQL 连接已关闭")
        except Exception as e:
            self.logger.error(f"✗ 关闭 MySQL 连接失败: {e}")
    
    @contextmanager
    def _get_cursor(self):
        """
        获取游标（上下文管理器）
        
        自动管理连接和游标的生命周期
        """
        should_close = False
        try:
            if not self.connection or not self.connection.open:
                self.connect()
                should_close = True
            
            cursor = self.connection.cursor()
            yield cursor
            self.connection.commit()
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            self.logger.error(f"✗ 数据库操作失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if should_close:
                self.close()
    
    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """
        执行 SQL 语句（INSERT, UPDATE, DELETE）
        
        Args:
            sql: SQL 语句
            params: 参数元组
        
        Returns:
            影响的行数
        
        示例：
            db.execute("INSERT INTO users (name, age) VALUES (%s, %s)", ("张三", 25))
            db.execute("UPDATE users SET age = %s WHERE name = %s", (26, "张三"))
            db.execute("DELETE FROM users WHERE name = %s", ("张三",))
        """
        try:
            with self._get_cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                self.logger.info(f"✓ 执行 SQL 成功，影响 {affected_rows} 行")
                self.logger.debug(f"SQL: {sql}, Params: {params}")
                return affected_rows
        except Exception as e:
            self.logger.error(f"✗ 执行 SQL 失败: {e}")
            self.logger.error(f"SQL: {sql}, Params: {params}")
            raise
    
    def execute_many(self, sql: str, params_list: List[Tuple]) -> int:
        """
        批量执行 SQL 语句
        
        Args:
            sql: SQL 语句
            params_list: 参数列表
        
        Returns:
            影响的总行数
        
        示例：
            users = [("张三", 25), ("李四", 30), ("王五", 28)]
            db.execute_many("INSERT INTO users (name, age) VALUES (%s, %s)", users)
        """
        try:
            with self._get_cursor() as cursor:
                affected_rows = cursor.executemany(sql, params_list)
                self.logger.info(f"✓ 批量执行 SQL 成功，影响 {affected_rows} 行")
                self.logger.debug(f"SQL: {sql}, Params count: {len(params_list)}")
                return affected_rows
        except Exception as e:
            self.logger.error(f"✗ 批量执行 SQL 失败: {e}")
            raise
    
    def query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        查询多条记录
        
        Args:
            sql: SQL 查询语句
            params: 参数元组
        
        Returns:
            查询结果列表（字典列表）
        
        示例：
            users = db.query("SELECT * FROM users WHERE age > %s", (25,))
            for user in users:
                print(user['name'], user['age'])
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                self.logger.info(f"✓ 查询成功，返回 {len(results)} 条记录")
                self.logger.debug(f"SQL: {sql}, Params: {params}")
                return results
        except Exception as e:
            self.logger.error(f"✗ 查询失败: {e}")
            self.logger.error(f"SQL: {sql}, Params: {params}")
            raise
    
    def query_one(self, sql: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        
        Args:
            sql: SQL 查询语句
            params: 参数元组
        
        Returns:
            查询结果（字典），如果没有结果返回 None
        
        示例：
            user = db.query_one("SELECT * FROM users WHERE name = %s", ("张三",))
            if user:
                print(user['age'])
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()
                if result:
                    self.logger.info("✓ 查询成功，返回 1 条记录")
                else:
                    self.logger.info("✓ 查询成功，无匹配记录")
                self.logger.debug(f"SQL: {sql}, Params: {params}")
                return result
        except Exception as e:
            self.logger.error(f"✗ 查询失败: {e}")
            self.logger.error(f"SQL: {sql}, Params: {params}")
            raise
    
    def query_value(self, sql: str, params: Optional[Tuple] = None) -> Any:
        """
        查询单个值（第一行第一列）
        
        Args:
            sql: SQL 查询语句
            params: 参数元组
        
        Returns:
            查询结果值
        
        示例：
            count = db.query_value("SELECT COUNT(*) as count FROM users")
            age = db.query_value("SELECT age FROM users WHERE name = %s", ("张三",))
        """
        result = self.query_one(sql, params)
        if result:
            # 返回第一个字段的值
            return list(result.values())[0]
        return None
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        插入一条记录
        
        Args:
            table: 表名
            data: 数据字典
        
        Returns:
            插入记录的 ID（自增主键）
        
        示例：
            user_id = db.insert("users", {"name": "张三", "age": 25})
        """
        try:
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
            
            with self._get_cursor() as cursor:
                cursor.execute(sql, tuple(data.values()))
                last_id = cursor.lastrowid
                self.logger.info(f"✓ 插入成功，ID: {last_id}")
                self.logger.debug(f"Table: {table}, Data: {data}")
                return last_id
        except Exception as e:
            self.logger.error(f"✗ 插入失败: {e}")
            self.logger.error(f"Table: {table}, Data: {data}")
            raise
    
    def update(self, table: str, data: Dict[str, Any], where: str, 
               where_params: Optional[Tuple] = None) -> int:
        """
        更新记录
        
        Args:
            table: 表名
            data: 要更新的数据字典
            where: WHERE 条件
            where_params: WHERE 条件参数
        
        Returns:
            影响的行数
        
        示例：
            db.update("users", {"age": 26}, "name = %s", ("张三",))
        """
        try:
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
            params = tuple(data.values()) + (where_params or ())
            
            return self.execute(sql, params)
        except Exception as e:
            self.logger.error(f"✗ 更新失败: {e}")
            raise
    
    def delete(self, table: str, where: str, where_params: Optional[Tuple] = None) -> int:
        """
        删除记录
        
        Args:
            table: 表名
            where: WHERE 条件
            where_params: WHERE 条件参数
        
        Returns:
            影响的行数
        
        示例：
            db.delete("users", "name = %s", ("张三",))
        """
        try:
            sql = f"DELETE FROM {table} WHERE {where}"
            return self.execute(sql, where_params)
        except Exception as e:
            self.logger.error(f"✗ 删除失败: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
        
        Returns:
            是否存在
        """
        sql = """
            SELECT COUNT(*) as count
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        """
        count = self.query_value(sql, (self.database, table_name))
        return count > 0
    
    def truncate_table(self, table_name: str):
        """
        清空表数据
        
        Args:
            table_name: 表名
        
        警告：此操作会删除表中所有数据，请谨慎使用
        """
        try:
            sql = f"TRUNCATE TABLE {table_name}"
            self.execute(sql)
            self.logger.info(f"✓ 清空表 {table_name} 成功")
        except Exception as e:
            self.logger.error(f"✗ 清空表 {table_name} 失败: {e}")
            raise
    
    def __enter__(self):
        """支持上下文管理器"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.close()


if __name__ == '__main__':
    # 使用示例（需要配置真实的数据库）
    # db = MySQLHelper(
    #     host="localhost",
    #     port=3306,
    #     user="root",
    #     password="password",
    #     database="test_db"
    # )
    # 
    # # 方式一：手动管理连接
    # db.connect()
    # users = db.query("SELECT * FROM users")
    # db.close()
    # 
    # # 方式二：使用上下文管理器（推荐）
    # with MySQLHelper(...) as db:
    #     users = db.query("SELECT * FROM users")
    #     print(users)
    
    print("MySQL 工具模块已加载")
