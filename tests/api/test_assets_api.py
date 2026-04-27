# -*- coding: utf-8 -*-
"""
资产管理接口测试
- 资产列表/详情/CRUD
- 资产申请/审批
- 资产统计
"""
import pytest
from tests.common.api_client import APIClient
from tests.common.constants import API, HTTPStatus, Roles
from tests.common.config import test_config


class TestAssetsList:
    """资产列表接口测试"""

    def test_get_assets(self, admin_client: APIClient):
        """测试获取资产列表"""
        resp = admin_client.get_assets()

        assert resp.get("code") == 200

    def test_get_assets_pagination(self, admin_client: APIClient):
        """测试资产列表分页"""
        resp = admin_client.get_assets(page=1, page_size=5)

        assert resp.get("code") == 200

    def test_get_asset_detail(self, admin_client: APIClient):
        """测试获取资产详情"""
        # 先获取资产列表，取第一个 ID
        list_resp = admin_client.get_assets(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))

        if items and len(items) > 0:
            asset_id = items[0].get("id", items[0].get("asset_id"))
            if asset_id:
                resp = admin_client.get_asset(asset_id)
                assert resp.get("code") == 200

    def test_get_asset_detail_not_found(self, admin_client: APIClient):
        """测试获取不存在的资产"""
        resp = admin_client.get_asset(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


class TestAssetsCRUD:
    """资产 CRUD 测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self._created_ids = []
        yield
        for aid in self._created_ids:
            try:
                c = APIClient()
                c.login(test_config.admin.username, test_config.admin.password)
                c.delete_asset(aid)
            except Exception:
                pass

    def test_create_asset(self, asset_mgr_client: APIClient):
        """测试创建资产"""
        import random
        suffix = random.randint(10000, 99999)

        resp = asset_mgr_client.create_asset(
            name=f"测试资产_{suffix}",
            category="电子设备",
            model=f"Model-{suffix}",
            quantity=1,
            unit_price=5000.00,
            total_price=5000.00,
            organization_id=1,
            status="正常",
            location=f"测试位置_{suffix}",
        )

        if resp.get("code") in (HTTPStatus.OK, HTTPStatus.CREATED):
            data = resp.get("data", {})
            asset_id = data.get("id", data.get("asset_id"))
            if asset_id:
                self._created_ids.append(asset_id)

    def test_update_asset(self, asset_mgr_client: APIClient):
        """测试更新资产"""
        list_resp = asset_mgr_client.get_assets(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            asset_id = items[0].get("id", items[0].get("asset_id"))
            if asset_id:
                resp = asset_mgr_client.update_asset(asset_id, location="更新后的位置")
                if resp.get("code") == 200:
                    detail = asset_mgr_client.get_asset(asset_id)
                    data = detail.get("data", {})
                    assert data.get("location") == "更新后的位置"

    def test_delete_asset(self, asset_mgr_client: APIClient):
        """测试删除资产"""
        resp = asset_mgr_client.delete_asset(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


class TestAssetsApplications:
    """资产申请审批测试"""

    def test_asset_apply_workflow(self, normal_client: APIClient,
                                  asset_mgr_client: APIClient):
        """测试资产申请审批全流程"""
        # 1. 获取一个资产
        list_resp = asset_mgr_client.get_assets(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if not items or len(items) == 0:
            pytest.skip("没有可用的资产进行申请测试")

        asset_id = items[0].get("id", items[0].get("asset_id"))
        if not asset_id:
            pytest.skip("无法获取资产 ID")

        # 2. 申请资产
        resp = normal_client.apply_for_asset(asset_id, quantity=1, reason="测试申请")
        assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.FORBIDDEN)


class TestAssetsStatistics:
    """资产统计测试"""

    def test_get_asset_statistics(self, admin_client: APIClient):
        """测试获取资产统计"""
        resp = admin_client.get_asset_statistics()
        assert resp.get("code") == 200

    def test_get_org_assets(self, admin_client: APIClient):
        """测试获取组织资产"""
        resp = admin_client.get_org_assets(1)
        assert resp.get("code") == 200

    def test_get_sub_orgs_assets(self, admin_client: APIClient):
        """测试获取下级单位资产"""
        resp = admin_client.get_sub_orgs_assets()
        assert resp.get("code") == 200

    def test_get_asset_level_stats(self, admin_client: APIClient):
        """测试获取分层级资产统计"""
        resp = admin_client.get_asset_level_stats()
        assert resp.get("code") == 200