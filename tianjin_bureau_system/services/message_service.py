# -*- coding: utf-8 -*-
"""
消息服务
"""
from models.message import Message
from db.connection import db


class MessageService:
    """消息服务"""

    @staticmethod
    def get_all_messages(filters=None):
        """获取消息列表"""
        return Message.get_all_messages(filters)

    @staticmethod
    def get_message_by_id(msg_id):
        """获取消息详情"""
        return Message.get_by_id(msg_id)

    @staticmethod
    def get_received_messages(receiver_org_id):
        """获取接收的消息"""
        return Message.get_messages_by_receiver(receiver_org_id)

    @staticmethod
    def get_official_messages():
        """获取局名义通知"""
        return Message.get_official_messages()

    @staticmethod
    def create_message(data, sender_id, sender_org_id):
        """创建消息"""
        return Message.create_message(
            data['title'], data['content'], sender_id, sender_org_id,
            data.get('receiver_org_id'), data.get('message_type', 'business'),
            data.get('is_public', 0)
        )

    @staticmethod
    def delete_message(msg_id):
        """删除消息"""
        return Message.delete_message(msg_id)

    @staticmethod
    def get_replies(message_id):
        """获取消息回复"""
        return Message.get_replies(message_id)

    @staticmethod
    def add_reply(message_id, reply_user_id, reply_org_id, content):
        """添加回复"""
        return Message.add_reply(message_id, reply_user_id, reply_org_id, content)

    @staticmethod
    def create_official_notice(data, sender_id, sender_org_id):
        """创建局名义通知"""
        return Message.create_message(
            data['title'], data['content'], sender_id, sender_org_id,
            None, 'official', 1
        )