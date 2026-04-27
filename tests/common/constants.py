# -*- coding: utf-8 -*-
"""
测试框架常量定义
"""

# ============================================================
# 角色定义
# ============================================================
class Roles:
    """系统角色常量"""
    SYSTEM_ADMIN = "system_admin"        # 系统管理员
    LEADER = "leader"                     # 局领导
    ASSET_MANAGER = "asset_manager"       # 资产管理处
    OFFICE = "office_staff"               # 办公室
    HR = "hr_staff"                       # 劳动人事处
    TECH = "tech_staff"                   # 科技处
    FINANCE = "finance_staff"             # 财务处
    UNIT_USER = "unit_user"               # 中层单位用户
    SUB_UNIT_USER = "sub_unit_user"       # 基层单位用户
    NORMAL_USER = "normal_user"           # 普通处室用户

    # 所有角色列表
    ALL = [
        SYSTEM_ADMIN, LEADER, ASSET_MANAGER, OFFICE, HR,
        TECH, FINANCE, UNIT_USER, SUB_UNIT_USER, NORMAL_USER
    ]

    # 角色显示名称映射
    LABELS = {
        SYSTEM_ADMIN: "系统管理员",
        LEADER: "局领导",
        ASSET_MANAGER: "资产管理处",
        OFFICE: "办公室",
        HR: "劳动人事处",
        TECH: "科技处",
        FINANCE: "财务处",
        UNIT_USER: "中层单位用户",
        SUB_UNIT_USER: "基层单位用户",
        NORMAL_USER: "普通处室用户",
    }


# ============================================================
# API 路径常量
# ============================================================
class API:
    """API 路径常量"""
    # 认证
    AUTH_LOGIN = "/api/auth/login"
    AUTH_LOGOUT = "/api/auth/logout"
    AUTH_PASSWORD = "/api/auth/password"
    AUTH_PERMISSION = "/api/auth/permission"
    AUTH_PASSWORD_APPROVE = "/api/auth/password/approve"

    # 用户
    USERS = "/api/users"
    USER_DETAIL = "/api/users/{user_id}"
    USER_PASSWORD = "/api/users/{user_id}/password"
    USER_REGISTER = "/api/users/register"

    # 组织
    ORGANIZATIONS = "/api/organizations"
    ORG_DETAIL = "/api/organizations/{org_id}"
    ORG_TREE = "/api/organizations/tree"
    ORG_DEPARTMENTS = "/api/organizations/departments"
    ORG_UNITS = "/api/organizations/units"
    ORG_SUB_UNITS = "/api/organizations/sub-units/{parent_id}"
    ORG_USERS = "/api/organizations/{org_id}/users"
    ORG_ASSETS = "/api/organizations/{org_id}/assets"
    ORG_PATH = "/api/organizations/path/{org_id}"

    # 资产
    ASSETS = "/api/assets"
    ASSET_DETAIL = "/api/assets/{asset_id}"
    ASSET_STATISTICS = "/api/assets/statistics"
    ASSET_APPLY = "/api/assets/{asset_id}/apply"
    ASSET_APPLICATIONS = "/api/assets/applications"
    ASSET_APPROVE = "/api/assets/applications/{app_id}/approve"
    ASSET_REJECT = "/api/assets/applications/{app_id}/reject"
    ASSET_MY_APPLICATIONS = "/api/assets/my-applications"
    ASSET_ORG_ASSETS = "/api/assets/org/{org_id}"
    ASSET_SUB_ORGS = "/api/assets/sub-orgs"
    ASSET_LEVEL_STATS = "/api/assets/level-stats"

    # 预算
    BUDGETS = "/api/budgets"
    BUDGET_DETAIL = "/api/budgets/{budget_id}"
    BUDGET_APPLY = "/api/budgets/{budget_id}/apply"
    BUDGET_APPLICATIONS = "/api/budgets/applications"
    BUDGET_APPROVE = "/api/budgets/applications/{app_id}/approve"
    BUDGET_REJECT = "/api/budgets/applications/{app_id}/reject"
    BUDGET_STATISTICS = "/api/budgets/statistics"
    BUDGET_MY_APPLICATIONS = "/api/budgets/my-applications"
    BUDGET_ORG_BUDGETS = "/api/budgets/org/{org_id}"

    # 公文
    DOCUMENTS = "/api/documents"
    DOCUMENT_DETAIL = "/api/documents/{doc_id}"
    DOCUMENT_SUBMIT = "/api/documents/{doc_id}/submit"
    DOCUMENT_APPROVE = "/api/documents/{doc_id}/approve"
    DOCUMENT_REJECT = "/api/documents/{doc_id}/reject"
    DOCUMENT_DISTRIBUTE = "/api/documents/{doc_id}/distribute"
    DOCUMENT_MY_DOCUMENTS = "/api/documents/my-documents"
    DOCUMENT_RECEIVED = "/api/documents/received"
    DOCUMENT_SAME_LEVEL = "/api/documents/same-level"

    # 消息
    MESSAGES = "/api/messages"
    MESSAGE_DETAIL = "/api/messages/{msg_id}"
    MESSAGE_INBOX = "/api/messages/inbox"
    MESSAGE_SENT = "/api/messages/sent"
    MESSAGE_UNREAD_COUNT = "/api/messages/unread-count"
    MESSAGE_READ = "/api/messages/{msg_id}/read"
    MESSAGE_BROADCAST = "/api/messages/broadcast"
    MESSAGE_BUSINESS_NOTICE = "/api/messages/business-notice"


