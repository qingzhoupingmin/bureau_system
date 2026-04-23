# -*- coding: utf-8 -*-
"""
认证接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str


@router.post("/login")
def login(req: LoginRequest):
    """
    用户登录
    """
    user = AuthService.login(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "user_id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "organization_id": user.get("organization_id")
        }
    }


@router.post("/logout")
def logout(user_id: int):
    """
    用户登出
    """
    try:
        AuthService.logout(user_id)
        return {"code": 200, "message": "登出成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/password")
def change_password(req: ChangePasswordRequest):
    """
    修改密码
    """
    success, message = AuthService.change_password(
        req.user_id, req.old_password, req.new_password
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"code": 200, "message": message}


@router.get("/permission")
def check_permission(user_id: int, required_role: str):
    """
    检查用户权限
    """
    from models.user import User
    user = User.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    has_permission = AuthService.check_permission(user, required_role)
    return {
        "code": 200,
        "data": {
            "has_permission": has_permission,
            "user_role": user["role"],
            "required_role": required_role
        }
    }