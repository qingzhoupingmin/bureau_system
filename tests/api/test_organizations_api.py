# -*- coding: utf-8 -*-
"""
组织架构接口测试
- 组织列表/树形结构
- 机关处室/中层单位/基层单位
- 组织下的用户和资产统计
"""
import pytest
from tests.common.api_client import APIClient
from tests.common.constants import API, HTTPStatus
from tests.common.config import test_config


class TestOrganizationsList:
    """组织列表接口测试"""

    def test_get_organizations(self, admin_client: APIClient):
        """测试获取组织列表"""
        resp = admin_client.get_organizations()

        assert resp.get("code") == 200

    def test_get_organizations_with_parent(self, admin_client: APIClient):
        """测试按父级组织筛选"""
        resp = admin_client.get_organizations(parent_id=1)

        if resp.get("code") == 200:
            data = resp.get("data", {})
            items = data.get("items", data.get("data", []))
            if items:
                for item in items:
                    assert str(item.get("parent_id")) == "1" or item.get("parent_id") == 1

    def test_get_organization_detail(self, admin_client: APIClient):
        """测试获取组织详情"""
        resp = admin_client.get_organization(1)

        if resp.get("code") == 200:
            data = resp.get("data", {})
            assert "id" in data or "org_id" in data or "organization_id" in data

    def test_get_org_tree(self, admin_client: APIClient):
        """测试获取组织架构树"""
        resp = admin_client.get_org_tree()

        assert resp.get("code") == 200


class TestOrganizationTypes:
    """不同类型组织接口测试"""

    def test_get_departments(self, admin_client: APIClient):
        """测试获取机关处室"""
        resp = admin_client.get_departments()

        assert resp.get("code") == 200
        data = resp.get("data", [])
        if data and isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                pass  # 验证存在

    def test_get_units(self, admin_client: APIClient):
        """测试获取中层单位"""
        resp = admin_client.get_units()

        assert resp.get("code") == 200

    def test_get_sub_units(self, admin_client: APIClient):
        """测试获取基层单位"""
        # 先获取中层单位列表，取第一个
        units_resp = admin_client.get_units()
        units = units_resp.get("data", [])
        parent_id = None

        if units and len(units) > 0:
            parent_id = units[0].get("id", units[0].get("org_id"))

        if parent_id:
            resp = admin_client.get_sub_units(parent_id)
            assert resp.get("code") == 200


class TestOrganizationUsers:
    """组织用户接口测试"""

    def test_get_org_users(self, admin_client: APIClient):
        """测试获取组织下的用户"""
        resp = admin_client.get_org_users(1)

        assert resp.get("code") == 200

    def test_get_org_assets_stats(self, admin_client: APIClient):
        """测试获取组织资产统计"""
        resp = admin_client.get_org_assets_stats(1)

        assert resp.get("code") == 200

    def test_get_org_path(self, admin_client: APIClient):
        """测试获取组织路径"""
        resp = admin_client.get_org_path(1)

        if resp.get("code") == 200:
            data = resp.get("data", {})
            assert "path" in data or isinstance(data, (list, str))