# ============================================================
# HTTP 状态码
# ============================================================
class HTTPStatus:
    """HTTP 状态码常量"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500


# ============================================================
# API 响应业务状态码
# ============================================================
class BizCode:
    """业务状态码"""
    SUCCESS = 200
    ERROR = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    VALIDATION_ERROR = 422


# ============================================================
# 业务状态常量
# ============================================================
class Status:
    """业务状态常量"""
    # 通用状态
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

    # 资产申请状态
    ASSET_APPLICATION_PENDING = "pending"       # 待审批
    ASSET_APPLICATION_APPROVED = "approved"     # 已通过
    ASSET_APPLICATION_REJECTED = "rejected"     # 已拒绝

    # 预算状态
    BUDGET_DRAFT = "draft"              # 草稿
    BUDGET_SUBMITTED = "submitted"      # 已提交
    BUDGET_APPROVED = "approved"        # 已通过
    BUDGET_REJECTED = "rejected"        # 已拒绝
    BUDGET_ALLOCATED = "allocated"      # 已分配

    # 公文状态
    DOCUMENT_DRAFT = "draft"            # 草稿
    DOCUMENT_SUBMITTED = "submitted"    # 已提交
    DOCUMENT_APPROVED = "approved"      # 已审核通过
    DOCUMENT_REJECTED = "rejected"      # 已拒绝
    DOCUMENT_DISTRIBUTED = "distributed"  # 已下达

    # 消息状态
    MESSAGE_UNREAD = "unread"           # 未读
    MESSAGE_READ = "read"               # 已读

    # 公文类型
    DOC_TYPE_REPORT = "report"          # 汇报
    DOC_TYPE_LETTER = "letter"          # 同级函件
    DOC_TYPE_REQUEST = "request"        # 请示
    DOC_TYPE_NOTICE = "notice"          # 通知


# ============================================================
# 组织层级
# ============================================================
class OrgLevel:
    """组织层级常量"""
    BUREAU = 1          # 局机关（第一级）
    MIDDLE = 2          # 中层单位（第二级）
    BASIC = 3           # 基层单位（第三级）

    LABELS = {
        BUREAU: "局机关",
        MIDDLE: "中层单位",
        BASIC: "基层单位",
    }


# ============================================================
# 测试数据常量
# ============================================================
class TestData:
    """测试数据常量"""
    # 分页
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20
    SMALL_PAGE_SIZE = 5

    # 超时
    DEFAULT_TIMEOUT = 10
    LONG_TIMEOUT = 30

    # 密码
    DEFAULT_PASSWORD = "test123456"
    NEW_PASSWORD = "new_password_123"
    WEAK_PASSWORD = "123"

    # 测试文本
    TEST_NAME = "测试资产"
    TEST_DESCRIPTION = "这是一个测试数据，用于自动化测试"
    TEST_REJECT_REASON = "测试拒绝原因"


# ============================================================
# 权限矩阵定义
# ============================================================
# 功能: [有权角色列表]
PERMISSION_MATRIX = {
    "view_all_assets": [
        Roles.SYSTEM_ADMIN, Roles.LEADER, Roles.ASSET_MANAGER,
    ],
    "asset_statistics": [
        Roles.SYSTEM_ADMIN, Roles.LEADER, Roles.ASSET_MANAGER,
    ],
    "asset_approve": [
        Roles.SYSTEM_ADMIN, Roles.LEADER, Roles.ASSET_MANAGER,
    ],
    "document_approve_distribute": [
        Roles.SYSTEM_ADMIN, Roles.OFFICE,
    ],
    "message_broadcast": [
        Roles.SYSTEM_ADMIN, Roles.OFFICE,
    ],
    "tech_management": [
        Roles.SYSTEM_ADMIN, Roles.TECH,
    ],
    "budget_management": [
        Roles.SYSTEM_ADMIN, Roles.LEADER, Roles.FINANCE,
    ],
    "password_approve": [
        Roles.SYSTEM_ADMIN, Roles.HR,
    ],
    "user_management": [
        Roles.SYSTEM_ADMIN,
    ],
}