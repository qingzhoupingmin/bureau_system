# -*- coding: utf-8 -*-
"""
三级管理数据隔离工具
"""
from typing import List, Dict, Optional
from db.connection import db


class ThreeLevelManager:
    """三级管理数据隔离管理器"""

    @staticmethod
    def get_organization_type(org_id: int) -> Optional[str]:
        """
        获取组织类型

        Args:
            org_id: 组织ID

        Returns:
            组织类型: department/unit/sub_unit/None
        """
        sql = "SELECT type FROM organizations WHERE id = %s"
        result = db.execute_query(sql, (org_id,))
        return result[0]['type'] if result else None

    @staticmethod
    def get_organization_path(org_id: int) -> List[Dict]:
        """
        获取组织的完整路径（从局机关到该组织）

        Args:
            org_id: 组织ID

        Returns:
            组织路径列表
        """
        sql = "SELECT * FROM organizations WHERE id = %s"
        result = db.execute_query(sql, (org_id,))

        if not result:
            return []

        path = [result[0]]
        current = result[0]

        # 递归查找父组织
        while current.get('parent_id'):
            sql = "SELECT * FROM organizations WHERE id = %s"
            parent_result = db.execute_query(sql, (current['parent_id'],))
            if parent_result:
                path.append(parent_result[0])
                current = parent_result[0]
            else:
                break

        # 反转路径，从顶层开始
        path.reverse()
        return path

    @staticmethod
    def get_subordinate_organizations(org_id: int) -> List[Dict]:
        """
        获取组织的所有下级组织

        Args:
            org_id: 组织ID

        Returns:
            下级组织列表
        """
        sql = "SELECT * FROM organizations WHERE parent_id = %s"
        return db.execute_query(sql, (org_id,))

    @staticmethod
    def get_all_subordinates(org_id: int, include_self: bool = True) -> List[int]:
        """
        获取组织的所有下级组织ID（包括递归下级）

        Args:
            org_id: 组织ID
            include_self: 是否包含自己

        Returns:
            组织ID列表
        """
        org_ids = []

        def collect_sub_organizations(parent_id):
            if include_self:
                org_ids.append(parent_id)

            subs = ThreeLevelManager.get_subordinate_organizations(parent_id)
            for sub in subs:
                collect_sub_organizations(sub['id'])

        collect_sub_organizations(org_id)

        return org_ids

    @staticmethod
    def get_accessible_organizations(user_org_id: int, user_role: str) -> List[int]:
        """
        根据用户角色获取可访问的组织列表

        Args:
            user_org_id: 用户所属组织ID
            user_role: 用户角色

        Returns:
            可访问的组织ID列表
        """
        org_type = ThreeLevelManager.get_organization_type(user_org_id)

        # 局机关（system_admin, leader等）可以访问所有组织
        if user_role in ['system_admin', 'leader']:
            sql = "SELECT id FROM organizations"
            result = db.execute_query(sql)
            return [org['id'] for org in result]

        # 局机关处室可以访问所有组织
        elif org_type == 'department':
            sql = "SELECT id FROM organizations"
            result = db.execute_query(sql)
            return [org['id'] for org in result]

        # 中层单位可以访问自己和下级组织
        elif org_type == 'unit':
            return ThreeLevelManager.get_all_subordinates(user_org_id, include_self=True)

        # 基层单位只能访问自己
        elif org_type == 'sub_unit':
            return [user_org_id]

        # 其他情况只能访问自己
        else:
            return [user_org_id]

    @staticmethod
    def can_access_organization(user_org_id: int, target_org_id: int, user_role: str) -> bool:
        """
        检查用户是否可以访问目标组织

        Args:
            user_org_id: 用户所属组织ID
            target_org_id: 目标组织ID
            user_role: 用户角色

        Returns:
            是否可以访问
        """
        # 获取用户可访问的组织列表
        accessible_orgs = ThreeLevelManager.get_accessible_organizations(user_org_id, user_role)

        return target_org_id in accessible_orgs

    @staticmethod
    def add_organization_filter(sql: str, user_org_id: int, user_role: str, table_alias: str = "") -> tuple:
        """
        为SQL添加组织过滤条件（三级管理数据隔离）

        Args:
            sql: 原始SQL语句
            user_org_id: 用户所属组织ID
            user_role: 用户角色
            table_alias: 表别名（如 organization_id 改为 o.organization_id）

        Returns:
            (修改后的SQL, 参数列表)
        """
        params = []
        accessible_orgs = ThreeLevelManager.get_accessible_organizations(user_org_id, user_role)

        # 如果可以访问所有组织，不添加过滤
        org_type = ThreeLevelManager.get_organization_type(user_org_id)
        if user_role in ['system_admin', 'leader'] or org_type == 'department':
            return sql, []

        # 构建IN子句
        column = f"{table_alias}.organization_id" if table_alias else "organization_id"
        placeholders = ','.join(['%s'] * len(accessible_orgs))

        # 添加WHERE条件
        if 'WHERE' in sql.upper():
            filtered_sql = sql + f" AND {column} IN ({placeholders})"
        else:
            filtered_sql = sql + f" WHERE {column} IN ({placeholders})"

        return filtered_sql, tuple(accessible_orgs)

    @staticmethod
    def check_cross_level_communication(from_org_id: int, to_org_id: int) -> tuple[bool, str]:
        """
        检查跨层级通信是否允许

        Args:
            from_org_id: 发送方组织ID
            to_org_id: 接收方组织ID

        Returns:
            (是否允许, 拒绝原因)
        """
        from_type = ThreeLevelManager.get_organization_type(from_org_id)
        to_type = ThreeLevelManager.get_organization_type(to_org_id)

        # 局机关可以向任何人发送
        if from_type == 'department':
            return True, ""

        # 中层单位可以向局机关和自己的下级发送
        elif from_type == 'unit':
            if to_type == 'department':
                return True, ""
            elif to_type == 'sub_unit':
                # 检查是否是自己的下级
                sub_orgs = ThreeLevelManager.get_all_subordinates(from_org_id, include_self=False)
                if to_org_id in sub_orgs:
                    return True, ""
                else:
                    return False, "只能向直属下级单位发送"

        # 基层单位只能向直属中层单位发送
        elif from_type == 'sub_unit':
            sql = "SELECT parent_id FROM organizations WHERE id = %s"
            result = db.execute_query(sql, (from_org_id,))
            if result and result[0]['parent_id'] == to_org_id:
                return True, ""
            else:
                return False, "只能向直属中层单位发送"

        return False, "不允许的跨层级通信"

    @staticmethod
    def get_user_level(user_role: str) -> int:
        """
        获取用户角色等级

        Args:
            user_role: 用户角色

        Returns:
            角色等级数字
        """
        role_hierarchy = {
            'system_admin': 10,
            'leader': 9,
            'asset_manager': 8,
            'office_staff': 7,
            'tech_staff': 6,
            'finance_staff': 6,
            'hr_staff': 6,
            'unit_user': 5,
            'sub_unit_user': 4,
            'normal_user': 1
        }
        return role_hierarchy.get(user_role, 0)