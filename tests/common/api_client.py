# -*- coding: utf-8 -*-
"""
API 客户端封装
提供统一的 HTTP 请求方法和会话管理
"""
import requests
from typing import Optional, Dict, Any, List
from tests.common.constants import HTTPStatus, API


class APIClientError(Exception):
    """API 客户端异常"""
    pass


class APIClient:
    """API 客户端"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self.token: Optional[str] = None
        self.current_user: Optional[Dict] = None

    def _get_headers(self) -> Dict:
        """获取请求头（包含 token）"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法 (GET/POST/PUT/DELETE)
            url: API 路径 (如 /api/auth/login)
            **kwargs: 传递给 requests 的额外参数

        Returns:
            解析后的 JSON 响应字典
        """
        full_url = self.base_url + url
        headers = self._get_headers()

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        timeout = kwargs.pop("timeout", 10)

        response = self.session.request(
            method=method,
            url=full_url,
            headers=headers,
            timeout=timeout,
            **kwargs
        )

        try:
            data = response.json()
        except (ValueError, requests.JSONDecodeError):
            data = {
                "code": response.status_code,
                "message": response.text,
                "data": None
            }

        if "code" not in data:
            data["code"] = response.status_code

        data["_status_code"] = response.status_code
        return data

    def get(self, url: str, params: Optional[Dict] = None) -> Dict:
        """发送 GET 请求"""
        return self.request("GET", url, params=params)

    def post(self, url: str, json: Optional[Dict] = None) -> Dict:
        """发送 POST 请求"""
        return self.request("POST", url, json=json or {})

    def put(self, url: str, json: Optional[Dict] = None) -> Dict:
        """发送 PUT 请求"""
        return self.request("PUT", url, json=json or {})

    def delete(self, url: str) -> Dict:
        """发送 DELETE 请求"""
        return self.request("DELETE", url)

    # ============================================================
    # 认证方法
    # ============================================================
    def login(self, username: str, password: str) -> Dict:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            响应数据，包含 { code, message, data: { user_id, ... } }
        """
        result = self.post(API.AUTH_LOGIN, json={
            "username": username,
            "password": password,
        })

        if result.get("code") == 200:
            data = result.get("data", {})
            self.token = str(data.get("user_id", ""))
            self.current_user = data

        return result

    def login_as(self, role: str) -> Dict:
        """
        使用角色名登录（需要在 config 中配置）

        Args:
            role: 角色名

        Returns:
            登录响应
        """
        from tests.common.config import test_config
        user_cfg = test_config.get_user_by_role(role)
        if not user_cfg:
            raise APIClientError(f"未找到角色 {role} 的测试用户配置")

        return self.login(user_cfg.username, user_cfg.password)

    def logout(self, user_id: int) -> Dict:
        """用户登出"""
        result = self.post(API.AUTH_LOGOUT, json={"user_id": user_id})
        if result.get("code") == 200:
            self.token = None
            self.current_user = None
        return result

    def change_password(self, user_id: int, old_pwd: str, new_pwd: str) -> Dict:
        """修改密码"""
        return self.put(API.AUTH_PASSWORD, json={
            "user_id": user_id,
            "old_password": old_pwd,
            "new_password": new_pwd,
        })

    def check_permission(self, user_id: int, required_role: str) -> Dict:
        """检查权限"""
        return self.get(API.AUTH_PERMISSION, params={
            "user_id": user_id,
            "required_role": required_role,
        })

    def approve_password_change(self, user_id: int, hr_id: int, comment: str = "") -> Dict:
        """劳动人事处审批密码修改"""
        return self.post(API.AUTH_PASSWORD_APPROVE.format(user_id=user_id), json={
            "hr_id": hr_id,
            "comment": comment,
        })

    def request_password_change(self, user_id: int, old_pwd: str, new_pwd: str, reason: str = "") -> Dict:
        """用户申请修改密码"""
        return self.post("/api/auth/password/request", json={
            "user_id": user_id,
            "old_password": old_pwd,
            "new_password": new_pwd,
            "reason": reason,
        })

    # ============================================================
    # 用户管理
    # ============================================================
    def get_users(self, page: int = 1, page_size: int = 20, **params) -> Dict:
        """获取用户列表"""
        return self.get(API.USERS, params={"page": page, "page_size": page_size, **params})

    def get_user(self, user_id: int) -> Dict:
        """获取用户详情"""
        return self.get(API.USER_DETAIL.format(user_id=user_id))

    def create_user(self, username: str, password: str, role: str,
                    org_id: int, full_name: str, position: str = "") -> Dict:
        """创建用户"""
        return self.post(API.USERS, json={
            "username": username, "password": password, "role": role,
            "organization_id": org_id, "full_name": full_name, "position": position,
        })

    def update_user(self, user_id: int, **data) -> Dict:
        """更新用户"""
        return self.put(API.USER_DETAIL.format(user_id=user_id), json=data)

    def delete_user(self, user_id: int) -> Dict:
        """删除用户"""
        return self.delete(API.USER_DETAIL.format(user_id=user_id))

    def reset_user_password(self, user_id: int, new_password: str) -> Dict:
        """管理员重置用户密码"""
        return self.put(API.USER_PASSWORD.format(user_id=user_id), json={"password": new_password})


    # ============================================================
    # 组织管理
    # ============================================================
    def get_organizations(self, parent_id: Optional[int] = None,
                          page: int = 1, page_size: int = 20) -> Dict:
        """获取组织列表"""
        params = {"page": page, "page_size": page_size}
        if parent_id is not None:
            params["parent_id"] = parent_id
        return self.get(API.ORGANIZATIONS, params=params)

    def get_organization(self, org_id: int) -> Dict:
        """获取组织详情"""
        return self.get(API.ORG_DETAIL.format(org_id=org_id))

    def get_org_tree(self) -> Dict:
        """获取组织架构树"""
        return self.get(API.ORG_TREE)

    def get_departments(self) -> Dict:
        """获取机关处室列表"""
        return self.get(API.ORG_DEPARTMENTS)

    def get_units(self) -> Dict:
        """获取中层单位列表"""
        return self.get(API.ORG_UNITS)

    def get_sub_units(self, parent_id: int) -> Dict:
        """获取基层单位列表"""
        return self.get(API.ORG_SUB_UNITS.format(parent_id=parent_id))

    def get_org_users(self, org_id: int) -> Dict:
        """获取组织下的用户"""
        return self.get(API.ORG_USERS.format(org_id=org_id))

    def get_org_assets_stats(self, org_id: int) -> Dict:
        """获取组织资产统计"""
        return self.get(API.ORG_ASSETS.format(org_id=org_id))

    def get_org_path(self, org_id: int) -> Dict:
        """获取组织路径"""
        return self.get(API.ORG_PATH.format(org_id=org_id))

    # ============================================================
    # 资产管理
    # ============================================================
    def get_assets(self, page: int = 1, page_size: int = 20, **params) -> Dict:
        """获取资产列表"""
        return self.get(API.ASSETS, params={"page": page, "page_size": page_size, **params})

    def get_asset(self, asset_id: int) -> Dict:
        """获取资产详情"""
        return self.get(API.ASSET_DETAIL.format(asset_id=asset_id))

    def create_asset(self, **data) -> Dict:
        """创建资产"""
        return self.post(API.ASSETS, json=data)

    def update_asset(self, asset_id: int, **data) -> Dict:
        """更新资产"""
        return self.put(API.ASSET_DETAIL.format(asset_id=asset_id), json=data)

    def delete_asset(self, asset_id: int) -> Dict:
        """删除资产"""
        return self.delete(API.ASSET_DETAIL.format(asset_id=asset_id))

    def get_asset_statistics(self) -> Dict:
        """获取资产统计"""
        return self.get(API.ASSET_STATISTICS)

    def apply_for_asset(self, asset_id: int, **data) -> Dict:
        """申请资产"""
        return self.post(API.ASSET_APPLY.format(asset_id=asset_id), json=data)

    def get_asset_applications(self, page: int = 1, page_size: int = 20, **params) -> Dict:
        """获取资产申请列表"""
        return self.get(API.ASSET_APPLICATIONS,
                        params={"page": page, "page_size": page_size, **params})

    def approve_asset_application(self, app_id: int, **data) -> Dict:
        """审批通过资产申请"""
        return self.post(API.ASSET_APPROVE.format(app_id=app_id), json=data)

    def reject_asset_application(self, app_id: int, **data) -> Dict:
        """拒绝资产申请"""
        return self.post(API.ASSET_REJECT.format(app_id=app_id), json=data)

    def get_my_asset_applications(self) -> Dict:
        """获取我的资产申请"""
        return self.get(API.ASSET_MY_APPLICATIONS)

    def get_org_assets(self, org_id: int) -> Dict:
        """获取组织资产"""
        return self.get(API.ASSET_ORG_ASSETS.format(org_id=org_id))

    def get_sub_orgs_assets(self) -> Dict:
        """获取下级单位资产"""
        return self.get(API.ASSET_SUB_ORGS)

    def get_asset_level_stats(self) -> Dict:
        """获取分层级资产统计"""
        return self.get(API.ASSET_LEVEL_STATS)

    # ============================================================
    # 预算管理
    # ============================================================
    def get_budgets(self, page: int = 1, page_size: int = 20, **params) -> Dict:
        """获取预算列表"""
        return self.get(API.BUDGETS, params={"page": page, "page_size": page_size, **params})

    def get_budget(self, budget_id: int) -> Dict:
        """获取预算详情"""
        return self.get(API.BUDGET_DETAIL.format(budget_id=budget_id))

    def create_budget(self, **data) -> Dict:
        """创建预算"""
        return self.post(API.BUDGETS, json=data)

    def update_budget(self, budget_id: int, **data) -> Dict:
        """更新预算"""
        return self.put(API.BUDGET_DETAIL.format(budget_id=budget_id), json=data)

    def delete_budget(self, budget_id: int) -> Dict:
        """删除预算"""
        return self.delete(API.BUDGET_DETAIL.format(budget_id=budget_id))

    def apply_budget(self, budget_id: int, **data) -> Dict:
        """预算申报"""
        return self.post(API.BUDGET_APPLY.format(budget_id=budget_id), json=data)

    def get_budget_applications(self, page: int = 1, page_size: int = 20, **params) -> Dict:
        """获取预算申报列表"""
        return self.get(API.BUDGET_APPLICATIONS,
                        params={"page": page, "page_size": page_size, **params})

    def approve_budget_application(self, app_id: int, **data) -> Dict:
        """审批通过预算"""
        return self.post(API.BUDGET_APPROVE.format(app_id=app_id), json=data)

    def reject_budget_application(self, app_id: int, **data) -> Dict:
        """拒绝预算"""
        return self.post(API.BUDGET_REJECT.format(app_id=app_id), json=data)

    def get_budget_statistics(self) -> Dict:
        """获取预算统计"""
        return self.get(API.BUDGET_STATISTICS)

    def get_my_budget_applications(self) -> Dict:
        """获取我的预算申报"""
        return self.get(API.BUDGET_MY_APPLICATIONS)

    # ============================================================
    # 公文管理
    # ============================================================
    def get_documents(self, page: int = 1, page_size: int = 20, **params) -> Dict:
        """获取公文列表"""
        return self.get(API.DOCUMENTS, params={"page": page, "page_size": page_size, **params})

    def get_document(self, doc_id: int) -> Dict:
        """获取公文详情"""
        return self.get(API.DOCUMENT_DETAIL.format(doc_id=doc_id))

    def create_document(self, **data) -> Dict:
        """创建公文"""
        return self.post(API.DOCUMENTS, json=data)

    def update_document(self, doc_id: int, **data) -> Dict:
        """更新公文"""
        return self.put(API.DOCUMENT_DETAIL.format(doc_id=doc_id), json=data)

    def delete_document(self, doc_id: int) -> Dict:
        """删除公文"""
        return self.delete(API.DOCUMENT_DETAIL.format(doc_id=doc_id))

    def submit_document(self, doc_id: int, **data) -> Dict:
        """提交公文"""
        return self.post(API.DOCUMENT_SUBMIT.format(doc_id=doc_id), json=data)

    def approve_document(self, doc_id: int, **data) -> Dict:
        """审批通过公文"""
        return self.post(API.DOCUMENT_APPROVE.format(doc_id=doc_id), json=data)

    def reject_document(self, doc_id: int, **data) -> Dict:
        """拒绝公文"""
        return self.post(API.DOCUMENT_REJECT.format(doc_id=doc_id), json=data)

    def distribute_document(self, doc_id: int, **data) -> Dict:
        """下达公文"""
        return self.post(API.DOCUMENT_DISTRIBUTE.format(doc_id=doc_id), json=data)

    def get_my_documents(self) -> Dict:
        """获取我的公文"""
        return self.get(API.DOCUMENT_MY_DOCUMENTS)

    def get_received_documents(self) -> Dict:
        """获取收到的公文"""
        return self.get(API.DOCUMENT_RECEIVED)

    def get_same_level_documents(self) -> Dict:
        """获取同级函件"""
        return self.get(API.DOCUMENT_SAME_LEVEL)

    # ============================================================
    # 消息管理
    # ============================================================
    def get_messages(self, page: int = 1, page_size: int = 20) -> Dict:
        """获取消息列表"""
        return self.get(API.MESSAGES, params={"page": page, "page_size": page_size})

    def get_message(self, msg_id: int) -> Dict:
        """获取消息详情"""
        return self.get(API.MESSAGE_DETAIL.format(msg_id=msg_id))

    def send_message(self, **data) -> Dict:
        """发送消息"""
        return self.post(API.MESSAGES, json=data)

    def delete_message(self, msg_id: int) -> Dict:
        """删除消息"""
        return self.delete(API.MESSAGE_DETAIL.format(msg_id=msg_id))

    def get_inbox(self) -> Dict:
        """获取收件箱"""
        return self.get(API.MESSAGE_INBOX)

    def get_sent_messages(self) -> Dict:
        """获取已发送消息"""
        return self.get(API.MESSAGE_SENT)

    def get_unread_count(self) -> Dict:
        """获取未读消息数"""
        return self.get(API.MESSAGE_UNREAD_COUNT)

    def mark_message_read(self, msg_id: int) -> Dict:
        """标记消息已读"""
        body = {"user_id": self.current_user.get("user_id")} if self.current_user else {}
        return self.put(API.MESSAGE_READ.format(msg_id=msg_id), json=body)

    def broadcast_message(self, **data) -> Dict:
        """广播消息"""
        return self.post(API.MESSAGE_BROADCAST, json=data)

    def send_business_notice(self, **data) -> Dict:
        """发送业务通知"""
        return self.post(API.MESSAGE_BUSINESS_NOTICE, json=data)