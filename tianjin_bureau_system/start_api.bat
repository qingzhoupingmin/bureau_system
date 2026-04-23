@echo off
chcp 65001 >nul
echo ========================================
echo   天津市市政工程局管理系统 API服务
echo ========================================
echo.

cd /d "%~dp0"
echo 当前目录: %CD%
echo.

echo [1/3] 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo [2/3] 检查依赖安装...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  依赖未安装，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo ✅ 依赖已安装
)
echo.

echo [3/3] 启动API服务...
echo.
echo ========================================
echo   API服务信息
echo ========================================
echo   地址: http://localhost:8000
echo   文档: http://localhost:8000/docs
echo   状态: http://localhost:8000/health
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

uvicorn api.main:app --reload --port 8000

pause