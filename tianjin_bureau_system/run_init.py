# -*- coding: utf-8 -*-
"""
运行数据库初始化
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试导入
try:
    from config import DB_CONFIG
    print(f"数据库配置: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
except Exception as e:
    print(f"导入config失败: {e}")
    sys.exit(1)

from db.init_db import init_all

if __name__ == '__main__':
    init_all()
    input("按回车键退出...")