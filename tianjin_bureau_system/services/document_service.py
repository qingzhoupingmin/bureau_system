# -*- coding: utf-8 -*-
"""
公文服务
"""
from models.document import Document
from db.connection import db


class DocumentService:
    """公文服务"""

    @staticmethod
    def get_all_documents(filters=None):
        """获取公文列表"""
        return Document.get_all_documents(filters)

    @staticmethod
    def get_document_by_id(doc_id):
        """获取公文详情"""
        return Document.get_by_id(doc_id)

    @staticmethod
    def create_document(data, sender_id, sender_org_id):
        """创建公文"""
        return Document.create_document(
            data['title'], data['content'], data.get('doc_type', 'notice'),
            sender_id, sender_org_id, data.get('receiver_org_ids', ''),
            data.get('is_official', 0),
            data.get('attachment', '')
        )

    @staticmethod
    def update_document(doc_id, data):
        """更新公文"""
        return Document.update_document(
            doc_id, data['title'], data['content'], data.get('doc_type', 'notice'),
            data.get('receiver_org_ids', ''), data.get('is_official', 0),
            data.get('attachment', '')
        )

    @staticmethod
    def publish_document(doc_id):
        """发布公文"""
        return Document.publish_document(doc_id)

    @staticmethod
    def delete_document(doc_id):
        """删除公文"""
        return Document.delete_document(doc_id)

    @staticmethod
    def get_received_documents(receiver_org_ids):
        """获取接收的公文"""
        return Document.get_documents_by_receiver(receiver_org_ids)