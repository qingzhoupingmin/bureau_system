# -*- coding: utf-8 -*-
"""
资产管理接口
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from services.asset_service import AssetService
from db.connection import db
from api.pagination import PaginationParams, PaginatedResponse, paginate_query, count_query

router = APIRouter(prefix="/api/assets", tags=["资产管理"])


class CreateAssetRequest(BaseModel):
    name: str
    category: str
    model: Optional[str] = ""
    serial_number: Optional[str] = ""
    purchase_date: Optional[str] = None
    price: float = 0
    location: str = ""
    status: str = "normal"
    organization_id: Optional[int] = None
    is_public: int = 0
    caretaker: str = ""


class UpdateAssetRequest(BaseModel):
    name: str
    category: str
    model: Optional[str] = ""
    serial_number: Optional[str] = ""
    purchase_date: Optional[str] = None
    price: float = 0
    location: str = ""
    status: str = "normal"
    organization_id: Optional[int] = None
    is_public: int = 0
    caretaker: str = ""


class ApplyAssetRequest(BaseModel):
    applicant_id: int
    applicant_org_id: int
    reason: str


@router.get("")
def get_assets(
    request: Request,
    category: Optional[str] = None,
    status: Optional[str] = None,
    org_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取资产列表（支持分页）
    """
    pagination = PaginationParams(page=page, page_size=page_size)

    # 构建SQL
    sql = "SELECT * FROM assets WHERE 1=1"
    params = []

    if category:
        sql += " AND category = %s"
        params.append(category)
    if status:
        sql += " AND status = %s"
        params.append(status)
    if org_id:
        sql += " AND organization_id = %s"
        params.append(org_id)

    # 获取总数
    count_sql = count_query(sql)
    total_result = db.execute_query(count_sql, tuple(params) if params else None)
    total = total_result[0].get('total', 0) if total_result else 0

    # 添加分页
    sql += " ORDER BY id DESC"
    paginated_sql, paginated_params = paginate_query(sql, tuple(params) if params else (), pagination)

    assets = db.execute_query(paginated_sql, paginated_params)

    return PaginatedResponse.create(assets, total, pagination).dict()


@router.get("/statistics")
def get_statistics():
    """
    获取资产统计
    """
    stats = AssetService.get_statistics()
    return {
        "code": 200,
        "data": stats
    }


@router.get("/{asset_id}")
def get_asset(asset_id: int):
    """
    获取资产详情
    """
    asset = AssetService.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    return {
        "code": 200,
        "data": asset
    }


@router.post("")
def create_asset(req: CreateAssetRequest):
    """
    创建资产
    """
    data = req.dict()
    asset_id = AssetService.create_asset(data)

    return {
        "code": 200,
        "message": "资产创建成功",
        "data": {"asset_id": asset_id}
    }


@router.put("/{asset_id}")
def update_asset(asset_id: int, req: UpdateAssetRequest):
    """
    更新资产
    """
    asset = AssetService.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    data = req.dict()
    AssetService.update_asset(asset_id, data)

    return {
        "code": 200,
        "message": "资产更新成功"
    }


@router.delete("/{asset_id}")
def delete_asset(asset_id: int):
    """
    删除资产
    """
    asset = AssetService.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    AssetService.delete_asset(asset_id)

    return {
        "code": 200,
        "message": "资产删除成功"
    }


@router.post("/{asset_id}/apply")
def apply_asset(asset_id: int, req: ApplyAssetRequest):
    """
    申请使用资产
    """
    asset = AssetService.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    AssetService.apply_for_asset(
        asset_id, req.applicant_id, req.applicant_org_id, req.reason
    )

    return {
        "code": 200,
        "message": "申请已提交"
    }


@router.get("/applications/list")
def get_applications(status: Optional[str] = None, applicant_id: Optional[int] = None):
    """
    获取资产申请列表
    """
    filters = {}
    if status:
        filters['status'] = status
    if applicant_id:
        filters['applicant_id'] = applicant_id

    applications = AssetService.get_applications(filters)

    return {
        "code": 200,
        "data": applications,
        "total": len(applications)
    }


