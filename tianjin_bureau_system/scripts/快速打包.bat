@echo off
chcp 65001 > nul
echo ========================================
echo 天津市市政工程局综合管理系统 - 快速打包
echo ========================================
echo.

echo 正在检查 Python 环境...
python --version

echo.
echo 正在打包为文件夹版本（推荐）...
echo.

pyinstaller --clean --noconfirm --onedir --windowed ^
    --name "天津市市政工程局综合管理系统" ^
    --icon="assets/images/icon.ico" ^
    --hidden-import="pymysql" ^
    --hidden-import="tkinter" ^
    --hidden-import="tkinter.ttk" ^
    --hidden-import="tkinter.messagebox" ^
    --hidden-import="tkinter.filedialog" ^
    main.py

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
    echo dist\天津市市政工程局综合管理系统\天津市市政工程局综合管理系统.exe
    echo.
    echo 需要将整个文件夹复制到目标电脑
)

echo.
pause