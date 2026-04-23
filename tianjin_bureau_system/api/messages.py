# -*- coding: utf-8 -*-
"""
消息管理接口
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from db.connection import db
from api.pagination import PaginationParams, PaginatedResponse, paginate_query, count_query

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
    request: Request,
    receiver_id: Optional[int] = None,
    sender_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取消息列表（支持分页）
    """
    pagination = PaginationParams(page=page, page_size=page_size)

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

    # 获取总数
    count_sql = count_query(sql)
    total_result = db.execute_query(count_sql, tuple(params) if params else None)
    total = total_result[0].get('total', 0) if total_result else 0

    # 添加分页
    sql += " ORDER BY m.create_date DESC"
    paginated_sql, paginated_params = paginate_query(sql, tuple(params) if params else (), pagination)

    messages = db.execute_query(paginated_sql, paginated_params)

    return PaginatedResponse.create(messages, total, pagination).dict()


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


@router.get("/unread-count")
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


@router.post("/broadcast")
def broadcast_message(
    title: str,
    content: str,
    sender_id: int,
    org_id: int,  # 发送方组织ID
    target_type: str = "all"  # all, department, unit, sub_unit
):
    """
    广播消息（局名义发送，仅办公室）
    """
    from models.user import User

    # 验证发送方是否为办公室
    sender = User.get_by_id(sender_id)
    if not sender or sender['role'] != 'office_staff':
        raise HTTPException(status_code=403, detail="只有办公室可以发送局名义消息")

    # 获取目标用户
    sql = """SELECT u.id as user_id
             FROM users u
             LEFT JOIN organizations o ON u.organization_id = o.id
             WHERE 1=1"""
    params = []

    if target_type == 'department':
        sql += " AND o.type = 'department'"
    elif target_type == 'unit':
        sql += " AND o.type = 'unit'"
    elif target_type == 'sub_unit':
        sql += " AND o.type = 'sub_unit'"

    users = db.execute_query(sql, tuple(params) if params else None)

    if not users:
        return {
            "code": 200,
            "message": "没有目标用户",
            "data": {"sent_count": 0}
        }

    # 批量发送消息
    sent_count = 0
    for user_data in users:
        sql = """INSERT INTO messages
                 (title, content, message_type, sender_id, receiver_id, is_read, create_date)
                 VALUES (%s, %s, 'official', %s, %s, 0, NOW())"""
        db.execute_update(sql, (title, content, sender_id, user_data['user_id']))
        sent_count += 1

    return {
        "code": 200,
        "message": "广播消息发送成功",
        "data": {"sent_count": sent_count}
    }


@router.post("/business-notice")
def send_business_notice(
    title: str,
    content: str,
    sender_id: int,
    sender_org_id: int,
    target_org_id: int
):
    """
    发送业务通知（各处室间）
    """
    # 获取目标组织的所有用户
    sql = "SELECT id FROM users WHERE organization_id = %s"
    users = db.execute_query(sql, (target_org_id,))

    if not users:
        return {
            "code": 200,
            "message": "目标组织没有用户",
            "data": {"sent_count": 0}
        }

    # 批量发送消息
    sent_count = 0
    for user_data in users:
        sql = """INSERT INTO messages
                 (title, content, message_type, sender_id, receiver_id, is_read, create_date)
                 VALUES (%s, %s, 'business', %s, %s, 0, NOW())"""
        db.execute_update(sql, (title, content, sender_id, user_data['id']))
        sent_count += 1

    return {
        "code": 200,
        "message": "业务通知发送成功",
        "data": {"sent_count": sent_count}
    }