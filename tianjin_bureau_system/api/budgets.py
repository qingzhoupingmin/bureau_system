# -*- coding: utf-8 -*-
"""
预算管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.connection import db

router = APIRouter(prefix="/api/budgets", tags=["预算管理"])


class CreateBudgetRequest(BaseModel):
    organization_id: int
    year: int
    amount: float
    category: str
    purpose: str
    applicant_id: int


class ApproveBudgetRequest(BaseModel):
    approver_id: int
    comment: str = ""


@router.get("")
def get_budgets(
    year: Optional[int] = None,
    status: Optional[str] = None,
    org_id: Optional[int] = None
):
    """
    获取预算申请列表
    """
    sql = """SELECT b.*, o.name as org_name, u.full_name as applicant_name
             FROM budget_applications b
             LEFT JOIN organizations o ON b.organization_id = o.id
             LEFT JOIN users u ON b.applicant_id = u.id
             WHERE 1=1"""
    params = []

    if year:
        sql += " AND b.year = %s"
        params.append(year)
    if status:
        sql += " AND b.status = %s"
        params.append(status)
    if org_id:
        sql += " AND b.organization_id = %s"
        params.append(org_id)

    sql += " ORDER BY b.apply_date DESC"

    budgets = db.execute_query(sql, tuple(params) if params else None)

    return {
        "code": 200,
        "data": budgets,
        "total": len(budgets)
    }


@router.get("/statistics")
def get_statistics():
    """
    获取预算统计
    """
    sql = """SELECT status, COUNT(*) as count, SUM(amount) as total
             FROM budget_applications GROUP BY status"""
    result = db.execute_query(sql)

    stats = {"total_apply": 0, "total_approved": 0, "total_rejected": 0, "total_pending": 0}
    for r in result:
        status = r.get('status')
        count = r.get('count', 0)
        total = r.get('total', 0) or 0
        stats['total_apply'] += count
        if status == 'approved':
            stats['total_approved'] = total
        elif status == 'rejected':
            stats['total_rejected'] = total
        elif status == 'pending':
            stats['total_pending'] = total

    return {
        "code": 200,
        "data": stats
    }


@router.get("/{budget_id}")
def get_budget(budget_id: int):
    """
    获取预算详情
    """
    sql = """SELECT b.*, o.name as org_name, u.full_name as applicant_name
             FROM budget_applications b
             LEFT JOIN organizations o ON b.organization_id = o.id
             LEFT JOIN users u ON b.applicant_id = u.id
             WHERE b.id = %s"""
    result = db.execute_query(sql, (budget_id,))

    if not result:
        raise HTTPException(status_code=404, detail="预算申请不存在")

    return {
        "code": 200,
        "data": result[0]
    }


@router.post("")
def create_budget(req: CreateBudgetRequest):
    """
    创建预算申请
    """
    sql = """INSERT INTO budget_applications
             (organization_id, year, amount, category, purpose, applicant_id, status, apply_date)
             VALUES (%s, %s, %s, %s, %s, %s, 'pending', NOW())"""
    budget_id = db.execute_update(sql, (
        req.organization_id, req.year, req.amount,
        req.category, req.purpose, req.applicant_id
    ))

    return {
        "code": 200,
        "message": "预算申请已提交",
        "data": {"budget_id": budget_id}
    }


@router.post("/{budget_id}/approve")
def approve_budget(budget_id: int, req: ApproveBudgetRequest):
    """
    审批预算
    """
    sql = "SELECT * FROM budget_applications WHERE id = %s"
    result = db.execute_query(sql, (budget_id,))
    if not result:
        raise HTTPException(status_code=404, detail="预算申请不存在")

    sql = """UPDATE budget_applications
             SET status='approved', approver_id=%s, approve_date=NOW(), approve_comment=%s
             WHERE id=%s"""
    db.execute_update(sql, (req.approver_id, req.comment, budget_id))

    return {
        "code": 200,
        "message": "预算审批通过"
    }


@router.post("/{budget_id}/reject")
def reject_budget(budget_id: int, req: ApproveBudgetRequest):
    """
    拒绝预算
    """
    sql = "SELECT * FROM budget_applications WHERE id = %s"
    result = db.execute_query(sql, (budget_id,))
    if not result:
        raise HTTPException(status_code=404, detail="预算申请不存在")

    sql = """UPDATE budget_applications
             SET status='rejected', approver_id=%s, approve_date=NOW(), approve_comment=%s
             WHERE id=%s"""
    db.execute_update(sql, (req.approver_id, req.comment, budget_id))

    return {
        "code": 200,
        "message": "预算申请已拒绝"
    }