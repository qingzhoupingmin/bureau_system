# -*- coding: utf-8 -*-
"""
用户模型
"""
from db.connection import db


class User:
    """用户模型"""

    @staticmethod
    def get_by_id(user_id):
        """根据ID获取用户"""
        sql = "SELECT * FROM users WHERE id = %s"
        result = db.execute_query(sql, (user_id,))
        return result[0] if result else None

    @staticmethod
    def get_by_username(username):
        """根据用户名获取用户"""
        sql = "SELECT * FROM users WHERE username = %s"
        result = db.execute_query(sql, (username,))
        return result[0] if result else None

    @staticmethod
    def verify_login(username, password):
        """验证登录"""
        # 重置数据库连接以确保 fresh connection
        db.reset()

        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        result = db.execute_query(sql, (username, password_hash))
        return result[0] if result else None

    @staticmethod
    def get_all_users():
        """获取所有用户"""
        sql = "SELECT u.*, o.name as org_name FROM users u LEFT JOIN organizations o ON u.organization_id = o.id"
        return db.execute_query(sql)

    @staticmethod
    def get_users_by_org(org_id):
        """根据组织获取用户"""
        sql = "SELECT * FROM users WHERE organization_id = %s"
        return db.execute_query(sql, (org_id,))

    @staticmethod
    def create_user(username, password, role, org_id, full_name, position=''):
        """创建用户"""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        sql = "INSERT INTO users (username, password, role, organization_id, full_name, position) VALUES (%s, %s, %s, %s, %s, %s)"
        return db.execute_update(sql, (username, password_hash, role, org_id, full_name, position))

    @staticmethod
    def update_user(user_id, full_name, position, role):
        """更新用户"""
        sql = "UPDATE users SET full_name = %s, position = %s, role = %s WHERE id = %s"
        return db.execute_update(sql, (full_name, position, role, user_id))

    @staticmethod
    def update_password(user_id, new_password):
        """修改密码"""
        import hashlib
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        sql = "UPDATE users SET password = %s WHERE id = %s"
        return db.execute_update(sql, (password_hash, user_id))

    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        sql = "DELETE FROM users WHERE id = %s"
        return db.execute_update(sql, (user_id,))