# -*- coding: utf-8 -*-
"""
资产服务
"""
from models.asset import Asset
from db.connection import db


class AssetService:
    """资产服务"""

    @staticmethod
    def get_all_assets(filters=None):
        """获取资产列表"""
        return Asset.get_all_assets(filters)

    @staticmethod
    def get_asset_by_id(asset_id):
        """获取资产详情"""
        return Asset.get_by_id(asset_id)

    @staticmethod
    def create_asset(data):
        """创建资产"""
        return Asset.create_asset(
            data['name'], data['category'], data.get('model', ''),
            data.get('serial_number', ''), data.get('purchase_date'),
            data.get('price', 0), data.get('location', ''),
            data.get('status', 'normal'), data.get('organization_id'),
            data.get('is_public', 0), data.get('caretaker', '')
        )

    @staticmethod
    def update_asset(asset_id, data):
        """更新资产"""
        return Asset.update_asset(
            asset_id, data['name'], data['category'], data.get('model', ''),
            data.get('serial_number', ''), data.get('purchase_date'),
            data.get('price', 0), data.get('location', ''),
            data.get('status', 'normal'), data.get('organization_id'),
            data.get('is_public', 0), data.get('caretaker', '')
        )

    @staticmethod
    def delete_asset(asset_id):
        """删除资产"""
        return Asset.delete_asset(asset_id)

    @staticmethod
    def get_statistics():
        """获取资产统计"""
        return Asset.get_statistics()

    @staticmethod
    def apply_for_asset(asset_id, applicant_id, applicant_org_id, reason):
        """申请使用资产"""
        sql = "INSERT INTO asset_applications (asset_id, applicant_id, applicant_org_id, reason, status) VALUES (%s, %s, %s, %s, 'pending')"
        return db.execute_update(sql, (asset_id, applicant_id, applicant_org_id, reason))

    @staticmethod
    def get_applications(filters=None):
        """获取申请列表"""
        sql = """SELECT a.*, ast.name as asset_name, u.full_name as applicant_name, o.name as org_name
                 FROM asset_applications a
                 LEFT JOIN assets ast ON a.asset_id = ast.id
                 LEFT JOIN users u ON a.applicant_id = u.id
                 LEFT JOIN organizations o ON a.applicant_org_id = o.id"""
        params = []
        if filters:
            conditions = []
            if filters.get('status'):
                conditions.append("a.status = %s")
                params.append(filters['status'])
            if filters.get('applicant_id'):
                conditions.append("a.applicant_id = %s")
                params.append(filters['applicant_id'])
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY a.apply_date DESC"
        return db.execute_query(sql, tuple(params) if params else None)

    @staticmethod
    def approve_application(app_id, approver_id, comment):
        """审批申请"""
        sql = "UPDATE asset_applications SET status='approved', approver_id=%s, approve_date=NOW(), approve_comment=%s WHERE id=%s"
        db.execute_update(sql, (approver_id, comment, app_id))
        # 更新资产状态
        sql = "SELECT asset_id FROM asset_applications WHERE id = %s"
        result = db.execute_query(sql, (app_id,))
        if result:
            sql = "UPDATE assets SET status='borrowed' WHERE id = %s"
            db.execute_update(sql, (result[0]['asset_id'],))

    @staticmethod
    def reject_application(app_id, approver_id, comment):
        """拒绝申请"""
        sql = "UPDATE asset_applications SET status='rejected', approver_id=%s, approve_date=NOW(), approve_comment=%s WHERE id=%s"
        return db.execute_update(sql, (approver_id, comment, app_id))