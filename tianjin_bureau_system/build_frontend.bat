@echo off
chcp 65001 >nul
echo ========================================
echo   构建前端页面
echo ========================================
echo.
cd /d "%~dp0"

echo [1/2] 安装前端依赖...
cd municipal-system
call npm install
if %errorlevel% neq 0 (
    echo ❌ npm install 失败
    pause
    exit /b 1
)
echo ✅ 前端依赖安装完成
echo.

echo [2/2] 构建前端...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ 前端构建失败
    pause
    exit /b 1
)
echo ✅ 前端构建成功！
echo.
echo 构建输出目录: municipal-system\dist\
echo.
echo 现在可以运行 start_api.bat 启动服务
echo.
pause