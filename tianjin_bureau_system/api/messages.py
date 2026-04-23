# -*- coding: utf-8 -*-
"""
消息管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.connection import db

router = APIRouter(prefix="/api/messages", tags=["消息管理"])


class SendMessageRequest(BaseModel):
    title: str
    content: str
    message_type: str
    sender_id: int
    receiver_id: int


class ReadMessageRequest(BaseModel):
    reader_id: int


@router.get("")
def get_messages(
    receiver_id: Optional[int] = None,
    sender_id: Optional[int] = None,
    is_read: Optional[bool] = None
):
    """
    获取消息列表
    """
    sql = """SELECT m.*, s.full_name as sender_name, r.full_name as receiver_name
             FROM messages m
             LEFT JOIN users s ON m.sender_id = s.id
             LEFT JOIN users r ON m.receiver_id = r.id
             WHERE 1=1"""
    params = []

    if receiver_id:
        sql += " AND m.receiver_id = %s"
        params.append(receiver_id)
    if sender_id:
        sql += " AND m.sender_id = %s"
        params.append(sender_id)
    if is_read is not None:
        sql += " AND m.is_read = %s"
        params.append(1 if is_read else 0)

    sql += " ORDER BY m.create_date DESC"

    messages = db.execute_query(sql, tuple(params) if params else None)

    return {
        "code": 200,
        "data": messages,
        "total": len(messages)
    }


@router.get("/{msg_id}")
def get_message(msg_id: int):
    """
    获取消息详情
    """
    sql = """SELECT m.*, s.full_name as sender_name, r.full_name as receiver_name
             FROM messages m
             LEFT JOIN users s ON m.sender_id = s.id
             LEFT JOIN users r ON m.receiver_id = r.id
             WHERE m.id = %s"""
    result = db.execute_query(sql, (msg_id,))

    if not result:
        raise HTTPException(status_code=404, detail="消息不存在")

    return {
        "code": 200,
        "data": result[0]
    }


@router.post("")
def send_message(req: SendMessageRequest):
    """
    发送消息
    """
    sql = """INSERT INTO messages
             (title, content, message_type, sender_id, receiver_id, is_read, create_date)
             VALUES (%s, %s, %s, %s, %s, 0, NOW())"""
    msg_id = db.execute_update(sql, (
        req.title, req.content, req.message_type,
        req.sender_id, req.receiver_id
    ))

    return {
        "code": 200,
        "message": "消息发送成功",
        "data": {"msg_id": msg_id}
    }


@router.delete("/{msg_id}")
def delete_message(msg_id: int):
    """
    删除消息
    """
    sql = "SELECT * FROM messages WHERE id = %s"
    result = db.execute_query(sql, (msg_id,))
    if not result:
        raise HTTPException(status_code=404, detail="消息不存在")

    sql = "DELETE FROM messages WHERE id = %s"
    db.execute_update(sql, (msg_id,))

    return {
        "code": 200,
        "message": "消息删除成功"
    }


@router.put("/{msg_id}/read")
def mark_as_read(msg_id: int, req: ReadMessageRequest):
    """
    标记消息为已读
    """
    sql = "SELECT * FROM messages WHERE id = %s"
    result = db.execute_query(sql, (msg_id,))
    if not result:
        raise HTTPException(status_code=404, detail="消息不存在")

    sql = "UPDATE messages SET is_read = 1, read_date = NOW() WHERE id = %s"
    db.execute_update(sql, (msg_id,))

    return {
        "code": 200,
        "message": "消息已标记为已读"
    }


@router.get("/unread/count")
def get_unread_count(receiver_id: int):
    """
    获取未读消息数量
    """
    sql = "SELECT COUNT(*) as count FROM messages WHERE receiver_id = %s AND is_read = 0"
    result = db.execute_query(sql, (receiver_id,))

    count = result[0].get('count', 0) if result else 0

    return {
        "code": 200,
        "data": {"unread_count": count}
    }