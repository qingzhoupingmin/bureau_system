# -*- coding: utf-8 -*-
"""
资产管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.asset_service import AssetService
from db.connection import db

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
    category: Optional[str] = None,
    status: Optional[str] = None,
    org_id: Optional[int] = None
):
    """
    获取资产列表
    """
    filters = {}
    if category:
        filters['category'] = category
    if status:
        filters['status'] = status
    if org_id:
        filters['organization_id'] = org_id

    assets = AssetService.get_all_assets(filters)

    return {
        "code": 200,
        "data": assets,
        "total": len(assets)
    }


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


@router.get("/applications")
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