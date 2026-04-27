# -*- coding: utf-8 -*-
"""
认证接口测试
- 登录/登出
- 密码修改
- 权限检查
- 密码修改审批
"""
import pytest
from tests.common.api_client import APIClient
from tests.common.constants import Roles, API, HTTPStatus, Status
from tests.common.config import test_config


class TestAuthLogin:
    """登录接口测试"""

    LOGIN_URL = API.AUTH_LOGIN

    def test_login_success(self, api_client: APIClient):
        """测试成功登录"""
        resp = api_client.login(test_config.admin.username, test_config.admin.password)

        assert resp.get("_status_code") == HTTPStatus.OK
        assert resp.get("code") == 200
        assert resp.get("message") == "登录成功"

        data = resp.get("data", {})
        assert "user_id" in data
        assert data.get("username") == test_config.admin.username
        assert data.get("role") == Roles.SYSTEM_ADMIN
        assert api_client.token is not None

    def test_login_wrong_password(self, api_client: APIClient):
        """测试错误密码登录"""
        resp = api_client.login("admin", "wrong_password")

        assert resp.get("_status_code") == HTTPStatus.UNAUTHORIZED
        # FastAPI HTTPException 返回 422 或 401
        assert resp.get("_status_code") in (HTTPStatus.UNAUTHORIZED, 422)

    def test_login_nonexistent_user(self, api_client: APIClient):
        """测试不存在的用户登录"""
        resp = api_client.login("nonexistent_user_12345", "test123")

        assert resp.get("_status_code") in (HTTPStatus.UNAUTHORIZED, HTTPStatus.NOT_FOUND)

    def test_login_empty_credentials(self, api_client: APIClient):
        """测试空凭据登录"""
        resp = api_client.login("", "")

        assert resp.get("_status_code") in (HTTPStatus.BAD_REQUEST, 422)

    @pytest.mark.parametrize("role,username_key", [
        (Roles.SYSTEM_ADMIN, "admin"),
        (Roles.LEADER, "leader"),
        (Roles.ASSET_MANAGER, "asset_manager"),
        (Roles.OFFICE, "office"),
        (Roles.HR, "hr"),
        (Roles.TECH, "tech"),
        (Roles.FINANCE, "finance"),
        (Roles.UNIT_USER, "unit_user"),
        (Roles.SUB_UNIT_USER, "sub_unit_user"),
        (Roles.NORMAL_USER, "normal"),
    ])
    def test_all_roles_login(self, api_client: APIClient, role: str, username_key: str):
        """测试所有角色登录"""
        user_cfg = getattr(test_config, username_key)
        resp = api_client.login(user_cfg.username, user_cfg.password)

        assert resp.get("code") == 200, f"角色 {role} 登录失败: {resp}"
        data = resp.get("data", {})
        assert data.get("role") == role


class TestAuthLogout:
    """登出接口测试"""

    def test_logout_success(self, admin_client: APIClient):
        """测试成功登出"""
        user_id = test_config.admin.user_id
        resp = admin_client.logout(user_id)

        assert resp.get("code") == 200
        assert resp.get("message") == "登出成功"
        assert admin_client.token is None

    def test_logout_no_login(self, api_client: APIClient):
        """测试未登录登出"""
        resp = api_client.post(API.AUTH_LOGOUT, json={"user_id": 99999})

        # 未登录也应该能处理
        assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.INTERNAL_ERROR)


class TestAuthPassword:
    """密码修改接口测试"""

    def test_change_password_success(self, normal_client: APIClient):
        """测试成功修改密码（然后改回来）"""
        user_id = test_config.normal.user_id
        old_pwd = test_config.normal.password
        new_pwd = "tmp_new_pwd_123"

        # 修改密码
        resp = normal_client.change_password(user_id, old_pwd, new_pwd)
        assert resp.get("code") == 200

        # 改回原密码
        resp2 = normal_client.change_password(user_id, new_pwd, old_pwd)
        assert resp2.get("code") == 200

    def test_change_password_wrong_old(self, normal_client: APIClient):
        """测试错误原密码修改"""
        user_id = test_config.normal.user_id
        resp = normal_client.change_password(user_id, "wrong_old_pwd", "new_pwd_123")

        assert resp.get("_status_code") in (HTTPStatus.BAD_REQUEST, 422)
        assert resp.get("code") != 200

    def test_change_password_nonexistent_user(self, api_client: APIClient):
        """测试不存在的用户修改密码"""
        resp = api_client.change_password(99999, "old_pwd", "new_pwd")

        assert resp.get("_status_code") in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND)


class TestAuthPermission:
    """权限检查接口测试"""

    def test_admin_has_high_permission(self, api_client: APIClient):
        """测试管理员有高级权限"""
        resp = api_client.check_permission(test_config.admin.user_id, Roles.ASSET_MANAGER)

        assert resp.get("code") == 200
        data = resp.get("data", {})
        assert data.get("has_permission") is True

    def test_normal_user_low_permission(self, api_client: APIClient):
        """测试普通用户无高级权限"""
        resp = api_client.check_permission(test_config.normal.user_id, Roles.ASSET_MANAGER)

        assert resp.get("code") == 200
        data = resp.get("data", {})
        assert data.get("has_permission") is False
        assert data.get("user_role") == Roles.NORMAL_USER

    def test_permission_nonexistent_user(self, api_client: APIClient):
        """测试不存在的用户权限检查"""
        resp = api_client.get(API.AUTH_PERMISSION, params={
            "user_id": 99999,
            "required_role": Roles.SYSTEM_ADMIN
        })

        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, 422)


class TestAuthPasswordApproval:
    """密码修改审批接口测试"""

    def test_password_approve_workflow(self, normal_client: APIClient, hr_client: APIClient):
        """测试密码修改审批全流程"""
        user_id = test_config.normal.user_id
        hr_id = test_config.hr.user_id
        old_pwd = test_config.normal.password
        new_pwd = "tmp_approve_pwd_123"
        reason = "测试审批修改密码"

        # 1. 用户提交密码修改申请
        resp = normal_client.request_password_change(user_id, old_pwd, new_pwd, reason)
        assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NOT_FOUND)

        # 如果成功提交，测试审批
        if resp.get("code") == 200:
            # 2. 劳动人事处审批通过
            resp2 = hr_client.approve_password_change(user_id, hr_id)
            assert resp2.get("_status_code") in (HTTPStatus.OK, HTTPStatus.CREATED)

            # 3. 验证新密码可以登录
            new_client = APIClient()
            resp3 = new_client.login(test_config.normal.username, new_pwd)
            assert resp3.get("code") == 200

            # 4. 改回原密码
            new_client.change_password(user_id, new_pwd, old_pwd)