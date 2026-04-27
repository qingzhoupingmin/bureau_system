@echo off
chcp 65001 >nul
echo ========================================
echo   天津市市政工程局管理系统
echo   Web前端启动程序
echo ========================================
echo.

cd /d "%~dp0"
echo 当前目录: %CD%
echo.

echo [1/4] 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装或未添加到PATH
    echo.
    echo 请先安装Node.js: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js环境正常
echo.

echo [2/4] 检查npm环境...
npm --version
if %errorlevel% neq 0 (
    echo ❌ npm未安装
    pause
    exit /b 1
)
echo ✅ npm环境正常
echo.

echo [3/4] 检查依赖安装...
if not exist "node_modules" (
    echo ⚠️  依赖未安装，正在安装...
    echo 这可能需要几分钟时间，请耐心等待...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo ✅ 依赖已安装
)
echo.

echo [4/4] 启动Web前端开发服务器...
echo.
echo ========================================
echo   Web前端信息
echo ========================================
echo   地址: http://localhost:5173
echo   API: http://localhost:8000
echo   ========================================
echo.
echo ⚠️  请确保API服务已启动！
echo 启动API服务: python api_start.py
echo.
echo 按 Ctrl+C 停止服务
echo.

call npm run dev

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败，请检查错误信息
) else (
    echo.
    echo ✅ Web前端已正常关闭
)

pause