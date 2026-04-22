# -*- coding: utf-8 -*-
"""
科研服务
"""
from db.connection import db


class ResearchService:
    """科研服务"""

    @staticmethod
    def get_all_projects(filters=None):
        """获取科研项目列表"""
        sql = """SELECT r.*, u.full_name as applicant_name, o.name as org_name
                 FROM research_projects r
                 LEFT JOIN users u ON r.applicant_id = u.id
                 LEFT JOIN organizations o ON r.applicant_org_id = o.id"""
        params = []
        if filters:
            conditions = []
            if filters.get('status'):
                conditions.append("r.status = %s")
                params.append(filters['status'])
            if filters.get('applicant_org_id'):
                conditions.append("r.applicant_org_id = %s")
                params.append(filters['applicant_org_id'])
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY r.apply_date DESC"
        return db.execute_query(sql, tuple(params) if params else None)

    @staticmethod
    def get_project_by_id(project_id):
        """获取项目详情"""
        sql = """SELECT r.*, u.full_name as applicant_name, o.name as org_name
                 FROM research_projects r
                 LEFT JOIN users u ON r.applicant_id = u.id
                 LEFT JOIN organizations o ON r.applicant_org_id = o.id
                 WHERE r.id = %s"""
        result = db.execute_query(sql, (project_id,))
        return result[0] if result else None

    @staticmethod
    def create_project(data, applicant_id, applicant_org_id):
        """创建科研项目"""
        sql = "INSERT INTO research_projects (name, description, applicant_id, applicant_org_id, budget, status) VALUES (%s, %s, %s, %s, %s, 'pending')"
        return db.execute_update(sql, (data['name'], data.get('description', ''), applicant_id, applicant_org_id, data.get('budget', 0)))

    @staticmethod
    def approve_project(project_id, approver_id, comment):
        """审批科研项目"""
        sql = "UPDATE research_projects SET status='approved', approver_id=%s, approve_date=NOW(), approve_comment=%s WHERE id=%s"
        result = db.execute_update(sql, (approver_id, comment, project_id))
        # 创建科研经费记录
        project = ResearchService.get_project_by_id(project_id)
        if project and project['budget']:
            sql = "INSERT INTO research_funds (project_id, total_budget) VALUES (%s, %s)"
            db.execute_update(sql, (project_id, project['budget']))
        return result

    @staticmethod
    def reject_project(project_id, approver_id, comment):
        """拒绝科研项目"""
        sql = "UPDATE research_projects SET status='rejected', approver_id=%s, approve_date=NOW(), approve_comment=%s WHERE id=%s"
        return db.execute_update(sql, (approver_id, comment, project_id))

    @staticmethod
    def allocate_fund(project_id, amount):
        """拨付科研经费"""
        sql = "UPDATE research_funds SET allocated = allocated + %s WHERE project_id = %s"
        return db.execute_update(sql, (amount, project_id))

    @staticmethod
    def get_funds(project_id):
        """获取项目经费"""
        sql = "SELECT * FROM research_funds WHERE project_id = %s"
        result = db.execute_query(sql, (project_id,))
        return result[0] if result else None