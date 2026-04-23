# -*- coding: utf-8 -*-
"""
API 中间件 - 权限验证、错误处理等
"""
from fastapi import Request, HTTPException, status
from functools import wraps
from typing import Optional, List
from services.auth_service import AuthService


def require_auth():
    """
    装饰器：要求用户认证
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从请求中获取用户ID（从Header或Query参数）
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(status_code=401, detail="未授权访问")

            # 从请求头获取用户ID
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                raise HTTPException(status_code=401, detail="未提供用户认证信息")

            try:
                user_id = int(user_id)
            except ValueError:
                raise HTTPException(status_code=401, detail="无效的用户ID")

            # 验证用户是否存在
            from models.user import User
            user = User.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=401, detail="用户不存在")

            # 将用户信息添加到请求上下文
            request.state.user = user

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(allowed_roles: List[str]):
    """
    装饰器：要求特定角色
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request or not hasattr(request.state, 'user'):
                raise HTTPException(status_code=401, detail="未授权访问")

            user = request.state.user
            if user['role'] not in allowed_roles:
                raise HTTPException(status_code=403, detail="权限不足")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_min_role(min_role: str):
    """
    装饰器：要求最低角色等级
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request or not hasattr(request.state, 'user'):
                raise HTTPException(status_code=401, detail="未授权访问")

            user = request.state.user
            has_permission = AuthService.check_permission(user, min_role)

            if not has_permission:
                raise HTTPException(status_code=403, detail="权限不足")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_organization_level():
    """
    装饰器：三级管理权限验证
    确保用户只能访问其组织层级范围内的数据
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request or not hasattr(request.state, 'user'):
                raise HTTPException(status_code=401, detail="未授权访问")

            user = request.state.user

            # 验证用户所属组织
            if not user.get('organization_id'):
                raise HTTPException(status_code=403, detail="用户未分配组织")

            # 从models.organization获取组织信息
            from models.organization import Organization
            org = Organization.get_by_id(user['organization_id'])
            if not org:
                raise HTTPException(status_code=403, detail "组织不存在")

            # 将组织信息添加到请求上下文
            request.state.organization = org

            return await func(*args, **kwargs)
        return wrapper
    return decorator