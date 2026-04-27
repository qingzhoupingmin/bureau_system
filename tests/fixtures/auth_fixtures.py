# -*- coding: utf-8 -*-
"""
认证相关的 pytest fixtures
"""
import pytest
from typing import Dict
from tests.common.api_client import APIClient
from tests.common.config import test_config


@pytest.fixture(scope="function")
def api_client() -> APIClient:
    """创建一个新的 API 客户端"""
    return APIClient(base_url=test_config.base_url)


@pytest.fixture(scope="function")
def admin_token(api_client: APIClient) -> str:
    """管理员 token"""
    resp = api_client.login(test_config.admin.username, test_config.admin.password)
    assert resp.get("code") == 200, f"管理员登录失败: {resp}"
    return api_client.token


@pytest.fixture(scope="function")
def admin_client(api_client: APIClient, admin_token: str) -> APIClient:
    """已登录的管理员客户端"""
    api_client.token = admin_token
    api_client.current_user = {"user_id": test_config.admin.user_id}
    return api_client


@pytest.fixture(scope="function")
def normal_client(api_client: APIClient) -> APIClient:
    """已登录的普通用户客户端"""
    resp = api_client.login(test_config.normal.username, test_config.normal.password)
    assert resp.get("code") == 200, f"普通用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def hr_client(api_client: APIClient) -> APIClient:
    """已登录的劳动人事处客户端"""
    resp = api_client.login(test_config.hr.username, test_config.hr.password)
    assert resp.get("code") == 200, f"劳动人事处登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def asset_mgr_client(api_client: APIClient) -> APIClient:
    """已登录的资产管理处客户端"""
    resp = api_client.login(test_config.asset_manager.username, test_config.asset_manager.password)
    assert resp.get("code") == 200, f"资产管理处登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def office_client(api_client: APIClient) -> APIClient:
    """已登录的办公室客户端"""
    resp = api_client.login(test_config.office.username, test_config.office.password)
    assert resp.get("code") == 200, f"办公室登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def leader_client(api_client: APIClient) -> APIClient:
    """已登录的局领导客户端"""
    resp = api_client.login(test_config.leader.username, test_config.leader.password)
    assert resp.get("code") == 200, f"局领导登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def finance_client(api_client: APIClient) -> APIClient:
    """已登录的财务处客户端"""
    resp = api_client.login(test_config.finance.username, test_config.finance.password)
    assert resp.get("code") == 200, f"财务处登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def tech_client(api_client: APIClient) -> APIClient:
    """已登录的科技处客户端"""
    resp = api_client.login(test_config.tech.username, test_config.tech.password)
    assert resp.get("code") == 200, f"科技处登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def unit_client(api_client: APIClient) -> APIClient:
    """已登录的中层单位客户端"""
    resp = api_client.login(test_config.unit_user.username, test_config.unit_user.password)
    assert resp.get("code") == 200, f"中层单位登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def sub_unit_client(api_client: APIClient) -> APIClient:
    """已登录的基层单位客户端"""
    resp = api_client.login(test_config.sub_unit_user.username, test_config.sub_unit_user.password)
    assert resp.get("code") == 200, f"基层单位登录失败: {resp}"
    return api_client