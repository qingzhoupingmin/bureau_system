# -*- coding: utf-8 -*-
"""
资产模型
"""
from db.connection import db


class Asset:
    """资产模型"""

    @staticmethod
    def get_by_id(asset_id):
        """根据ID获取资产"""
        sql = "SELECT a.*, o.name as org_name FROM assets a LEFT JOIN organizations o ON a.organization_id = o.id WHERE a.id = %s"
        result = db.execute_query(sql, (asset_id,))
        return result[0] if result else None

    @staticmethod
    def get_all_assets(filters=None):
        """获取所有资产"""
        sql = "SELECT a.*, o.name as org_name FROM assets a LEFT JOIN organizations o ON a.organization_id = o.id"
        params = []
        if filters:
            conditions = []
            if filters.get('category'):
                conditions.append("a.category = %s")
                params.append(filters['category'])
            if filters.get('status'):
                conditions.append("a.status = %s")
                params.append(filters['status'])
            if filters.get('organization_id'):
                conditions.append("a.organization_id = %s")
                params.append(filters['organization_id'])
            if filters.get('is_public') is not None:
                conditions.append("a.is_public = %s")
                params.append(filters['is_public'])
            if filters.get('keyword'):
                conditions.append("a.name LIKE %s")
                params.append(f"%{filters['keyword']}%")
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY a.id DESC"
        return db.execute_query(sql, tuple(params) if params else None)

    @staticmethod
    def get_assets_by_org(org_id):
        """根据组织获取资产"""
        sql = "SELECT * FROM assets WHERE organization_id = %s ORDER BY id DESC"
        return db.execute_query(sql, (org_id,))

    @staticmethod
    def get_public_assets():
        """获取公用资产"""
        sql = "SELECT a.*, o.name as org_name FROM assets a LEFT JOIN organizations o ON a.organization_id = o.id WHERE a.is_public = 1 ORDER BY a.id DESC"
        return db.execute_query(sql)

    @staticmethod
    def create_asset(name, category, model, serial_number, purchase_date, price, location, status, organization_id, is_public, caretaker):
        """创建资产"""
        sql = """INSERT INTO assets
                 (name, category, sub_category, model, serial_number, purchase_date, price, location, status, organization_id, is_public, caretaker)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        return db.execute_update(sql, (name, category, '', model, serial_number, purchase_date, price, location, status, organization_id, is_public, caretaker))

    @staticmethod
    def update_asset(asset_id, name, category, model, serial_number, purchase_date, price, location, status, organization_id, is_public, caretaker):
        """更新资产"""
        sql = """UPDATE assets SET
                 name=%s, category=%s, model=%s, serial_number=%s, purchase_date=%s,
                 price=%s, location=%s, status=%s, organization_id=%s, is_public=%s, caretaker=%s
                 WHERE id=%s"""
        return db.execute_update(sql, (name, category, model, serial_number, purchase_date, price, location, status, organization_id, is_public, caretaker, asset_id))

    @staticmethod
    def delete_asset(asset_id):
        """删除资产"""
        sql = "DELETE FROM assets WHERE id = %s"
        return db.execute_update(sql, (asset_id,))

    @staticmethod
    def get_statistics():
        """获取资产统计"""
        stats = {}

        # 总数
        sql = "SELECT COUNT(*) as total FROM assets"
        result = db.execute_query(sql)
        stats['total'] = result[0]['total']

        # 总金额
        sql = "SELECT SUM(price) as total_price FROM assets"
        result = db.execute_query(sql)
        stats['total_price'] = result[0]['total_price'] or 0

        # 按类别统计
        sql = "SELECT category, COUNT(*) as count FROM assets GROUP BY category"
        result = db.execute_query(sql)
        stats['by_category'] = {r['category']: r['count'] for r in result}

        # 按状态统计
        sql = "SELECT status, COUNT(*) as count FROM assets GROUP BY status"
        result = db.execute_query(sql)
        stats['by_status'] = {r['status']: r['count'] for r in result}

        # 按处室统计
        sql = """SELECT o.name, COUNT(a.id) as count
                 FROM assets a LEFT JOIN organizations o ON a.organization_id = o.id
                 WHERE a.organization_id IS NOT NULL
                 GROUP BY a.organization_id"""
        result = db.execute_query(sql)
        stats['by_org'] = {r['name']: r['count'] for r in result}

        return stats