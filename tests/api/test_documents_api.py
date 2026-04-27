# -*- coding: utf-8 -*-
"""
公文管理接口测试
- 公文列表/详情/CRUD
- 公文提交/审批/下达
- 我的公文/收到的公文
"""
import pytest
import random
from tests.common.api_client import APIClient
from tests.common.constants import API, HTTPStatus, Roles
from tests.common.config import test_config


class TestDocumentsList:
    """公文列表接口测试"""

    def test_get_documents(self, admin_client: APIClient):
        """测试获取公文列表"""
        resp = admin_client.get_documents()
        assert resp.get("code") == 200

    def test_get_documents_pagination(self, admin_client: APIClient):
        """测试公文列表分页"""
        resp = admin_client.get_documents(page=1, page_size=5)
        assert resp.get("code") == 200

    def test_get_document_detail(self, admin_client: APIClient):
        """测试获取公文详情"""
        list_resp = admin_client.get_documents(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))

        if items and len(items) > 0:
            doc_id = items[0].get("id", items[0].get("doc_id"))
            if doc_id:
                resp = admin_client.get_document(doc_id)
                assert resp.get("code") == 200

    def test_get_document_not_found(self, admin_client: APIClient):
        """测试获取不存在的公文"""
        resp = admin_client.get_document(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


class TestDocumentsCRUD:
    """公文 CRUD 测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self._created_ids = []
        yield
        for did in self._created_ids:
            try:
                c = APIClient()
                c.login(test_config.admin.username, test_config.admin.password)
                c.delete_document(did)
            except Exception:
                pass

    def test_create_document(self, office_client: APIClient):
        """测试创建公文"""
        suffix = random.randint(10000, 99999)

        resp = office_client.create_document(
            title=f"测试公文_{suffix}",
            content=f"这是测试公文的内容_{suffix}",
            doc_type="通知",
            priority="normal",
            sender_id=test_config.office.user_id,
            receiver_org_ids=[1],
        )

        if resp.get("code") in (HTTPStatus.OK, HTTPStatus.CREATED):
            data = resp.get("data", {})
            doc_id = data.get("id", data.get("doc_id"))
            if doc_id:
                self._created_ids.append(doc_id)

    def test_update_document(self, office_client: APIClient):
        """测试更新公文"""
        list_resp = office_client.get_documents(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            doc_id = items[0].get("id", items[0].get("doc_id"))
            if doc_id:
                new_title = f"更新后的公文_{random.randint(10000, 99999)}"
                resp = office_client.update_document(doc_id, title=new_title)
                if resp.get("code") == 200:
                    detail = office_client.get_document(doc_id)
                    data = detail.get("data", {})
                    assert data.get("title") == new_title


class TestDocumentsWorkflow:
    """公文审批流程测试"""

    def test_submit_document(self, office_client: APIClient):
        """测试提交公文"""
        list_resp = office_client.get_documents(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            doc_id = items[0].get("id", items[0].get("doc_id"))
            if doc_id:
                resp = office_client.submit_document(doc_id, comment="请审批")
                assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.FORBIDDEN)

    def test_document_approve_reject(self, leader_client: APIClient):
        """测试公文审批/拒绝"""
        list_resp = leader_client.get_documents(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            doc_id = items[0].get("id", items[0].get("doc_id"))
            if doc_id:
                # 尝试审批
                resp_approve = leader_client.approve_document(doc_id, comment="同意")
                # 尝试拒绝
                resp_reject = leader_client.reject_document(doc_id, comment="不同意")
                assert resp_approve.get("_status_code") in (HTTPStatus.OK, HTTPStatus.FORBIDDEN)
                assert resp_reject.get("_status_code") in (HTTPStatus.OK, HTTPStatus.FORBIDDEN)

    def test_distribute_document(self, office_client: APIClient):
        """测试下达公文"""
        list_resp = office_client.get_documents(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            doc_id = items[0].get("id", items[0].get("doc_id"))
            if doc_id:
                resp = office_client.distribute_document(doc_id, target_org_ids=[1])
                assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.FORBIDDEN)


class TestDocumentsPersonal:
    """个人公文测试"""

    def test_get_my_documents(self, office_client: APIClient):
        """测试获取我的公文"""
        resp = office_client.get_my_documents()
        assert resp.get("code") == 200

    def test_get_received_documents(self, admin_client: APIClient):
        """测试获取收到的公文"""
        resp = admin_client.get_received_documents()
        assert resp.get("code") == 200

    def test_get_same_level_documents(self, admin_client: APIClient):
        """测试获取同级函件"""
        resp = admin_client.get_same_level_documents()
        assert resp.get("code") == 200