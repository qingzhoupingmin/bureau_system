# -*- coding: utf-8 -*-
"""
公文模型
"""
from db.connection import db


class Document:
    """公文模型"""

    @staticmethod
    def get_by_id(doc_id):
        """根据ID获取公文"""
        sql = "SELECT d.*, u.full_name as sender_name, o.name as org_name FROM documents d LEFT JOIN users u ON d.sender_id = u.id LEFT JOIN organizations o ON d.sender_org_id = o.id WHERE d.id = %s"
        result = db.execute_query(sql, (doc_id,))
        return result[0] if result else None

    @staticmethod
    def get_all_documents(filters=None):
        """获取所有公文"""
        sql = """SELECT d.*, u.full_name as sender_name, o.name as org_name
                 FROM documents d
                 LEFT JOIN users u ON d.sender_id = u.id
                 LEFT JOIN organizations o ON d.sender_org_id = o.id"""
        params = []
        if filters:
            conditions = []
            if filters.get('status'):
                conditions.append("d.status = %s")
                params.append(filters['status'])
            if filters.get('doc_type'):
                conditions.append("d.doc_type = %s")
                params.append(filters['doc_type'])
            if filters.get('sender_id'):
                conditions.append("d.sender_id = %s")
                params.append(filters['sender_id'])
            if filters.get('is_official') is not None:
                conditions.append("d.is_official = %s")
                params.append(filters['is_official'])
            if filters.get('keyword'):
                conditions.append("d.title LIKE %s")
                params.append(f"%{filters['keyword']}%")
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY d.create_date DESC"
        return db.execute_query(sql, tuple(params) if params else None)

    @staticmethod
    def get_documents_by_receiver(receiver_org_ids):
        """获取发送给指定组织的公文"""
        if not receiver_org_ids:
            return []
        sql = """SELECT d.*, u.full_name as sender_name, o.name as org_name
                 FROM documents d
                 LEFT JOIN users u ON d.sender_id = u.id
                 LEFT JOIN organizations o ON d.sender_org_id = o.id
                 WHERE d.status = 'published' AND (d.receiver_org_ids IS NULL OR d.receiver_org_ids = '' OR d.receiver_org_ids LIKE %s)
                 ORDER BY d.publish_date DESC"""
        return db.execute_query(sql, (f'%{receiver_org_ids}%',))

    @staticmethod
    def create_document(title, content, doc_type, sender_id, sender_org_id, receiver_org_ids, is_official, attachment=''):
        """创建公文"""
        sql = """INSERT INTO documents
                 (title, content, attachment, doc_type, sender_id, sender_org_id, receiver_org_ids, is_official, status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'draft')"""
        return db.execute_update(sql, (title, content, attachment, doc_type, sender_id, sender_org_id, receiver_org_ids, is_official))

    @staticmethod
    def update_document(doc_id, title, content, doc_type, receiver_org_ids, is_official, attachment=''):
        """更新公文"""
        sql = """UPDATE documents SET
                 title=%s, content=%s, attachment=%s, doc_type=%s, receiver_org_ids=%s, is_official=%s
                 WHERE id=%s"""
        return db.execute_update(sql, (title, content, attachment, doc_type, receiver_org_ids, is_official, doc_id))

    @staticmethod
    def publish_document(doc_id):
        """发布公文"""
        sql = "UPDATE documents SET status='published', publish_date=NOW() WHERE id=%s"
        return db.execute_update(sql, (doc_id,))

    @staticmethod
    def approve_document(doc_id):
        """审核通过公文"""
        sql = "UPDATE documents SET status='approved' WHERE id=%s"
        return db.execute_update(sql, (doc_id,))

    @staticmethod
    def delete_document(doc_id):
        """删除公文"""
        sql = "DELETE FROM documents WHERE id = %s"
        return db.execute_update(sql, (doc_id,))