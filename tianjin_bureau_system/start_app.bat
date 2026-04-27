@echo off
chcp 65001 >nul
echo ========================================
echo   天津市市政工程局综合管理系统
echo   桌面应用启动程序
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
pip show pymyql >nul 2>&1
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

echo [3/3] 启动桌面应用...
echo.
echo ========================================
echo   系统信息
echo ========================================
echo   应用类型: Tkinter桌面应用
echo   数据库: MySQL (localhost:3306)
echo   用户名: admin
echo   密码: admin123
echo ========================================
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败
    pause
) else (
    echo.
    echo ✅ 系统已正常退出
)

pause