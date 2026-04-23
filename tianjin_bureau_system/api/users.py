# -*- coding: utf-8 -*-
"""
用户管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models.user import User

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
def get_users(role: Optional[str] = None, org_id: Optional[int] = None):
    """
    获取用户列表
    """
    users = User.get_all_users()

    # 根据角色过滤
    if role:
        users = [u for u in users if u.get('role') == role]

    # 根据组织过滤
    if org_id:
        users = [u for u in users if u.get('organization_id') == org_id]

    return {
        "code": 200,
        "data": users,
        "total": len(users)
    }


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