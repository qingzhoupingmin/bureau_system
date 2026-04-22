# -*- coding: utf-8 -*-
"""
打包测试脚本 - 测试打包后的程序是否正常
"""
import os
import sys
import subprocess

def test_imports():
    """测试所有必要的模块是否可以导入"""
    print("=" * 60)
    print("测试模块导入...")
    print("=" * 60)

    required_modules = [
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'pymysql',
        'config',
        'models.asset',
        'models.user',
        'models.document',
        'models.message',
        'models.organization',
        'db.connection',
        'services.auth_service',
        'services.asset_service',
        'views.login_window',
        'views.asset_manager_window',
        'views.organization_overview',
    ]

    failed = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - {e}")
            failed.append(module)

    if failed:
        print(f"\n失败的模块：{', '.join(failed)}")
        return False
    else:
        print("\n所有模块导入成功！")
        return True

def test_files_exist():
    """测试必要文件是否存在"""
    print("\n" + "=" * 60)
    print("测试文件完整性...")
    print("=" * 60)

    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
    ]

    required_dirs = [
        'dao',
        'db',
        'models',
        'services',
        'utils',
        'views',
    ]

    missing = []

    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            missing.append(file)

    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/")
            missing.append(dir_name)

    if missing:
        print(f"\n缺失的文件/目录：{', '.join(missing)}")
        return False
    else:
        print("\n所有文件完整！")
        return True

def test_config():
    """测试配置文件"""
    print("\n" + "=" * 60)
    print("测试配置文件...")
    print("=" * 60)

    try:
        from config import DB_CONFIG

        print("数据库配置：")
        print(f"  主机: {DB_CONFIG.get('host')}")
        print(f"  端口: {DB_CONFIG.get('port')}")
        print(f"  用户: {DB_CONFIG.get('user')}")
        print(f"  数据库: {DB_CONFIG.get('database')}")
        print("\n✓ 配置文件正常")
        return True
    except Exception as e:
        print(f"\n✗ 配置文件错误：{e}")
        return False

def test_database_connection():
    """测试数据库连接（可选）"""
    print("\n" + "=" * 60)
    print("测试数据库连接...")
    print("=" * 60)

    try:
        from db.connection import db

        result = db.execute_query("SELECT 1 as test")
        if result and result[0]['test'] == 1:
            print("✓ 数据库连接成功")
            return True
        else:
            print("✗ 数据库查询失败")
            return False
    except Exception as e:
        print(f"⚠ 数据库连接失败（可忽略）：{e}")
        print("  注意：首次打包时可能数据库未初始化")
        return True  # 不影响打包

def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("*" * 60)
    print("天津市市政工程局综合管理系统 - 打包前测试")
    print("*" * 60)

    results = []

    # 测试文件完整性
    results.append(("文件完整性", test_files_exist()))

    # 测试模块导入
    results.append(("模块导入", test_imports()))

    # 测试配置文件
    results.append(("配置文件", test_config()))

    # 测试数据库连接
    results.append(("数据库连接", test_database_connection()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name:15s} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ 所有测试通过，可以开始打包！")
        print("  运行 '快速打包.bat' 开始打包")
    else:
        print("\n✗ 部分测试失败，请检查并修复后再打包")

    print("\n")

if __name__ == '__main__':
    run_all_tests()