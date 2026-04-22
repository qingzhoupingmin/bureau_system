@echo off
chcp 65001 > nul
echo.
echo ========================================
echo 打包前测试 - 天津市市政工程局综合管理系统
echo ========================================
echo.

python test_before_build.py

if errorlevel 1 (
    echo.
    echo 测试过程中出现错误，建议检查后重新测试
)

pause