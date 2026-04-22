# -*- coding: utf-8 -*-
"""
数据库连接模块
"""
import pymysql
from config import DB_CONFIG


class DatabaseConnection:
    """数据库连接类 - 不使用单例，每次创建新连接"""

    def get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )

    def close(self):
        """关闭数据库连接"""
        pass  # 不再需要手动关闭

    def execute_query(self, sql, params=None):
        """执行查询"""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
        conn.close()
        return result

    def execute_update(self, sql, params=None):
        """执行更新/插入/删除"""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            result = cursor.execute(sql, params)
            conn.commit()
        conn.close()
        return result

    def execute_many(self, sql, params_list):
        """批量执行"""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            result = cursor.executemany(sql, params_list)
            conn.commit()
        conn.close()
        return result

    def reset(self):
        """重置连接状态（兼容旧代码）"""
        pass


# 实例
db = DatabaseConnection()