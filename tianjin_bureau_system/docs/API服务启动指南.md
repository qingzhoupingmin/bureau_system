# API服务启动指南

## 快速启动（3步走）

### 第1步：安装依赖
```bash
cd d:\测试开发项目\电商系统企业级+自动化框架\tianjin_bureau_system
pip install -r requirements.txt
```

### 第2步：启动MySQL数据库
```bash
# 确保MySQL服务已启动
# 数据库配置信息：
#   主机: localhost
#   端口: 3306
#   用户: root
#   密码: Oppor831t
#   数据库: tianjin_bureau
```

### 第3步：启动API服务
```bash
# 开发模式（推荐测试用）
uvicorn api.main:app --reload --port 8000

# 生产模式
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## 详细启动步骤

### 1. 环境准备

#### 1.1 Python版本要求
- Python 3.8 或更高版本

#### 1.2 MySQL版本要求
- MySQL 5.7 或更高版本

#### 1.3 检查Python版本
```bash
python --version
```

#### 1.4 检查MySQL状态
```bash
# Windows
net start MySQL80

# 或者在服务管理器中启动MySQL服务
```

---

### 2. 安装依赖

#### 2.1 进入项目目录
```bash
cd d:\测试开发项目\电商系统企业级+自动化框架\tianjin_bureau_system
```

#### 2.2 安装requirements.txt中的依赖
```bash
pip install -r requirements.txt
```

#### 2.3 如果安装失败，尝试逐个安装
```bash
pip install pymysql>=1.1.0
pip install fastapi>=0.100.0
pip install uvicorn>=0.23.0
pip install pydantic>=2.0.0
pip install requests>=2.28.0
pip install pyinstaller>=5.0.0
```

---

### 3. 数据库配置

#### 3.1 检查数据库配置文件
配置文件位置：`tianjin_bureau_system/config.py`

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Oppor831t',
    'database': 'tianjin_bureau',
    'charset': 'utf8mb4'
}
```

#### 3.2 创建数据库（如果不存在）
```sql
CREATE DATABASE IF NOT EXISTS tianjin_bureau DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 3.3 初始化数据库表结构
```bash
python db/init_db.py
```

或使用GUI工具：
```bash
python init_db_gui.py
```

#### 3.4 验证数据库连接
```bash
python -c "from db.connection import db; print(db.execute_query('SELECT 1 as test'))"
```

---

### 4. 启动API服务

#### 4.1 开发模式启动（推荐测试用）
```bash
uvicorn api.main:app --reload --port 8000
```

**特点：**
- 自动重载：代码修改后自动重启
- 详细日志：显示详细的请求日志
- 端口：8000

#### 4.2 生产模式启动
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**特点：**
- 多进程：使用4个工作进程
- 外网访问：绑定到0.0.0.0
- 高性能：适合生产环境

#### 4.3 使用指定配置文件启动
```bash
uvicorn api.main:app --reload --port 8000 --log-level debug
```

---

### 5. 验证API服务

#### 5.1 检查服务是否启动成功
```bash
# 命令行检查
curl http://localhost:8000/

# 或使用浏览器访问
http://localhost:8000/
```

#### 5.2 访问Swagger文档
```
http://localhost:8000/docs
```

#### 5.3 访问ReDoc文档
```
http://localhost:8000/redoc
```

#### 5.4 健康检查
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy"
}
```

---

### 6. 测试API接口

#### 6.1 测试登录接口
```bash
curl -X POST http://localhost:8000/api/auth/login \n  -H "Content-Type: application/json" \n  -d "{"username":"admin","password":"admin123"}"
```

预期响应：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "username": "admin",
    "full_name": "系统管理员",
    "role": "system_admin",
    "organization_id": null
  }
}
```

#### 6.2 测试获取用户列表（带分页）
```bash
curl "http://localhost:8000/api/users?page=1&page_size=10"
```

#### 6.3 使用Python requests测试
```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
print(response.json())

# 获取用户列表
response = requests.get("http://localhost:8000/api/users?page=1&page_size=10")
print(response.json())
```

---

## 常见问题处理

### 问题1：端口被占用

**错误信息：**
```
uvicorn.error: [Errno 48] Address already in use
```

**解决方案：**
```bash
# Windows: 查找占用8000端口的进程
netstat -ano | findstr :8000

