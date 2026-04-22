@echo off
chcp 65001 > nul
echo ========================================
echo 天津市市政工程局综合管理系统 - 打包工具
echo ========================================
echo.

echo 正在检查 Python 环境...
python --version
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在检查 PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [提示] 未安装 PyInstaller，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 开始打包...
echo ========================================
echo.

pyinstaller --clean --noconfirm main.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    echo 请查看上面的错误信息
) else (
    echo.
    echo ========================================
    echo ✓ 打包成功！
    echo ========================================
    echo.
    echo 可执行文件位置：
    echo dist\天津市市政工程局综合管理系统.exe
    echo.
    echo 可以将该文件复制到其他电脑上使用
)

echo.
pause