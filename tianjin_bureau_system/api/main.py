# -*- coding: utf-8 -*-
"""
API 入口文件
使用方法: uvicorn api.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api import auth, users, assets, budgets, documents, messages, organizations
from api.response import APIResponse

app = FastAPI(
    title="天津市市政工程局管理系统 API",
    description="提供业务系统的 REST API 接口",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc)
        }
    )

# 注册路由
app.include_router(auth.router, tags=["认证"])
app.include_router(users.router, tags=["用户管理"])
app.include_router(organizations.router, tags=["组织管理"])
app.include_router(assets.router, tags=["资产管理"])
app.include_router(budgets.router, tags=["预算管理"])
app.include_router(documents.router, tags=["公文管理"])
app.include_router(messages.router, tags=["消息管理"])


@app.get("/")
def root():
    return {
        "message": "天津市市政工程局管理系统 API",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "统一的响应格式",
            "分页支持",
            "三级管理数据隔离",
            "权限验证",
            "错误处理"
        ]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}