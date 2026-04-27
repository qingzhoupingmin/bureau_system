# -*- coding: utf-8 -*-
"""
API 入口文件
使用方法: uvicorn api.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from api import auth, users, assets, budgets, documents, messages, organizations
from api.response import APIResponse
import os

# ==========================================
# 前端静态文件路径（构建后的 Vite 输出）
# ==========================================
FRONTEND_DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "municipal-system", "dist")
FRONTEND_INDEX_HTML = os.path.join(FRONTEND_DIST_DIR, "index.html")
STATIC_ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, "assets")

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

# 挂载静态资源（如果前端已构建）
if os.path.exists(STATIC_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=STATIC_ASSETS_DIR), name="frontend_assets")


@app.get("/")
async def root():
    """根路径 - 如果前端已构建则返回前端页面，否则返回API信息"""
    if os.path.exists(FRONTEND_INDEX_HTML):
        return FileResponse(FRONTEND_INDEX_HTML)
    
    return {
        "message": "天津市市政工程局管理系统 API",
        "version": "2.0.0",
        "docs": "/docs",
        "note": "前端页面未构建，访问 http://localhost:8080 (npm run dev) 体验Web界面",
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


# SPA 兜底路由 - 所有非 API 路径都返回前端页面
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # API路径跳过（让FastAPI自己处理）
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi") or full_path == "health":
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    # 如果前端构建文件存在，返回前端页面
    if os.path.exists(FRONTEND_INDEX_HTML):
        return FileResponse(FRONTEND_INDEX_HTML)
    
    return JSONResponse(status_code=404, content={"detail": "前端页面未构建，请先运行 npm run build"})