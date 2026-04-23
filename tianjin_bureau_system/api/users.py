# -*- coding: utf-8 -*-
"""
用户管理接口
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from models.user import User
from api.pagination import PaginationParams, PaginatedResponse, paginate_query

router = APIRouter(prefix="/api/users", tags=["用户管理"])


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str
    organization_id: Optional[int] = None
    full_name: str
    position: Optional[str] = ""


class UpdateUserRequest(BaseModel):
    full_name: str
    position: str
    role: str


@router.get("")
def get_users(
    request: Request,
    role: Optional[str] = None,
    org_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取用户列表（支持分页）
    """
    pagination = PaginationParams(page=page, page_size=page_size)

    # 构建基础SQL
    sql = "SELECT * FROM users WHERE 1=1"
    params = []

    # 根据角色过滤
    if role:
        sql += " AND role = %s"
        params.append(role)

    # 根据组织过滤
    if org_id:
        sql += " AND organization_id = %s"
        params.append(org_id)

    # 获取总数
    from api.pagination import count_query
    count_sql = count_query(sql)
    from db.connection import db
    total_result = db.execute_query(count_sql, tuple(params) if params else None)
    total = total_result[0].get('total', 0) if total_result else 0

    # 添加分页
    sql += " ORDER BY id DESC"
    paginated_sql, paginated_params = paginate_query(sql, tuple(params) if params else (), pagination)

    users = db.execute_query(paginated_sql, paginated_params)

    return PaginatedResponse.create(users, total, pagination).dict()


@router.get("/{user_id}")
def get_user(user_id: int):
    """
    获取用户详情
    """
    user = User.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "code": 200,
        "data": user
    }


@router.post("")
def create_user(req: CreateUserRequest):
    """
    创建用户
    """
    # 检查用户名是否已存在
    existing = User.get_by_username(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user_id = User.create_user(
        req.username, req.password, req.role,
        req.organization_id, req.full_name, req.position
    )

    return {
        "code": 200,
        "message": "用户创建成功",
        "data": {"user_id": user_id}
    }


@router.put("/{user_id}")
def update_user(user_id: int, req: UpdateUserRequest):
    """
    更新用户
    """
    user = User.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    User.update_user(user_id, req.full_name, req.position, req.role)

    return {
        "code": 200,
        "message": "用户更新成功"
    }


@router.delete("/{user_id}")
def delete_user(user_id: int):
    """
    删除用户
    """
    user = User.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    User.delete_user(user_id)

    return {
        "code": 200,
        "message": "用户删除成功"
    }


@router.get("/by/org/{org_id}")
def get_users_by_org(org_id: int):
    """
    获取指定组织的用户列表
    """
    users = User.get_users_by_org(org_id)
    return {
        "code": 200,
        "data": users,
        "total": len(users)
    }


@router.put("/{user_id}/password")
def reset_password(user_id: int, new_password: str, admin_id: int):
    """
    管理员重置用户密码
    """
    # 验证管理员权限
    from models.user import User
    admin = User.get_by_id(admin_id)
    if not admin or admin['role'] != 'system_admin':
        raise HTTPException(status_code=403, detail="只有系统管理员可以重置密码")

    # 重置密码
    User.update_password(user_id, new_password)

    return {
        "code": 200,
        "message": "密码重置成功"
    }


@router.post("/register")
def register_user(username: str, password: str, full_name: str, organization_id: int):
    """
    用户注册（待审批）
    """
    # 检查用户名是否已存在
    existing = User.get_by_username(username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建用户（状态为pending）
    from db.connection import db
    sql = """INSERT INTO users
             (username, password, full_name, organization_id, role, status, create_time)
             VALUES (%s, %s, %s, %s, 'normal_user', 'pending', NOW())"""

    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user_id = db.execute_update(sql, (username, password_hash, full_name, organization_id))

    return {
        "code": 200,
        "message": "注册成功，等待审批",
        "data": {"user_id": user_id}
    }