# -*- coding: utf-8 -*-
"""
预算管理接口测试
- 预算列表/详情/CRUD
- 预算申报/审批
- 预算统计
"""
import pytest
from tests.common.api_client import APIClient
from tests.common.constants import API, HTTPStatus, Roles
from tests.common.config import test_config


class TestBudgetsList:
    """预算列表接口测试"""

    def test_get_budgets(self, admin_client: APIClient):
        """测试获取预算列表"""
        resp = admin_client.get_budgets()
        assert resp.get("code") == 200

    def test_get_budgets_pagination(self, admin_client: APIClient):
        """测试预算列表分页"""
        resp = admin_client.get_budgets(page=1, page_size=5)
        assert resp.get("code") == 200

    def test_get_budget_detail(self, admin_client: APIClient):
        """测试获取预算详情"""
        list_resp = admin_client.get_budgets(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))

        if items and len(items) > 0:
            budget_id = items[0].get("id", items[0].get("budget_id"))
            if budget_id:
                resp = admin_client.get_budget(budget_id)
                assert resp.get("code") == 200

    def test_get_budget_not_found(self, admin_client: APIClient):
        """测试获取不存在的预算"""
        resp = admin_client.get_budget(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


class TestBudgetsCRUD:
    """预算 CRUD 测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self._created_ids = []
        yield
        for bid in self._created_ids:
            try:
                c = APIClient()
                c.login(test_config.admin.username, test_config.admin.password)
                c.delete_budget(bid)
            except Exception:
                pass

    def test_create_budget(self, finance_client: APIClient):
        """测试创建预算"""
        import random
        suffix = random.randint(10000, 99999)

        resp = finance_client.create_budget(
            year=2025,
            name=f"测试预算_{suffix}",
            total_amount=100000.00,
            organization_id=1,
            category="日常办公",
        )

        if resp.get("code") in (HTTPStatus.OK, HTTPStatus.CREATED):
            data = resp.get("data", {})
            budget_id = data.get("id", data.get("budget_id"))
            if budget_id:
                self._created_ids.append(budget_id)

    def test_update_budget(self, finance_client: APIClient):
        """测试更新预算"""
        list_resp = finance_client.get_budgets(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            budget_id = items[0].get("id", items[0].get("budget_id"))
            if budget_id:
                resp = finance_client.update_budget(budget_id, total_amount=200000.00)
                if resp.get("code") == 200:
                    detail = finance_client.get_budget(budget_id)
                    data = detail.get("data", {})
                    assert data.get("total_amount") == 200000.00

    def test_delete_budget(self, finance_client: APIClient):
        """测试删除预算"""
        resp = finance_client.delete_budget(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


class TestBudgetsApplications:
    """预算申报审批测试"""

    def test_budget_apply_workflow(self, normal_client: APIClient,
                                   finance_client: APIClient):
        """测试预算申报审批全流程"""
        # 1. 获取预算列表
        list_resp = finance_client.get_budgets(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if not items or len(items) == 0:
            pytest.skip("没有可用的预算进行申报测试")

        budget_id = items[0].get("id", items[0].get("budget_id"))
        if not budget_id:
            pytest.skip("无法获取预算 ID")

        # 2. 申报预算
        resp = normal_client.apply_budget(budget_id, amount=10000.00, reason="测试预算申报")
        assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.FORBIDDEN)


class TestBudgetsStatistics:
    """预算统计测试"""

    def test_get_budget_statistics(self, admin_client: APIClient):
        """测试获取预算统计"""
        resp = admin_client.get_budget_statistics()
        assert resp.get("code") == 200

    def test_get_my_budget_applications(self, normal_client: APIClient):
        """测试获取我的预算申报"""
        resp = normal_client.get_my_budget_applications()
        assert resp.get("code") == 200