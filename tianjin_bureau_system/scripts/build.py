# -*- coding: utf-8 -*-
"""
天津市市政工程局综合管理系统 - 打包脚本
使用 PyInstaller 打包为 Windows 可执行文件
"""

import os
import sys
import subprocess

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller 安装成功！")
    except subprocess.CalledProcessError:
        print("PyInstaller 安装失败！请检查网络连接。")
        sys.exit(1)

def create_icon():
    """创建图标文件（可选）"""
    if not os.path.exists('assets/images'):
        os.makedirs('assets/images', exist_ok=True)
        print("创建 assets/images 目录")

    # 如果没有图标，提示用户
    icon_path = 'assets/images/icon.ico'
    if not os.path.exists(icon_path):
        print(f"提示：如果没有图标文件 {icon_path}，打包时不包含图标")
        print("可以放置 ico 格式图标文件到该位置")
    return icon_path

def build_executable():
    """打包可执行文件"""
    print("=" * 60)
    print("开始打包天津市市政工程局综合管理系统")
    print("=" * 60)

    # 检查必要的文件
    required_files = ['main.py', 'config.py', 'requirements.txt']
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误：找不到必要文件 {file}")
            sys.exit(1)

    # 检查必要的目录
    required_dirs = ['dao', 'db', 'models', 'services', 'utils', 'views']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"错误：找不到必要目录 {dir_name}")
            sys.exit(1)

    # 创建图标目录
    create_icon()

    # 打包命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "main.spec"
    ]

    print(f"执行命令: {' '.join(cmd)}")
    print("-" * 60)

    try:
        subprocess.check_call(cmd)
        print("-" * 60)
        print("✓ 打包成功！")
        print("-" * 60)
        print(f"可执行文件位置: dist/天津市市政工程局综合管理系统.exe")
        print("-" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print("-" * 60)
        print(f"✗ 打包失败：{e}")
        print("-" * 60)
        return False

def build_installer():
    """创建安装程序（可选，需要 Inno Setup）"""
    print("\n是否创建安装程序？")
    print("需要安装 Inno Setup (https://jrsoftware.org/isdl.php)")
    print("安装完成后运行安装程序脚本")

def main():
    """主函数"""
    print("天津市市政工程局综合管理系统 - 打包工具")
    print("=" * 60)

    # 检查是否安装了 PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller 已安装：{PyInstaller.__version__}")
    except ImportError:
        print("未安装 PyInstaller，正在安装...")
        install_pyinstaller()

    # 打包可执行文件
    success = build_executable()

    if success:
        print("\n打包完成！")
        print("\n后续步骤：")
        print("1. 测试可执行文件是否正常运行")
        print("2. 在目标机器上配置数据库连接（修改config.py）")
        print("3. 如果需要，可以创建安装程序")

if __name__ == '__main__':
    main()