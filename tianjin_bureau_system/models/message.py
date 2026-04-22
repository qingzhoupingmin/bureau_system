# -*- coding: utf-8 -*-
"""
消息模型
"""
from db.connection import db


class Message:
    """消息模型"""

    @staticmethod
    def get_by_id(msg_id):
        """根据ID获取消息"""
        sql = "SELECT m.*, u.full_name as sender_name, o.name as org_name FROM messages m LEFT JOIN users u ON m.sender_id = u.id LEFT JOIN organizations o ON m.sender_org_id = o.id WHERE m.id = %s"
        result = db.execute_query(sql, (msg_id,))
        return result[0] if result else None

    @staticmethod
    def get_all_messages(filters=None):
        """获取所有消息"""
        sql = """SELECT m.*, u.full_name as sender_name, o.name as org_name
                 FROM messages m
                 LEFT JOIN users u ON m.sender_id = u.id
                 LEFT JOIN organizations o ON m.sender_org_id = o.id"""
        params = []
        if filters:
            conditions = []
            if filters.get('message_type'):
                conditions.append("m.message_type = %s")
                params.append(filters['message_type'])
            if filters.get('sender_id'):
                conditions.append("m.sender_id = %s")
                params.append(filters['sender_id'])
            if filters.get('keyword'):
                conditions.append("m.title LIKE %s")
                params.append(f"%{filters['keyword']}%")
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY m.create_date DESC"
        return db.execute_query(sql, tuple(params) if params else None)

    @staticmethod
    def get_messages_by_receiver(receiver_org_id):
        """获取接收到的消息"""
        sql = """SELECT m.*, u.full_name as sender_name, o.name as org_name
                 FROM messages m
                 LEFT JOIN users u ON m.sender_id = u.id
                 LEFT JOIN organizations o ON m.sender_org_id = o.id
                 WHERE (m.receiver_org_id = %s OR m.is_public = 1)
                 ORDER BY m.create_date DESC"""
        return db.execute_query(sql, (receiver_org_id,))

    @staticmethod
    def get_official_messages():
        """获取局名义通知"""
        sql = """SELECT m.*, u.full_name as sender_name, o.name as org_name
                 FROM messages m
                 LEFT JOIN users u ON m.sender_id = u.id
                 LEFT JOIN organizations o ON m.sender_org_id = o.id
                 WHERE m.message_type = 'official'
                 ORDER BY m.create_date DESC"""
        return db.execute_query(sql)

    @staticmethod
    def create_message(title, content, sender_id, sender_org_id, receiver_org_id, message_type, is_public):
        """创建消息"""
        sql = """INSERT INTO messages
                 (title, content, sender_id, sender_org_id, receiver_org_id, message_type, is_public)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        return db.execute_update(sql, (title, content, sender_id, sender_org_id, receiver_org_id, message_type, is_public))

    @staticmethod
    def delete_message(msg_id):
        """删除消息"""
        sql = "DELETE FROM messages WHERE id = %s"
        return db.execute_update(sql, (msg_id,))

    @staticmethod
    def get_replies(message_id):
        """获取消息回复"""
        sql = """SELECT r.*, u.full_name as reply_name, o.name as org_name
                 FROM message_replies r
                 LEFT JOIN users u ON r.reply_user_id = u.id
                 LEFT JOIN organizations o ON r.reply_org_id = o.id
                 WHERE r.message_id = %s
                 ORDER BY r.reply_date"""
        return db.execute_query(sql, (message_id,))

    @staticmethod
    def add_reply(message_id, reply_user_id, reply_org_id, content):
        """添加回复"""
        sql = "INSERT INTO message_replies (message_id, reply_user_id, reply_org_id, content) VALUES (%s, %s, %s, %s)"
        return db.execute_update(sql, (message_id, reply_user_id, reply_org_id, content))