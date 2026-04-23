# -*- coding: utf-8 -*-
"""
公文管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.connection import db

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
    status: Optional[str] = None,
    doc_type: Optional[str] = None,
    org_id: Optional[int] = None
):
    """
    获取公文列表
    """
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

    sql += " ORDER BY d.create_date DESC"

    docs = db.execute_query(sql, tuple(params) if params else None)

    return {
        "code": 200,
        "data": docs,
        "total": len(docs)
    }


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