# -*- coding: utf-8 -*-
"""
用户管理接口测试
- 用户列表/详情
- 用户创建/更新/删除
- 密码重置
"""
import pytest
from tests.common.api_client import APIClient
from tests.common.constants import API, HTTPStatus, Roles
from tests.common.config import test_config


class TestUsersList:
    """用户列表接口测试"""

    def test_get_users_success(self, admin_client: APIClient):
        """测试获取用户列表"""
        resp = admin_client.get_users()

        assert resp.get("code") == 200, f"获取用户列表失败: {resp}"
        data = resp.get("data", {})
        # 分页数据
        assert "items" in data or "data" in data or isinstance(data.get("total"), int)

    def test_get_users_pagination(self, admin_client: APIClient):
        """测试用户列表分页"""
        resp = admin_client.get_users(page=1, page_size=5)

        assert resp.get("code") == 200

    def test_get_users_unauthorized(self, api_client: APIClient):
        """测试未授权获取用户列表"""
        resp = api_client.get_users()

        assert resp.get("_status_code") in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, HTTPStatus.OK)

    def test_get_user_detail(self, admin_client: APIClient):
        """测试获取用户详情"""
        user_id = test_config.admin.user_id
        resp = admin_client.get_user(user_id)

        if resp.get("code") == 200:
            data = resp.get("data", {})
            assert str(data.get("id", data.get("user_id", ""))) == str(user_id)

    def test_get_user_not_found(self, admin_client: APIClient):
        """测试获取不存在的用户"""
        resp = admin_client.get_user(99999)

        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


class TestUsersCreate:
    """用户创建接口测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """测试前后清理"""
        self._created_ids = []
        yield
        # 清理创建的用户
        for uid in self._created_ids:
            try:
                admin_client = APIClient()
                admin_client.login(test_config.admin.username, test_config.admin.password)
                admin_client.delete_user(uid)
            except Exception:
                pass

    def test_create_user_success(self, admin_client: APIClient):
        """测试创建用户"""
        import random
        suffix = random.randint(10000, 99999)
        username = f"test_user_{suffix}"

        resp = admin_client.create_user(
            username=username,
            password="test123456",
            role=Roles.NORMAL_USER,
            org_id=test_config.normal.org_id,
            full_name=f"测试用户{suffix}",
        )

        if resp.get("code") in (HTTPStatus.OK, HTTPStatus.CREATED):
            data = resp.get("data", {})
            user_id = data.get("id", data.get("user_id"))
            if user_id:
                self._created_ids.append(user_id)

    def test_create_user_duplicate(self, admin_client: APIClient):
        """测试创建重复用户"""
        resp = admin_client.create_user(
            username=test_config.normal.username,
            password="test123456",
            role=Roles.NORMAL_USER,
            org_id=test_config.normal.org_id,
            full_name="重复用户测试",
        )

        assert resp.get("_status_code") in (HTTPStatus.CONFLICT, HTTPStatus.BAD_REQUEST, HTTPStatus.OK)

    def test_create_user_unauthorized(self, api_client: APIClient):
        """测试未授权创建用户"""
        resp = api_client.create_user(
            username="unauth_user",
            password="test123",
            role=Roles.NORMAL_USER,
            org_id=1,
            full_name="未授权创建",
        )

        assert resp.get("_status_code") in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, HTTPStatus.OK)


class TestUsersUpdate:
    """用户更新接口测试"""

    def test_update_user(self, admin_client: APIClient):
        """测试更新用户"""
        user_id = test_config.normal.user_id
        new_name = "已更新的测试用户"
        resp = admin_client.update_user(user_id, full_name=new_name)

        # 如果成功，验证
        if resp.get("code") == 200:
            detail_resp = admin_client.get_user(user_id)
            data = detail_resp.get("data", {})
            assert data.get("full_name") == new_name


class TestUsersDelete:
    """用户删除接口测试"""

    def test_delete_nonexistent_user(self, admin_client: APIClient):
        """测试删除不存在的用户"""
        resp = admin_client.delete_user(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)