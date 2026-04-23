# -*- coding: utf-8 -*-
"""
公文管理接口
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from db.connection import db
from api.pagination import PaginationParams, PaginatedResponse, paginate_query, count_query

router = APIRouter(prefix="/api/documents", tags=["公文管理"])


class CreateDocumentRequest(BaseModel):
    title: str
    content: str
    doc_type: str
    sender_org_id: int
    sender_id: int


class PublishDocumentRequest(BaseModel):
    publisher_id: int


@router.get("")
def get_documents(
    request: Request,
    status: Optional[str] = None,
    doc_type: Optional[str] = None,
    org_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取公文列表（支持分页）
    """
    pagination = PaginationParams(page=page, page_size=page_size)

    sql = """SELECT d.*, o.name as org_name
             FROM documents d
             LEFT JOIN organizations o ON d.sender_org_id = o.id
             WHERE 1=1"""
    params = []

    if status:
        sql += " AND d.status = %s"
        params.append(status)
    if doc_type:
        sql += " AND d.doc_type = %s"
        params.append(doc_type)
    if org_id:
        sql += " AND d.sender_org_id = %s"
        params.append(org_id)

    # 获取总数
    count_sql = count_query(sql)
    total_result = db.execute_query(count_sql, tuple(params) if params else None)
    total = total_result[0].get('total', 0) if total_result else 0

    # 添加分页
    sql += " ORDER BY d.create_date DESC"
    paginated_sql, paginated_params = paginate_query(sql, tuple(params) if params else (), pagination)

    docs = db.execute_query(paginated_sql, paginated_params)

    return PaginatedResponse.create(docs, total, pagination).dict()


@router.get("/{doc_id}")
def get_document(doc_id: int):
    """
    获取公文详情
    """
    sql = "SELECT * FROM documents WHERE id = %s"
    result = db.execute_query(sql, (doc_id,))

    if not result:
        raise HTTPException(status_code=404, detail="公文不存在")

    return {
        "code": 200,
        "data": result[0]
    }


@router.post("")
def create_document(req: CreateDocumentRequest):
    """
    创建公文（草稿）
    """
    sql = """INSERT INTO documents
             (title, content, doc_type, sender_org_id, sender_id, status, create_date)
             VALUES (%s, %s, %s, %s, %s, 'draft', NOW())"""
    doc_id = db.execute_update(sql, (
        req.title, req.content, req.doc_type,
        req.sender_org_id, req.sender_id
    ))

    return {
        "code": 200,
        "message": "公文创建成功",
        "data": {"doc_id": doc_id}
    }


@router.put("/{doc_id}")
def update_document(doc_id: int, req: CreateDocumentRequest):
    """
    更新公文
    """
    sql = "SELECT * FROM documents WHERE id = %s"
    result = db.execute_query(sql, (doc_id,))
    if not result:
        raise HTTPException(status_code=404, detail="公文不存在")

    sql = """UPDATE documents
             SET title=%s, content=%s, doc_type=%s
             WHERE id=%s"""
    db.execute_update(sql, (req.title, req.content, req.doc_type, doc_id))

    return {
        "code": 200,
        "message": "公文更新成功"
    }


@router.delete("/{doc_id}")
def delete_document(doc_id: int):
    """
    删除公文
    """
    sql = "SELECT * FROM documents WHERE id = %s"
    result = db.execute_query(sql, (doc_id,))
    if not result:
        raise HTTPException(status_code=404, detail="公文不存在")

    sql = "DELETE FROM documents WHERE id = %s"
    db.execute_update(sql, (doc_id,))

    return {
        "code": 200,
        "message": "公文删除成功"
    }


@router.post("/{doc_id}/publish")
def publish_document(doc_id: int, req: PublishDocumentRequest):
    """
    发布公文
    """
    sql = "SELECT * FROM documents WHERE id = %s"
    result = db.execute_query(sql, (doc_id,))
    if not result:
        raise HTTPException(status_code=404, detail="公文不存在")

    sql = """UPDATE documents
             SET status='published', publisher_id=%s, publish_date=NOW()
             WHERE id=%s"""
    db.execute_update(sql, (req.publisher_id, doc_id))

    return {
        "code": 200,
        "message": "公文发布成功"
    }


@router.post("/{doc_id}/reply")
def reply_document(doc_id: int, sender_id: int, content: str):
    """
    回复公文
    """
    sql = "SELECT * FROM documents WHERE id = %s"
    result = db.execute_query(sql, (doc_id,))
    if not result:
        raise HTTPException(status_code=404, detail="公文不存在")

    sql = """INSERT INTO document_replies (document_id, sender_id, content, create_date)
             VALUES (%s, %s, %s, NOW())"""
    db.execute_update(sql, (doc_id, sender_id, content))

    sql = "UPDATE documents SET status='replied' WHERE id = %s"
    db.execute_update(sql, (doc_id,))

    return {
        "code": 200,
        "message": "回复成功"
    }


@router.get("/my-documents")
def get_my_documents(user_id: int, doc_type: Optional[str] = None):
    """
    获取我的公文（发出的/收到的）
    """
    sql = """SELECT d.*, o.name as org_name
             FROM documents d
             LEFT JOIN organizations o ON d.sender_org_id = o.id
             WHERE d.sender_id = %s"""
    params = [user_id]

    if doc_type:
        sql += " AND d.doc_type = %s"
        params.append(doc_type)

    sql += " ORDER BY d.create_date DESC"

    docs = db.execute_query(sql, tuple(params))

    return {
        "code": 200,
        "data": docs,
        "total": len(docs)
    }


@router.get("/received")
def get_received_documents(user_id: int, is_read: Optional[bool] = None):
    """
    获取收到的公文
    """
    # 首先获取用户所属组织
    from models.user import User
    user = User.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    org_id = user.get('organization_id')
    if not org_id:
        raise HTTPException(status_code=400, detail="用户未分配组织")

    sql = """SELECT d.*, o.name as org_name, dr.read_time
             FROM documents d
             LEFT JOIN organizations o ON d.sender_org_id = o.id
             LEFT JOIN document_receipts dr ON d.id = dr.document_id AND dr.receiver_org_id = %s
             WHERE d.status = 'published'
             AND dr.document_id IS NOT NULL"""
    params = [org_id]

    if is_read is not None:
        if is_read:
            sql += " AND dr.read_time IS NOT NULL"
        else:
            sql += " AND dr.read_time IS NULL"

    sql += " ORDER BY d.create_date DESC"

    docs = db.execute_query(sql, (org_id,))

    return {
        "code": 200,
        "data": docs,
        "total": len(docs)
    }