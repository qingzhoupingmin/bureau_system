# -*- coding: utf-8 -*-
"""
组织模型
"""
from db.connection import db


class Organization:
    """组织模型"""

    @staticmethod
    def get_by_id(org_id):
        """根据ID获取组织"""
        sql = "SELECT * FROM organizations WHERE id = %s"
        result = db.execute_query(sql, (org_id,))
        return result[0] if result else None

    @staticmethod
    def get_all_organizations(org_type=None):
        """获取所有组织"""
        if org_type:
            sql = "SELECT * FROM organizations WHERE type = %s ORDER BY sort_order"
            return db.execute_query(sql, (org_type,))
        sql = "SELECT * FROM organizations ORDER BY type, sort_order"
        return db.execute_query(sql)

    @staticmethod
    def get_departments():
        """获取机关处室"""
        sql = "SELECT * FROM organizations WHERE type = 'department' ORDER BY sort_order"
        return db.execute_query(sql)

    @staticmethod
    def get_units():
        """获取下属单位"""
        sql = "SELECT * FROM organizations WHERE type = 'unit' ORDER BY sort_order"
        return db.execute_query(sql)

    @staticmethod
    def create_organization(name, org_type, parent_id=None, sort_order=0):
        """创建组织"""
        sql = "INSERT INTO organizations (name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s)"
        return db.execute_update(sql, (name, org_type, parent_id, sort_order))

    @staticmethod
    def update_organization(org_id, name, sort_order):
        """更新组织"""
        sql = "UPDATE organizations SET name=%s, sort_order=%s WHERE id=%s"
        return db.execute_update(sql, (name, sort_order, org_id))

    @staticmethod
    def delete_organization(org_id):
        """删除组织"""
        sql = "DELETE FROM organizations WHERE id = %s"
        return db.execute_update(sql, (org_id,))