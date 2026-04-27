# -*- coding: utf-8 -*-
"""
pytest 全局配置与 fixtures
"""
import pytest
import requests
from typing import Dict, Optional
from tests.common.api_client import APIClient
from tests.common.config import test_config


@pytest.fixture(scope="session")
def base_url() -> str:
    """API 基础URL"""
    return "http://127.0.0.1:8000"


@pytest.fixture(scope="function")
def api_client(base_url: str) -> APIClient:
    """API 客户端 fixture"""
    client = APIClient(base_url=base_url)
    return client


@pytest.fixture(scope="function")
def admin_token(api_client: APIClient) -> str:
    """管理员登录 token"""
    cfg = test_config.admin
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"管理员登录失败: {resp}"
    return api_client.token


@pytest.fixture(scope="function")
def admin_client(api_client: APIClient, admin_token: str) -> APIClient:
    """已登录管理员的 API 客户端"""
    api_client.token = admin_token
    api_client.current_user = {"user_id": test_config.admin.user_id}
    return api_client


@pytest.fixture(scope="function")
def leader_token(api_client: APIClient) -> str:
    """局领导登录 token"""
    cfg = test_config.leader
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"局领导登录失败: {resp}"
    return api_client.token


@pytest.fixture(scope="function")
def leader_client(api_client: APIClient, leader_token: str) -> APIClient:
    """已登录局领导的 API 客户端"""
    api_client.token = leader_token
    api_client.current_user = {"user_id": test_config.leader.user_id}
    return api_client


@pytest.fixture(scope="function")
def normal_client(api_client: APIClient) -> APIClient:
    """已登录普通用户的 API 客户端"""
    cfg = test_config.normal
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"普通用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def asset_mgr_client(api_client: APIClient) -> APIClient:
    """已登录资产处用户的 API 客户端"""
    cfg = test_config.asset_manager
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"资产处用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def office_client(api_client: APIClient) -> APIClient:
    """已登录办公室用户的 API 客户端"""
    cfg = test_config.office
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"办公室用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def hr_client(api_client: APIClient) -> APIClient:
    """已登录劳动人事处用户的 API 客户端"""
    cfg = test_config.hr
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"劳动人事处用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def tech_client(api_client: APIClient) -> APIClient:
    """已登录科技处用户的 API 客户端"""
    cfg = test_config.tech
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"科技处用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def finance_client(api_client: APIClient) -> APIClient:
    """已登录财务处用户的 API 客户端"""
    cfg = test_config.finance
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"财务处用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def unit_client(api_client: APIClient) -> APIClient:
    """已登录中层单位用户的 API 客户端"""
    cfg = test_config.unit_user
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"中层单位用户登录失败: {resp}"
    return api_client


@pytest.fixture(scope="function")
def sub_unit_client(api_client: APIClient) -> APIClient:
    """已登录基层单位用户的 API 客户端"""
    cfg = test_config.sub_unit_user
    resp = api_client.login(cfg.username, cfg.password)
    assert api_client.token is not None, f"基层单位用户登录失败: {resp}"
    return api_client