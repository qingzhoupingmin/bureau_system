# -*- coding: utf-8 -*-
"""
认证服务
"""
from models.user import User


class AuthService:
    """认证服务"""

    @staticmethod
    def login(username, password):
        """用户登录"""
        user = User.verify_login(username, password)
        if user:
            # 记录登录日志
            from db.connection import db
            sql = "INSERT INTO login_logs (user_id, username, ip_address, status) VALUES (%s, %s, %s, 'success')"
            db.execute_update(sql, (user['id'], username, 'localhost'))
            return user
        return None

    @staticmethod
    def logout(user_id):
        """用户登出"""
        from db.connection import db
        sql = "UPDATE login_logs SET logout_time=NOW(), status='logout' WHERE user_id=%s AND logout_time IS NULL"
        db.execute_update(sql, (user_id,))

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        # 验证旧密码
        user = User.get_by_id(user_id)
        if not user:
            return False, "用户不存在"

        import hashlib
        old_hash = hashlib.sha256(old_password.encode()).hexdigest()
        if user['password'] != old_hash:
            return False, "原密码错误"

        # 更新密码
        User.update_password(user_id, new_password)
        return True, "密码修改成功"

    @staticmethod
    def check_permission(user, required_role):
        """检查权限"""
        role_hierarchy = {
            'system_admin': 10,
            'leader': 9,
            'asset_manager': 8,
            'office_staff': 7,
            'tech_staff': 6,
            'finance_staff': 6,
            'unit_user': 5,
            'sub_unit_user': 4,  # 下属单位的下属单位
            'normal_user': 1
        }
        user_level = role_hierarchy.get(user['role'], 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level