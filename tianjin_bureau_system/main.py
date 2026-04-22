# -*- coding: utf-8 -*-
"""
天津市市政工程局综合管理系统 - 主入口
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.login_window import LoginWindow
from views.asset_manager_window import AssetManagerWindow
from views.office_window import OfficeWindow
from views.tech_window import TechWindow
from views.finance_window import FinanceWindow
from views.leader_window import LeaderWindow
from views.department_window import DepartmentWindow
from views.normal_user_window import NormalUserWindow
from services.auth_service import AuthService
from config import (
    ROLE_ADMIN, ROLE_LEADER, ROLE_ASSET_MANAGER, ROLE_OFFICE_STAFF,
    ROLE_TECH_STAFF, ROLE_FINANCE_STAFF, ROLE_UNIT_USER, ROLE_SUB_UNIT_USER
)


def get_window_by_role(user):
    """根据用户角色返回对应窗口"""
    role = user['role']

    # 系统管理员
    if role == ROLE_ADMIN:
        return AssetManagerWindow(user)

    # 资产管理处
    elif role == ROLE_ASSET_MANAGER:
        return AssetManagerWindow(user)

    # 办公室
    elif role == ROLE_OFFICE_STAFF:
        return OfficeWindow(user)

    # 科技处
    elif role == ROLE_TECH_STAFF:
        return TechWindow(user)

    # 财务处
    elif role == ROLE_FINANCE_STAFF:
        return FinanceWindow(user)

    # 局领导
    elif role == ROLE_LEADER:
        return LeaderWindow(user)

    # 下属单位
    elif role == ROLE_UNIT_USER:
        return NormalUserWindow(user)

    # 下属单位的下属单位（如道桥处下属单位）
    elif role == ROLE_SUB_UNIT_USER:
        return NormalUserWindow(user)

    # 普通处室用户 (normal_user) - 使用专业处室窗口
    elif role == 'normal_user':
        return DepartmentWindow(user)

    # 其他情况默认
    else:
        return DepartmentWindow(user)


def main():
    """主函数"""
    print("启动天津市市政工程局综合管理系统...")

    # 显示登录窗口
    login_window = LoginWindow()
    user = login_window.show()

    if not user:
        print("用户取消登录，系统退出")
        return

    print(f"用户登录成功: {user['full_name']} ({user['role']})")

    # 根据角色打开对应窗口
    main_window = get_window_by_role(user)
    main_window.show()


if __name__ == '__main__':
    main()