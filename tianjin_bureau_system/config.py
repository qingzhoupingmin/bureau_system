# -*- coding: utf-8 -*-
"""
天津市市政工程局综合管理系统 - 配置文件
"""

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Oppor831t',
    'database': 'tianjin_bureau',
    'charset': 'utf8mb4'
}

# 系统配置
SYSTEM_NAME = '天津市市政工程局综合管理系统'
SYSTEM_VERSION = '1.0.0'

# 角色定义
ROLE_ADMIN = 'system_admin'
ROLE_LEADER = 'leader'
ROLE_ASSET_MANAGER = 'asset_manager'
ROLE_OFFICE_STAFF = 'office_staff'
ROLE_TECH_STAFF = 'tech_staff'
ROLE_FINANCE_STAFF = 'finance_staff'
ROLE_UNIT_USER = 'unit_user'
ROLE_SUB_UNIT_USER = 'sub_unit_user'  # 下属单位下属的用户（如道桥处下属单位）
ROLE_NORMAL_USER = 'normal_user'

# 资产状态
ASSET_STATUS_NORMAL = 'normal'
ASSET_STATUS_IN_USE = 'in_use'
ASSET_STATUS_BORROWED = 'borrowed'
ASSET_STATUS_MAINTENANCE = 'maintenance'
ASSET_STATUS_SCRAPPED = 'scrapped'

# 申请状态
APPLY_STATUS_PENDING = 'pending'
APPLY_STATUS_APPROVED = 'approved'
APPLY_STATUS_REJECTED = 'rejected'

# 公文状态
DOC_STATUS_DRAFT = 'draft'
DOC_STATUS_PENDING = 'pending'
DOC_STATUS_PUBLISHED = 'published'
DOC_STATUS_REPLIED = 'replied'

# 消息类型
MSG_TYPE_OFFICIAL = 'official'      # 局名义通知
MSG_TYPE_BUSINESS = 'business'       # 业务通知
MSG_TYPE_REQUEST = 'request'         # 业务请示

# 组织类型
ORG_TYPE_DEPARTMENT = 'department'   # 机关处室
ORG_TYPE_UNIT = 'unit'               # 下属单位
ORG_TYPE_SUB_UNIT = 'sub_unit'       # 下属单位的下属单位（道桥处下属单位）
ORG_TYPE_LEADER = 'leader'           # 领导职务

# 处室ID映射
DEPARTMENTS = {
    1: '办公室',
    2: '计划处',
    3: '设施管理处',
    4: '设施养护处',
    5: '建设管理处',
    6: '规划处',
    7: '财务处',
    8: '规费管理处',
    9: '审计处',
    10: '资产管理处',
    11: '劳动人事处',
    12: '科技处',
    13: '安全保卫处',
    14: '法规处',
    15: '党委办公室',
    16: '纪检委',
    17: '宣传部',
    18: '组织部',
    19: '老干部处'
}

# 资产类别
ASSET_CATEGORIES = {
    'device': '办公设备',
    'furniture': '办公家具',
    'public': '公用设备',
    'consumable': '消耗品'
}

# 下属单位全称（包含括号）
UNITS = {
    21: '天津市公路处',
    22: '天津市高速公路管理处',
    23: '天津市道路桥梁管理处',
    26: '天津市市政工程研究院',
    27: '天津市市政工程设计研究院',
    31: '天津市市政工程建设公司',
    38: '天津市地铁管理处',
    39: '天津市市政公路巡查管理处',
    41: '天津市公路治理车辆超限超载管理办公室',
    42: '天津市公路养护工程处',
}

# 道路桥梁管理处下属单位（ID 51-60）
SUB_UNITS_BRIDGE = {
    51: '第一桥梁管理所',
    52: '第二桥梁管理所',
    53: '第一道路管理所',
    54: '第二道路管理所',
    55: '第一快速路管理所',
    56: '第二快速路管理所',
    57: '拌合厂',
    58: '机修厂',
    59: '天津市占路监理所',
    60: '通达广告部',
}

# 公路处下属单位（ID 81-90）
SUB_UNITS_HIGHWAY = {
    81: '第一公路管理所',
    82: '第二公路管理所',
    83: '第三公路管理所',
    84: '第四公路管理所',
    85: '外环公路管理所',
    86: '天津市蓟县路政管理所',
    87: '天津市宝坻路政管理所',
    88: '天津市武清路政管理所',
    89: '天津市静海路政管理所',
    90: '天津市宁河路政管理所',
}

# 高速公路管理处下属单位（ID 61-72）
SUB_UNITS_HIGHWAY_EXPRESS = {
    61: '天津市高速公路电子收费管理中心',
    64: '天津市京津塘高速路政大队',
    65: '天津市津滨高速路政大队',
    66: '天津市津沧高速路政大队',
    67: '天津市唐津高速路政大队',
    68: '监控中心',
    69: '第一养护管理所',
    70: '第二养护管理所',
    71: '第三养护管理所',
    72: '第四养护管理所',
}

# 市政工程研究院下属单位（ID 73-79）
SUB_UNITS_RESEARCH = {
    73: '工程质量检测中心',
    74: '路桥检测中心',
    75: '海顺设计公司',
    76: '建达科技公司',
    77: '路驰监理公司',
    78: '金艾检测中心',
    79: '滨海分院',
}

# 市政工程建设公司下属单位（ID 86-88）
SUB_UNITS_CONSTRUCTION = {
    86: '天津道桥建设发展有限公司',
    87: '天津市政道桥建筑工程公司',
    88: '天津道桥工程公司',
}

# 市政工程设计研究院下属单位（ID 91-99）
SUB_UNITS_DESIGN = {
    62: '天津市市政工程设计研究院城市设计分院',
    91: '天津市给排水设计研究院',
    92: '天津市燃气设计研究院',
    93: '天津市道路桥梁设计研究院',
    94: '天津市市政工程设计研究院重庆分院',
    95: '天津市市政工程设计研究院浙江分院',
    96: '天津市市政工程设计研究院西安分院',
    97: '天津市市政工程设计研究院广州分院',
    98: '天津市市政工程设计研究院滨海新区分院',
}

# 地铁管理处下属单位（ID 63）
SUB_UNITS_METRO = {
    63: '天津市地下铁道总公司',
}

# 公路养护工程处下属单位（ID 101-110）
SUB_UNITS_MAINTENANCE = {
    101: '天津市和平区公路设施养护所',
    102: '天津市河东区公路设施养护所',
    103: '天津市河西区公路设施养护所',
    104: '天津市南开区公路设施养护所',
    105: '天津市河北区公路设施养护所',
    106: '天津市红桥区公路设施养护所',
    107: '天津市东丽区公路设施养护所',
    108: '天津市西青区公路设施养护所',
    109: '天津市津南区公路设施养护所',
    110: '天津市北辰区公路设施养护所',
}