@router.get("/applications")
def get_applications_paginated(
    status: Optional[str] = None,
    applicant_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取资产申请列表（支持分页）
    """
    pagination = PaginationParams(page=page, page_size=page_size)

    sql = """SELECT a.*, ast.name as asset_name, u.full_name as applicant_name, o.name as org_name
             FROM asset_applications a
             LEFT JOIN assets ast ON a.asset_id = ast.id
             LEFT JOIN users u ON a.applicant_id = u.id
             LEFT JOIN organizations o ON a.applicant_org_id = o.id
             WHERE 1=1"""
    params = []

    if status:
        sql += " AND a.status = %s"
        params.append(status)
    if applicant_id:
        sql += " AND a.applicant_id = %s"
        params.append(applicant_id)

    # 获取总数
    count_sql = count_query(sql)
    total_result = db.execute_query(count_sql, tuple(params) if params else None)
    total = total_result[0].get('total', 0) if total_result else 0

    # 添加分页
    sql += " ORDER BY a.apply_date DESC"
    paginated_sql, paginated_params = paginate_query(sql, tuple(params) if params else (), pagination)

    applications = db.execute_query(paginated_sql, paginated_params)

    return PaginatedResponse.create(applications, total, pagination).dict()


@router.get("/my-applications")
def get_my_applications(applicant_id: int, status: Optional[str] = None):
    """
    获取我的资产申请
    """
    filters = {'applicant_id': applicant_id}
    if status:
        filters['status'] = status

    applications = AssetService.get_applications(filters)

    return {
        "code": 200,
        "data": applications,
        "total": len(applications)
    }


@router.get("/org/{org_id}")
def get_assets_by_org(org_id: int):
    """
    按组织查看资产
    """
    sql = "SELECT * FROM assets WHERE organization_id = %s ORDER BY id DESC"
    assets = db.execute_query(sql, (org_id,))

    return {
        "code": 200,
        "data": assets,
        "total": len(assets)
    }


@router.get("/sub-orgs")
def get_sub_org_assets(user_org_id: int):
    """
    查看下级单位资产（中层单位专用）
    """
    # 获取该组织的所有下级组织
    sql = "SELECT id FROM organizations WHERE parent_id = %s"
    sub_orgs = db.execute_query(sql, (user_org_id,))

    if not sub_orgs:
        return {
            "code": 200,
            "data": [],
            "total": 0
        }

    # 获取所有下级组织的资产
    sub_org_ids = [org['id'] for org in sub_orgs]
    placeholders = ','.join(['%s'] * len(sub_org_ids))

    sql = f"SELECT * FROM assets WHERE organization_id IN ({placeholders}) ORDER BY id DESC"
    assets = db.execute_query(sql, tuple(sub_org_ids))

    return {
        "code": 200,
        "data": assets,
        "total": len(assets)
    }


@router.get("/level-stats")
def get_level_statistics():
    """
    分层级资产统计
    """
    stats = {}

    # 局机关资产统计
    sql = """SELECT COUNT(*) as count, SUM(price) as total_value
             FROM assets a
             LEFT JOIN organizations o ON a.organization_id = o.id
             WHERE o.type = 'department'"""
    dept_result = db.execute_query(sql)
    if dept_result:
        stats['department'] = {
            'count': dept_result[0]['count'],
            'total_value': dept_result[0]['total_value'] or 0
        }

    # 中层单位资产统计
    sql = """SELECT COUNT(*) as count, SUM(price) as total_value
             FROM assets a
             LEFT JOIN organizations o ON a.organization_id = o.id
             WHERE o.type = 'unit'"""
    unit_result = db.execute_query(sql)
    if unit_result:
        stats['unit'] = {
            'count': unit_result[0]['count'],
            'total_value': unit_result[0]['total_value'] or 0
        }

    # 基层单位资产统计
    sql = """SELECT COUNT(*) as count, SUM(price) as total_value
             FROM assets a
             LEFT JOIN organizations o ON a.organization_id = o.id
             WHERE o.type = 'sub_unit'"""
    sub_unit_result = db.execute_query(sql)
    if sub_unit_result:
        stats['sub_unit'] = {
            'count': sub_unit_result[0]['count'],
            'total_value': sub_unit_result[0]['total_value'] or 0
        }

    return {
        "code": 200,
        "data": stats
    }


@router.post("/applications/{app_id}/approve")
def approve_application(app_id: int, approver_id: int, comment: str = ""):
    """
    审批资产申请
    """
    AssetService.approve_application(app_id, approver_id, comment)

    return {
        "code": 200,
        "message": "审批通过"
    }


@router.post("/applications/{app_id}/reject")
def reject_application(app_id: int, approver_id: int, comment: str = ""):
    """
    拒绝资产申请
    """
    AssetService.reject_application(app_id, approver_id, comment)

    return {
        "code": 200,
        "message": "申请已拒绝"
    }