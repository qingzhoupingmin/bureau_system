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


class ApprovePasswordRequest(BaseModel):
    hr_id: int
    comment: str = ""


@router.post("/password/approve")
def approve_password_change(user_id: int, req: ApprovePasswordRequest):
    """
    劳动人事处审批密码修改申请

    Args:
        user_id: 申请修改密码的用户ID
        req: 审批信息
    """
    from db.connection import db

    # 验证审批人权限（必须是劳动人事处）
    from models.user import User
    hr_user = User.get_by_id(req.hr_id)
    if not hr_user or hr_user['role'] != 'hr_staff':
        raise HTTPException(status_code=403, detail="只有劳动人事处可以审批密码修改")

    # 查找待审批的密码修改申请
    sql = "SELECT * FROM password_change_requests WHERE user_id = %s AND status = 'pending'"
    result = db.execute_query(sql, (user_id,))

    if not result:
        raise HTTPException(status_code=404, detail="未找到待审批的密码修改申请")

    # 更新申请状态
    sql = """UPDATE password_change_requests
             SET status = 'approved', hr_id = %s, approve_time = NOW(), comment = %s
             WHERE user_id = %s AND status = 'pending'"""
    db.execute_update(sql, (req.hr_id, req.comment, user_id))

    # 更新用户密码
    request_data = result[0]
    User.update_password(user_id, request_data['new_password'])

    return {
        "code": 200,
        "message": "密码修改审批通过"
    }


class RequestPasswordChange(BaseModel):
    user_id: int
    old_password: str
    new_password: str
    reason: str = ""


@router.post("/password/request")
def request_password_change(req: RequestPasswordChange):
    """
    用户申请修改密码（需要劳动人事处审批）

    Args:
        req: 密码修改申请信息
    """
    from models.user import User
    from db.connection import db

    # 验证用户
    user = User.get_by_id(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 验证旧密码
    import hashlib
    old_hash = hashlib.sha256(req.old_password.encode()).hexdigest()
    if user['password'] != old_hash:
        raise HTTPException(status_code=400, detail="原密码错误")

    # 创建密码修改申请
    sql = """INSERT INTO password_change_requests
             (user_id, old_password, new_password, reason, status, request_time)
             VALUES (%s, %s, %s, %s, 'pending', NOW())"""
    db.execute_update(sql, (req.user_id, old_hash, req.new_password, req.reason))

    return {
        "code": 200,
        "message": "密码修改申请已提交，等待劳动人事处审批"
    }