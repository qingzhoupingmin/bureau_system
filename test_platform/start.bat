@echo off
chcp 65001 >nul
echo.
echo ===============================================
echo   天津市市政工程局 - 自动化测试平台
echo ===============================================
echo.
echo 正在启动...
echo.
cd /d %~dp0..
python -m test_platform.app
pause