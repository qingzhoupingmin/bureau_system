# -*- coding: utf-8 -*-
"""
组织管理接口
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from db.connection import db
from api.pagination import PaginationParams, PaginatedResponse, paginate_query, count_query

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
def get_organizations(
    request: Request,
    parent_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取组织列表（支持分页）
    """
    pagination = PaginationParams(page=page, page_size=page_size)

    if parent_id is not None:
        sql = "SELECT * FROM organizations WHERE parent_id = %s ORDER BY id"
        params = (parent_id,)
    else:
        sql = "SELECT * FROM organizations ORDER BY id"
        params = None

    # 获取总数
    count_sql = count_query(sql)
    total_result = db.execute_query(count_sql, params)
    total = total_result[0].get('total', 0) if total_result else 0

    # 添加分页
    paginated_sql, paginated_params = paginate_query(sql, params if params else (), pagination)

    orgs = db.execute_query(paginated_sql, paginated_params)

    return PaginatedResponse.create(orgs, total, pagination).dict()


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


@router.get("/tree")
def get_organization_tree():
    """
    获取组织架构树（三级管理）
    """
    # 递归构建树形结构
    def build_tree(parent_id=None):
        sql = "SELECT * FROM organizations WHERE parent_id IS NULL" if parent_id is None else f"SELECT * FROM organizations WHERE parent_id = {parent_id}"
        if parent_id is not None:
            sql = "SELECT * FROM organizations WHERE parent_id = %s"
            orgs = db.execute_query(sql, (parent_id,))
        else:
            sql = "SELECT * FROM organizations WHERE parent_id IS NULL"
            orgs = db.execute_query(sql)

        for org in orgs:
            org['children'] = build_tree(org['id'])

        return orgs

    tree = build_tree()

    return {
        "code": 200,
        "data": tree
    }


@router.get("/departments")
def get_departments():
    """
    获取机关处室列表（第一级）
    """
    sql = "SELECT * FROM organizations WHERE type = 'department' ORDER BY id"
    orgs = db.execute_query(sql)

    return {
        "code": 200,
        "data": orgs,
        "total": len(orgs)
    }


@router.get("/units")
def get_units():
    """
    获取中层单位列表（第二级）
    """
    sql = "SELECT * FROM organizations WHERE type = 'unit' ORDER BY id"
    orgs = db.execute_query(sql)

    return {
        "code": 200,
        "data": orgs,
        "total": len(orgs)
    }


@router.get("/sub-units/{parent_id}")
def get_sub_units(parent_id: int):
    """
    获取基层单位列表（第三级）
    """
    sql = "SELECT * FROM organizations WHERE type = 'sub_unit' AND parent_id = %s ORDER BY id"
    orgs = db.execute_query(sql, (parent_id,))

    return {
        "code": 200,
        "data": orgs,
        "total": len(orgs)
    }


@router.get("/{org_id}/assets")
def get_org_assets(org_id: int):
    """
    获取组织的资产统计
    """
    sql = """SELECT COUNT(*) as count, SUM(price) as total_value
             FROM assets WHERE organization_id = %s"""
    result = db.execute_query(sql, (org_id,))

    stats = {
        'count': result[0]['count'] if result else 0,
        'total_value': result[0]['total_value'] if result else 0
    }

    return {
        "code": 200,
        "data": stats
    }


@router.get("/path/{org_id}")
def get_organization_path(org_id: int):
    """
    获取组织路径（从中层到基层）
    """
    sql = "SELECT * FROM organizations WHERE id = %s"
    org = db.execute_query(sql, (org_id,))

    if not org:
        raise HTTPException(status_code=404, detail="组织不存在")

    path = [org[0]]

    # 递归查找父组织
    current = org[0]
    while current.get('parent_id'):
        sql = "SELECT * FROM organizations WHERE id = %s"
        parent = db.execute_query(sql, (current['parent_id'],))
        if parent:
            path.append(parent[0])
            current = parent[0]
        else:
            break

    # 反转路径，从顶层开始
    path.reverse()

    return {
        "code": 200,
        "data": path
    }