# 结束进程
taskkill /PID <进程ID> /F

# 或使用其他端口
uvicorn api.main:app --reload --port 8001
```

---

### 问题2：数据库连接失败

**错误信息：**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```

**解决方案：**
```bash
# 1. 检查MySQL服务是否启动
net start MySQL80

# 2. 检查MySQL是否监听3306端口
netstat -ano | findstr :3306

# 3. 检查数据库配置
# 编辑 config.py 中的 DB_CONFIG

# 4. 测试数据库连接
mysql -h localhost -u root -p
```

---

### 问题3：依赖安装失败

**错误信息：**
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**解决方案：**
```bash
# 1. 升级pip
python -m pip install --upgrade pip

# 2. 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 逐个安装依赖
pip install pymysql
pip install fastapi
pip install uvicorn
pip install pydantic
```

---

### 问题4：找不到模块

**错误信息：**
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案：**
```bash
# 1. 确认在正确的目录
cd d:\测试开发项目\电商系统企业级+自动化框架\tianjin_bureau_system

# 2. 设置Python路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Windows PowerShell:
$env:PYTHONPATH += ";$(pwd)"

# 3. 重新安装依赖
pip install -r requirements.txt
```

---

### 问题5：CORS错误

**错误信息：**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解决方案：**
已在 `api/main.py` 中配置了CORS，如果仍有问题：
```python
# 编辑 api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 自动化测试集成

### 1. 使用pytest测试API

创建测试文件 `tests/api/test_auth_api.py`:

```python
import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_login_success():
    """测试登录成功"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data

def test_login_fail():
    """测试登录失败"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401
```

运行测试：
```bash
cd tests
pytest api/test_auth_api.py -v
```

### 2. 使用pytest + requests进行API测试

安装测试依赖：
```bash
pip install pytest pytest-cov requests
```

运行所有API测试：
```bash
pytest tests/api/ -v --cov=tianjin_bureau_system.api
```

---

## 性能优化建议

### 1. 使用Gunicorn启动（生产环境）
```bash
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 启用日志
```bash
uvicorn api.main:app --reload --port 8000 --log-level info
```

### 3. 使用环境变量配置
```bash
# 创建 .env 文件
export DB_PASSWORD="your_password"
export API_PORT=8000

# 启动时读取环境变量
uvicorn api.main:app --reload --port $API_PORT
```

---

## 停止API服务

### 1. 在命令行中停止
```bash
# 按 Ctrl+C 停止服务
```

### 2. 强制停止（Windows）
```bash
# 查找进程
netstat -ano | findstr :8000

# 结束进程
taskkill /PID <进程ID> /F
```

---

## 启动脚本

### Windows批处理脚本 (start_api.bat)

```batch
@echo off
echo Starting API Server...
cd /d "d:\测试开发项目\电商系统企业级+自动化框架\tianjin_bureau_system"
uvicorn api.main:app --reload --port 8000
pause
```

### PowerShell脚本 (start_api.ps1)

```powershell
Write-Host "Starting API Server..."
Set-Location "d:\测试开发项目\电商系统企业级+自动化框架\tianjin_bureau_system"
uvicorn api.main:app --reload --port 8000
```

使用方法：
```bash
# 双击 start_api.bat 或
start_api.bat
```

---

## Docker部署（可选）

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 启动Docker容器
```bash
docker build -t tianjin-bureau-api .
docker run -p 8000:8000 tianjin-bureau-api
```

---

## 总结

### 快速启动命令
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动MySQL服务
net start MySQL80

# 3. 启动API服务
uvicorn api.main:app --reload --port 8000
```

### 验证服务
```bash
# 访问根路径
curl http://localhost:8000/

# 访问API文档
http://localhost:8000/docs

# 健康检查
curl http://localhost:8000/health
```

### 测试API
```bash
# 测试登录
curl -X POST http://localhost:8000/api/auth/login \n  -H "Content-Type: application/json" \n  -d "{"username":"admin","password":"admin123"}"
```

按照以上步骤，你就可以成功启动API服务，并进行自动化测试了！