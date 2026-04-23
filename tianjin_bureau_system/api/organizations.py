# -*- coding: utf-8 -*-
"""
组织管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.connection import db

router = APIRouter(prefix="/api/organizations", tags=["组织管理"])


class CreateOrgRequest(BaseModel):
    name: str
    code: str
    parent_id: Optional[int] = None
    description: str = ""


class UpdateOrgRequest(BaseModel):
    name: str
    description: str


@router.get("")
def get_organizations(parent_id: Optional[int] = None):
    """
    获取组织列表
    """
    if parent_id is not None:
        sql = "SELECT * FROM organizations WHERE parent_id = %s ORDER BY id"
        orgs = db.execute_query(sql, (parent_id,))
    else:
        sql = "SELECT * FROM organizations ORDER BY id"
        orgs = db.execute_query(sql)

    return {
        "code": 200,
        "data": orgs,
        "total": len(orgs)
    }


@router.get("/{org_id}")
def get_organization(org_id: int):
    """
    获取组织详情
    """
    sql = "SELECT * FROM organizations WHERE id = %s"
    orgs = db.execute_query(sql, (org_id,))

    if not orgs:
        raise HTTPException(status_code=404, detail="组织不存在")

    return {
        "code": 200,
        "data": orgs[0]
    }


@router.post("")
def create_organization(req: CreateOrgRequest):
    """
    创建组织
    """
    sql = """INSERT INTO organizations (name, code, parent_id, description)
             VALUES (%s, %s, %s, %s)"""
    org_id = db.execute_update(sql, (req.name, req.code, req.parent_id, req.description))

    return {
        "code": 200,
        "message": "组织创建成功",
        "data": {"org_id": org_id}
    }


@router.put("/{org_id}")
def update_organization(org_id: int, req: UpdateOrgRequest):
    """
    更新组织
    """
    sql = "UPDATE organizations SET name = %s, description = %s WHERE id = %s"
    db.execute_update(sql, (req.name, req.description, org_id))

    return {
        "code": 200,
        "message": "组织更新成功"
    }


@router.delete("/{org_id}")
def delete_organization(org_id: int):
    """
    删除组织
    """
    # 检查是否有子组织
    sql = "SELECT COUNT(*) as cnt FROM organizations WHERE parent_id = %s"
    result = db.execute_query(sql, (org_id,))
    if result and result[0].get('cnt', 0) > 0:
        raise HTTPException(status_code=400, detail="请先删除子组织")

    sql = "DELETE FROM organizations WHERE id = %s"
    db.execute_update(sql, (org_id,))

    return {
        "code": 200,
        "message": "组织删除成功"
    }


@router.get("/{org_id}/users")
def get_org_users(org_id: int):
    """
    获取组织下的用户
    """
    sql = "SELECT * FROM users WHERE organization_id = %s"
    users = db.execute_query(sql, (org_id,))

    return {
        "code": 200,
        "data": users,
        "total": len(users)
    }