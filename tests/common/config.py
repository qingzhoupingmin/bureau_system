# -*- coding: utf-8 -*-
"""
测试配置 - 测试用户、URL等配置信息
"""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class TestUser:
    """测试用户配置"""
    username: str
    password: str
    role: str
    org_id: int
    full_name: str
    org_name: str = ""
    user_id: int = 0  # 预留，可在运行时填充


@dataclass
class TestConfig:
    """测试配置"""
    # API配置
    base_url: str = "http://127.0.0.1:8000"

    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "root"
    db_name: str = "tianjin_bureau"

    # 测试用户 - 10种角色
    admin: TestUser = field(default_factory=lambda: TestUser(
        username="admin", password="admin123", role="system_admin",
        org_id=1, full_name="系统管理员"
    ))
    leader: TestUser = field(default_factory=lambda: TestUser(
        username="leader_l1", password="leader123", role="leader",
        org_id=0, full_name="党委书记(局领导)"
    ))
    asset_manager: TestUser = field(default_factory=lambda: TestUser(
        username="asset_mgr", password="asset123", role="asset_manager",
        org_id=10, full_name="资产管理处处长"
    ))
    office: TestUser = field(default_factory=lambda: TestUser(
        username="office1", password="office123", role="office_staff",
        org_id=1, full_name="办公室主任"
    ))
    hr: TestUser = field(default_factory=lambda: TestUser(
        username="hr_staff", password="hr123", role="hr_staff",
        org_id=11, full_name="劳动人事处处长"
    ))
    tech: TestUser = field(default_factory=lambda: TestUser(
        username="tech1", password="tech123", role="tech_staff",
        org_id=12, full_name="科技处处长"
    ))
    finance: TestUser = field(default_factory=lambda: TestUser(
        username="finance1", password="finance123", role="finance_staff",
        org_id=7, full_name="财务处处长"
    ))
    unit_user: TestUser = field(default_factory=lambda: TestUser(
        username="unit_user1", password="unit123", role="unit_user",
        org_id=21, full_name="中层单位用户-公路处"
    ))
    sub_unit_user: TestUser = field(default_factory=lambda: TestUser(
        username="sub_unit1", password="sub123", role="sub_unit_user",
        org_id=51, full_name="基层单位用户-第一桥梁管理所"
    ))
    normal: TestUser = field(default_factory=lambda: TestUser(
        username="user1", password="user123", role="normal_user",
        org_id=3, full_name="普通处室用户"
    ))

    # 额外的测试用户（用于多用户场景）
    extra_unit_user: TestUser = field(default_factory=lambda: TestUser(
        username="unit_user2", password="unit123", role="unit_user",
        org_id=23, full_name="中层单位用户-道路桥梁管理处"
    ))
    extra_sub_unit: TestUser = field(default_factory=lambda: TestUser(
        username="sub_unit2", password="sub123", role="sub_unit_user",
        org_id=61, full_name="基层单位用户-高速路政大队"
    ))

    def get_user_by_role(self, role: str) -> Optional[TestUser]:
        """根据角色名获取测试用户"""
        mapping = {
            "system_admin": self.admin,
            "leader": self.leader,
            "asset_manager": self.asset_manager,
            "office_staff": self.office,
            "hr_staff": self.hr,
            "tech_staff": self.tech,
            "finance_staff": self.finance,
            "unit_user": self.unit_user,
            "sub_unit_user": self.sub_unit_user,
            "normal_user": self.normal,
        }
        return mapping.get(role)

    def get_all_users(self) -> Dict[str, TestUser]:
        """获取所有测试用户"""
        return {
            "admin": self.admin,
            "leader": self.leader,
            "asset_manager": self.asset_manager,
            "office": self.office,
            "hr": self.hr,
            "tech": self.tech,
            "finance": self.finance,
            "unit_user": self.unit_user,
            "sub_unit_user": self.sub_unit_user,
            "normal": self.normal,
        }


# 全局测试配置实例
test_config = TestConfig()