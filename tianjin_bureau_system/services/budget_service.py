# -*- coding: utf-8 -*-
"""
预算服务
"""
from db.connection import db


class BudgetService:
    """预算服务"""

    @staticmethod
    def get_all_applications(filters=None):
        """获取预算申请列表"""
        sql = """SELECT b.*, o.name as org_name
                 FROM budget_applications b
                 LEFT JOIN organizations o ON b.organization_id = o.id"""
        params = []
        if filters:
            conditions = []
            if filters.get('status'):
                conditions.append("b.status = %s")
                params.append(filters['status'])
            if filters.get('organization_id'):
                conditions.append("b.organization_id = %s")
                params.append(filters['organization_id'])
            if filters.get('year'):
                conditions.append("b.year = %s")
                params.append(filters['year'])
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY b.apply_date DESC"
        return db.execute_query(sql, tuple(params) if params else None)

    @staticmethod
    def get_application_by_id(app_id):
        """获取预算申请详情"""
        sql = """SELECT b.*, o.name as org_name
                 FROM budget_applications b
                 LEFT JOIN organizations o ON b.organization_id = o.id
                 WHERE b.id = %s"""
        result = db.execute_query(sql, (app_id,))
        return result[0] if result else None

    @staticmethod
    def create_application(data, organization_id):
        """创建预算申请"""
        sql = "INSERT INTO budget_applications (organization_id, year, amount, purpose, type, status) VALUES (%s, %s, %s, %s, %s, 'pending')"
        return db.execute_update(sql, (organization_id, data['year'], data['amount'], data.get('purpose', ''), data.get('type', '下属单位')))

    @staticmethod
    def approve_application(app_id, approver_id, comment):
        """审批预算申请"""
        sql = "UPDATE budget_applications SET status='approved', approver_id=%s, approve_date=NOW(), approve_comment=%s WHERE id=%s"
        return db.execute_update(sql, (approver_id, comment, app_id))

    @staticmethod
    def reject_application(app_id, approver_id, comment):
        """拒绝预算申请"""
        sql = "UPDATE budget_applications SET status='rejected', approver_id=%s, approve_date=NOW(), approve_comment=%s WHERE id=%s"
        return db.execute_update(sql, (approver_id, comment, app_id))

    @staticmethod
    def get_statistics(year=None):
        """获取预算统计"""
        sql = "SELECT organization_id, o.name as org_name, SUM(amount) as total FROM budget_applications b LEFT JOIN organizations o ON b.organization_id = o.id"
        params = []
        if year:
            sql += " WHERE b.year = %s"
            params.append(year)
        sql += " GROUP BY b.organization_id"
        return db.execute_query(sql, tuple(params) if params else None)