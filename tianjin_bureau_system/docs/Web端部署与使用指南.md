# 天津市市政工程局管理系统 - Web端部署与使用指南

## 概述

本系统已改造为 **Web端内部管理系统**，基于：
- **前端**: React + Vite（`municipal-system/` 目录）
- **后端**: FastAPI Python（`api/` 目录）
- **数据库**: SQLite（兼容现有业务数据）

访问方式：**浏览器直接访问**，无需安装任何桌面客户端。

---

## 快速启动

### 方法一：一键启动（推荐）

```bash
# 1. 构建前端（首次或前端代码修改后执行）
cd municipal-system
npm install
npm run build

# 2. 启动后端服务
cd ..
python api_start.py --port 8000

# 3. 打开浏览器访问
# http://localhost:8000/
```

### 方法二：双击批处理文件

1. 双击 `build_frontend.bat` - 构建前端（首次执行）
2. 双击 `start_api.bat` - 启动服务
3. 浏览器访问 http://localhost:8000/

---

## 开发模式

开发时前后端分离，支持热更新：

```bash
# 终端1：启动后端API
cd tianjin_bureau_system
python api_start.py --port 8000

# 终端2：启动前端开发服务器
cd tianjin_bureau_system/municipal-system
npm run dev
```

前端开发服务器运行在 http://localhost:8080/ ，会自动代理API请求到后端8000端口。

---

## 生产部署

```bash
# 1. 构建前端
cd municipal-system
npm install
npm run build

# 2. 启动后端（自动提供前端页面）
cd ..
python api_start.py --host 0.0.0.0 --port 80 --no-reload --workers 4
```

---

## 系统功能

| 功能模块 | 描述 | 路径 |
|---------|------|------|
| 仪表盘 | 系统概览、统计数据 | `/` |
| 资产管理 | 资产增删改查、审批 | `/assets` |
| 预算管理 | 预算编制、执行监控 | `/budgets` |
| 组织管理 | 组织机构、部门管理 | `/organizations` |
| 公文管理 | 公文流转、审批 | `/documents` |
| 消息管理 | 站内消息通知 | `/messages` |

---

## 架构说明

```
用户浏览器 → FastAPI (端口8000)
                  ├── /api/* → API路由（业务逻辑）
                  ├── /assets/* → 静态资源（JS/CSS/图片）
                  └── /* → SPA前端入口（React应用）
```

- 前端采用 HashRouter，所有路由兼容服务器端直出
- 构建后的前端文件位于 `municipal-system/dist/`
- API 请求通过同源方式（相对路径）访问，无需配置跨域