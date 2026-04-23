# -*- coding: utf-8 -*-
"""
单位概况模块 - 显示单位职能介绍、内设机构与下属单位
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import DEPARTMENTS, SUB_UNITS_BRIDGE, SUB_UNITS_HIGHWAY, SUB_UNITS_HIGHWAY_EXPRESS, SUB_UNITS_DESIGN, SUB_UNITS_METRO, SUB_UNITS_RESEARCH, SUB_UNITS_CONSTRUCTION


class OrganizationOverview:
    """单位概况管理器"""

    def __init__(self, parent, colors, user=None):
        """初始化"""
        self.parent = parent
        self.COLORS = colors
        self.user = user  # 当前用户信息

        # 处室详细介绍
        self.DEPARTMENT_DETAILS = {
            1: {
                'name': '办公室',
                'functions': [
                    '负责局机关日常运转和综合协调工作',
                    '负责公文处理、文秘档案、印章管理',
                    '负责信访接待、外事管理、后勤保障',
                    '负责重要会议组织和决议事项督办',
                    '负责政务信息公开和新闻宣传工作'
                ],
                'responsibilities': '综合协调、文秘档案、信访接待、后勤保障、政务公开'
            },
            2: {
                'name': '计划处',
                'functions': [
                    '负责编制市政工程年度投资计划',
                    '负责项目立项审批和投资管理',
                    '负责市政工程统计分析和预测',
                    '负责重大项目前期工作协调',
                    '负责行业发展规划编制'
                ],
                'responsibilities': '计划编制、项目立项、投资管理、统计分析'
            },
            3: {
                'name': '设施管理处',
                'functions': [
                    '负责市政设施维护计划制定',
                    '负责设施台账管理和档案建立',
                    '负责设施巡查和状况评估',
                    '负责设施改造和大修项目管理',
                    '负责设施技术标准和规范制定'
                ],
                'responsibilities': '设施维护、台账管理、巡查评估、技术改造'
            },
            4: {
                'name': '设施养护处',
                'functions': [
                    '负责市政道路桥梁养护管理',
                    '负责养护作业质量和安全监督',
                    '负责养护工程验收和评价',
                    '负责养护机械设备管理',
                    '负责养护技术创新和推广'
                ],
                'responsibilities': '养护管理、质量监督、设备管理、技术创新'
            },
            5: {
                'name': '建设管理处',
                'functions': [
                    '负责市政工程建设项目管理',
                    '负责工程招标投标监管',
                    '负责工程质量安全监督',
                    '负责工程进度和投资控制',
                    '负责工程竣工验收和移交'
                ],
                'responsibilities': '项目管理、招标监管、质量安全、进度控制'
            },
            6: {
                'name': '规划处',
                'functions': [
                    '负责市政基础设施总体规划',
                    '负责城市道路交通规划',
                    '负责市政工程规划审批',
                    '负责规划实施监督评估',
                    '负责规划信息管理'
                ],
                'responsibilities': '规划编制、规划审批、规划监督、信息管理'
            },
            7: {
                'name': '财务处',
                'functions': [
                    '负责部门预算编制和执行',
                    '负责经费核算和财务管理',
                    '负责资金使用监督',
                    '负责政府采购管理',
                    '负责财务报告和统计分析'
                ],
                'responsibilities': '预算管理、经费核算、资金监督、政府采购'
            },
            8: {
                'name': '规费管理处',
                'functions': [
                    '负责公路养路费征收管理',
                    '负责通行费征收监管',
                    '负责规费政策制定执行',
                    '负责规费统计分析',
                    '负责规费减免审批'
                ],
                'responsibilities': '规费征收、政策执行、统计分析、减免审批'
            },
            9: {
                'name': '审计处',
                'functions': [
                    '负责内部审计工作',
                    '负责工程审计和决算审计',
                    '负责经济责任审计',
                    '负责财务收支审计',
                    '负责审计问题整改落实'
                ],
                'responsibilities': '内部审计、工程审计、经济责任审计、整改落实'
            },
            10: {
                'name': '资产管理处',
                'functions': [
                    '负责固定资产配置管理',
                    '负责资产清查和登记',
                    '负责资产处置审批',
                    '负责资产收益管理',
                    '负责资产信息系统建设'
                ],
                'responsibilities': '资产配置、清查登记、处置审批、收益管理'
            },
            11: {
                'name': '劳动人事处',
                'functions': [
                    '负责人员编制和人事管理',
                    '负责干部选拔任用',
                    '负责工资福利管理',
                    '负责职称评审和考核',
                    '负责教育培训管理'
                ],
                'responsibilities': '人事管理、干部管理、工资福利、职称评审'
            },
            12: {
                'name': '科技处',
                'functions': [
                    '负责科技创新项目管理',
                    '负责科技成果推广',
                    '负责技术标准制定',
                    '负责信息化建设和维护',
                    '负责技术培训交流'
                ],
                'responsibilities': '科技创新、成果推广、标准制定、信息化建设'
            },
            13: {
                'name': '安全保卫处',
                'functions': [
                    '负责安全生产监督管理',
                    '负责安全检查和隐患排查',
                    '负责安全事故调查处理',
                    '负责应急管理和预案制定',
                    '负责治安保卫工作'
                ],
                'responsibilities': '安全监督、检查排查、事故处理、应急管理'
            },
            14: {
                'name': '法规处',
                'functions': [
                    '负责法规政策制定和审查',
                    '负责普法宣传教育',
                    '负责行政复议和诉讼',
                    '负责执法监督指导',
                    '负责合同审核管理'
                ],
                'responsibilities': '法规制定、普法宣传、复议诉讼、执法监督'
            },
            15: {
                'name': '党委办公室',
                'functions': [
                    '负责党委日常事务',
                    '负责重要会议组织',
                    '负责党务公文处理',
                    '负责党委决策督办',
                    '负责党建管理工作'
                ],
                'responsibilities': '党委事务、会议组织、党务管理、党建管理'
            },
            16: {
                'name': '纪检委',
                'functions': [
                    '负责党风廉政建设',
                    '负责纪律检查和监督',
                    '负责违纪案件查处',
                    '负责反腐倡廉教育',
                    '负责效能监察'
                ],
                'responsibilities': '党风廉政建设、纪律检查、案件查处、反腐倡廉'
            },
            17: {
                'name': '宣传部',
                'functions': [
                    '负责理论学习和宣传教育',
                    '负责新闻宣传和舆论引导',
                    '负责精神文明建设',
                    '负责思想政治工作',
                    '负责文化阵地建设'
                ],
                'responsibilities': '宣传教育、新闻宣传、精神文明、思想工作'
            },
            18: {
                'name': '组织部',
                'functions': [
                    '负责党的组织建设',
                    '负责党员发展教育管理',
                    '负责基层党组织建设',
                    '负责组织制度建设',
                    '负责党费收缴管理'
                ],
                'responsibilities': '组织建设、党员管理、基层建设、制度建设'
            },
            19: {
                'name': '老干部处',
                'functions': [
                    '负责离休干部服务管理',
                    '负责退休干部服务管理',
                    '负责老干部活动组织',
                    '负责老干部待遇落实',
                    '负责老干部慰问走访'
                ],
                'responsibilities': '离休服务、退休管理、活动组织、待遇落实'
            }
        }

        # 下属单位详细介绍
        self.UNIT_DETAILS = {
            21: {
                'name': '天津市公路处',
                'functions': [
                    '负责国省干线公路建设养护',
                    '负责公路路政管理',
                    '负责公路应急抢险',
                    '负责公路技术管理',
                    '负责公路统计信息'
                ],
                'responsibilities': '公路建设、养护管理、路政管理、应急抢险',
                'sub_units': {
                    81: '第一公路管理所',
                    82: '第二公路管理所',
                    83: '第三公路管理所',
                    84: '第四公路管理所',
                    85: '外环公路管理所',
                },
                'sub_unit_desc': '负责国省干线公路管理'
            },
            22: {
                'name': '天津市高速公路管理处',
                'functions': [
                    '负责高速公路运营管理',
                    '负责高速公路养护监管',
                    '负责高速公路服务区管理',
                    '负责高速公路应急处置',
                    '负责高速公路收费监管'
                ],
                'responsibilities': '高速运营、养护监管、服务区管理、应急处置',
                'sub_units': {
                    61: '天津市高速公路电子收费管理中心',
                    64: '第一路政支队',
                    65: '第二路政支队',
                    66: '第三路政支队',
                    67: '第四路政支队',
                    68: '监控中心',
                    69: '第一养护管理所',
                    70: '第二养护管理所',
                    71: '第三养护管理所',
                    72: '第四养护管理所',
                },
                'sub_unit_desc': '实行分所管理模式，下设多个路政和养护单位'
            },
            23: {
                'name': '天津市道路桥梁管理处',
                'functions': [
                    '负责城市道路桥梁管理',
                    '负责桥梁检测评估',
                    '负责桥梁维修加固',
                    '负责桥梁档案管理',
                    '负责桥梁安全监测'
                ],
                'responsibilities': '道路桥梁管理、检测评估、维修加固、安全监测',
                'sub_units': {
                    51: '第一桥梁管理所',
                    52: '第二桥梁管理所',
                    53: '第一道路管理所',
                    54: '第二道路管理所',
                    55: '第一快速路管理所',
                    56: '第二快速路管理所',
                    57: '拌合厂',
                    58: '机修厂',
                    59: '天津市占路监理所',
                    60: '通达广告部'
                },
                'sub_unit_desc': '实行分所管理模式，下设多个基层管理和技术单位'
            },
            24: {
                'name': '天津市市政工程经济技术定额研究站（天津市公路工程定额管理站）',
                'functions': [
                    '负责定额标准研究编制',
                    '负责工程造价管理',
                    '负责经济技术分析',
                    '负责定额信息发布',
                    '负责造价咨询服务'
                ],
                'responsibilities': '定额研究、造价管理、经济分析、咨询服务'
            },
            25: {
                'name': '天津市市政工程配套办公室',
                'functions': [
                    '负责市政配套工程管理',
                    '负责配套工程协调',
                    '负责配套工程验收',
                    '负责配套档案管理',
                    '负责配套技术服务'
                ],
                'responsibilities': '配套工程管理、协调验收、档案管理、技术服务'
            },
            26: {
                'name': '天津市市政工程研究院（天津市公路工程研究院）',
                'functions': [
                    '负责市政工程技术研究',
                    '负责工程质量检测',
                    '负责技术咨询服务',
                    '负责新材料新技术研发',
                    '负责科研成果转化'
                ],
                'responsibilities': '技术研究、质量检测、咨询服务、成果转化',
                'sub_units': {
                    73: '工程质量检测中心',
                    74: '路桥检测中心',
                    75: '海顺设计公司',
                    76: '建达科技公司',
                    77: '路驰监理公司',
                    78: '金艾检测中心',
                    79: '滨海分院',
                },
                'sub_unit_desc': '负责工程质量检测和技术服务'
            },
            27: {
                'name': '天津市市政工程设计研究院',
                'functions': [
                    '负责市政工程设计',
                    '负责设计技术咨询',
                    '负责设计审查',
                    '负责设计标准制定',
                    '负责设计技术创新'
                ],
                'responsibilities': '工程设计、技术咨询、设计审查、标准制定',
                'sub_units': {
                    62: '天津市市政工程设计研究院城市设计分院',
                },
                'sub_unit_desc': '负责城市设计研究'
            },
            28: {
                'name': '天津市市政工程学校',
                'functions': [
                    '负责专业技术人才培养',
                    '负责在职人员培训',
                    '负责技能鉴定',
                    '负责教学研究',
                    '负责实训基地建设'
                ],
                'responsibilities': '人才培养、在职培训、技能鉴定、教学研究'
            },
            29: {
                'name': '天津市市政公路管理局干部中等专业学校（中国共产党天津市市政公路管理局委员会党校）',
                'functions': [
                    '负责干部教育培训',
                    '负责党校教学管理',
                    '负责理论研究',
                    '负责党员教育',
                    '负责培训基地建设'
                ],
                'responsibilities': '干部培训、党校教学、理论研究、党员教育'
            },
            30: {
                'name': '天津市市政公路管理局技工学校',
                'functions': [
                    '负责技工教育培训',
                    '负责职业技能鉴定',
                    '负责实训教学',
                    '负责校企合作',
                    '负责就业指导'
                ],
                'responsibilities': '技工教育、技能鉴定、实训教学、校企合作'
            },
            31: {
                'name': '天津市市政工程建设公司（天津市市政公路利用世界银行贷款办公室）',
                'functions': [
                    '负责市政工程建设施工',
                    '负责工程施工管理',
                    '负责施工安全管理',
                    '负责施工质量控制',
                    '负责施工技术创新'
                ],
                'responsibilities': '建设施工、施工管理、安全质量、技术创新',
                'sub_units': {
                    86: '天津道桥建设发展有限公司',
                    87: '天津市政道桥建筑工程公司',
                    88: '天津道桥工程公司',
                },
                'sub_unit_desc': '负责市政道桥工程建设'
            },
            32: {
                'name': '天津市贷款道路建设车辆通行费征收办公室',
                'functions': [
                    '负责通行费征收管理',
                    '负责收费站点管理',
                    '负责收费票据管理',
                    '负责收费稽查',
                    '负责收费统计分析'
                ],
                'responsibilities': '通行费征收、站点管理、票据管理、收费稽查'
            },
            33: {
                'name': '天津市贷款道路建设车辆通行费稽查管理处',
                'functions': [
                    '负责收费稽查执法',
                    '负责违规处理',
                    '负责收费监督检查',
                    '负责投诉处理',
                    '负责稽查统计分析'
                ],
                'responsibilities': '稽查执法、违规处理、监督检查、投诉处理'
            },
            34: {
                'name': '天津市公路养路费征稽处',
                'functions': [
                    '负责养路费征收',
                    '负责征稽管理',
                    '负责欠费追缴',
                    '负责征稽稽查',
                    '负责征稽统计'
                ],
                'responsibilities': '养路费征收、征稽管理、欠费追缴、征稽稽查'
            },
            35: {
                'name': '天津市公路养护工程处',
                'functions': [
                    '负责公路养护施工',
                    '负责养护工程管理',
                    '负责养护设备管理',
                    '负责养护技术创新',
                    '负责应急抢险施工'
                ],
                'responsibilities': '养护施工、工程管理、设备管理、应急抢险'
            },
            36: {
                'name': '天津市乡村公路管理办公室',
                'functions': [
                    '负责乡村公路管理',
                    '负责乡村公路规划',
                    '负责乡村公路建设',
                    '负责乡村公路养护',
                    '负责乡村公路统计'
                ],
                'responsibilities': '乡村公路管理、规划建设、养护统计'
            },
            37: {
                'name': '天津市市政公路工程质量监督站（天津市公路工程质量安全监督站）',
                'functions': [
                    '负责工程质量监督',
                    '负责质量检测',
                    '负责质量事故处理',
                    '负责质量信息管理',
                    '负责质量培训'
                ],
                'responsibilities': '质量监督、质量检测、事故处理、信息管理'
            },
            38: {
                'name': '天津市地铁管理处',
                'functions': [
                    '负责地铁设施管理',
                    '负责地铁建设协调',
                    '负责地铁运营监管',
                    '负责地铁安全管理',
                    '负责地铁应急协调'
                ],
                'responsibilities': '地铁管理、建设协调、运营监管、安全管理',
                'sub_units': {
                    63: '天津市地下铁道总公司',
                },
                'sub_unit_desc': '负责地铁运营管理'
            },
            39: {
                'name': '天津市市政公路信息中心',
                'functions': [
                    '负责信息系统建设',
                    '负责信息资源管理',
                    '负责网络信息安全',
                    '负责信息技术服务',
                    '负责信息统计分析'
                ],
                'responsibilities': '系统建设、资源管理、信息安全、技术服务'
            },
            40: {
                'name': '天津市市政公路行业管理办公室',
                'functions': [
                    '负责行业管理',
                    '负责行业统计',
                    '负责行业协调',
                    '负责行业服务',
                    '负责行业自律'
                ],
                'responsibilities': '行业管理、行业统计、行业协调、行业服务'
            }
        }

        # 基层单位详细介绍
        self.SUB_UNIT_DETAILS = {
            # 道路桥梁处下属单位（51-60）
            51: {
                'name': '第一桥梁管理所',
                'functions': ['负责桥梁日常巡检维护', '负责桥梁安全检测评估', '负责桥梁病害处理', '负责桥梁档案管理'],
                'responsibilities': '桥梁巡检、安全检测、病害处理、档案管理'
            },
            52: {
                'name': '第二桥梁管理所',
                'functions': ['负责桥梁日常巡检维护', '负责桥梁安全检测评估', '负责桥梁病害处理', '负责桥梁档案管理'],
                'responsibilities': '桥梁巡检、安全检测、病害处理、档案管理'
            },
            53: {
                'name': '第一道路管理所',
                'functions': ['负责道路日常养护管理', '负责道路病害维修', '负责道路排水设施维护', '负责道路应急抢修'],
                'responsibilities': '道路养护、病害维修、排水维护、应急抢修'
            },
            54: {
                'name': '第二道路管理所',
                'functions': ['负责道路日常养护管理', '负责道路病害维修', '负责道路排水设施维护', '负责道路应急抢修'],
                'responsibilities': '道路养护、病害维修、排水维护、应急抢修'
            },
            55: {
                'name': '第一快速路管理所',
                'functions': ['负责快速路日常巡检', '负责快速路养护施工', '负责快速路交通设施维护', '负责快速路应急处置'],
                'responsibilities': '快速路巡检、养护施工、交通设施维护、应急处置'
            },
            56: {
                'name': '第二快速路管理所',
                'functions': ['负责快速路日常巡检', '负责快速路养护施工', '负责快速路交通设施维护', '负责快速路应急处置'],
                'responsibilities': '快速路巡检、养护施工、交通设施维护、应急处置'
            },
            57: {
                'name': '拌合厂',
                'functions': ['负责沥青混凝土生产', '负责路面材料供应', '负责材料质量检测', '负责生产设备管理'],
                'responsibilities': '沥青生产、材料供应、质量检测、设备管理'
            },
            58: {
                'name': '机修厂',
                'functions': ['负责施工机械设备维修', '负责设备配件供应', '负责设备租赁管理', '负责设备技术改造'],
                'responsibilities': '设备维修、配件供应、设备租赁、技术改造'
            },
            59: {
                'name': '天津市占路监理所',
                'functions': ['负责占路施工审批', '负责占路现场监管', '负责恢复质量验收', '负责违规行为查处'],
                'responsibilities': '占路审批、现场监管、质量验收、违规查处'
            },
            60: {
                'name': '通达广告部',
                'functions': ['负责道路广告设置审批', '负责广告设施维护', '负责户外广告管理', '负责广告收益管理'],
                'responsibilities': '广告审批、设施维护、广告管理、收益管理'
            },
            # 高速处下属单位（61-72）
            61: {
                'name': '天津市高速公路电子收费管理中心',
                'functions': ['负责ETC收费系统运营', '负责收费数据分析', '负责收费设备维护', '负责客户服务管理'],
                'responsibilities': '收费运营、数据分析、设备维护、客户服务'
            },
            64: {
                'name': '第一路政支队',
                'functions': ['负责高速公路路政执法', '负责道路安全保护', '负责超限运输治理', '负责事故现场疏导'],
                'responsibilities': '路政执法、安全保护、超限治理、事故疏导'
            },
            65: {
                'name': '第二路政支队',
                'functions': ['负责高速公路路政执法', '负责道路安全保护', '负责超限运输治理', '负责事故现场疏导'],
                'responsibilities': '路政执法、安全保护、超限治理、事故疏导'
            },
            66: {
                'name': '第三路政支队',
                'functions': ['负责高速公路路政执法', '负责道路安全保护', '负责超限运输治理', '负责事故现场疏导'],
                'responsibilities': '路政执法、安全保护、超限治理、事故疏导'
            },
            67: {
                'name': '第四路政支队',
                'functions': ['负责高速公路路政执法', '负责道路安全保护', '负责超限运输治理', '负责事故现场疏导'],
                'responsibilities': '路政执法、安全保护、超限治理、事故疏导'
            },
            68: {
                'name': '监控中心',
                'functions': ['负责高速公路监控调度', '负责信息采集发布', '负责应急指挥协调', '负责数据分析统计'],
                'responsibilities': '监控调度、信息发布、应急指挥、数据分析'
            },
            69: {
                'name': '第一养护管理所',
                'functions': ['负责高速公路日常养护', '负责养护工程质量控制', '负责养护作业安全监督', '负责养护资料管理'],
                'responsibilities': '日常养护、质量控制、安全监督、资料管理'
            },
            70: {
                'name': '第二养护管理所',
                'functions': ['负责高速公路日常养护', '负责养护工程质量控制', '负责养护作业安全监督', '负责养护资料管理'],
                'responsibilities': '日常养护、质量控制、安全监督、资料管理'
            },
            71: {
                'name': '第三养护管理所',
                'functions': ['负责高速公路日常养护', '负责养护工程质量控制', '负责养护作业安全监督', '负责养护资料管理'],
                'responsibilities': '日常养护、质量控制、安全监督、资料管理'
            },
            72: {
                'name': '第四养护管理所',
                'functions': ['负责高速公路日常养护', '负责养护工程质量控制', '负责养护作业安全监督', '负责养护资料管理'],
                'responsibilities': '日常养护、质量控制、安全监督、资料管理'
            },
            # 研究院下属单位（73-79）
            73: {
                'name': '工程质量检测中心',
                'functions': ['负责工程质量检测鉴定', '负责材料试验分析', '负责检测设备校准', '负责检测报告编制'],
                'responsibilities': '质量检测、材料试验、设备校准、报告编制'
            },
            74: {
                'name': '路桥检测中心',
                'functions': ['负责桥梁结构检测', '负责道路状况评估', '负责荷载试验分析', '负责检测技术研发'],
                'responsibilities': '桥梁检测、道路评估、荷载试验、技术研发'
            },
            75: {
                'name': '海顺设计公司',
                'functions': ['负责市政工程设计', '负责设计方案优化', '负责设计图纸审查', '负责设计技术服务'],
                'responsibilities': '工程设计、方案优化、图纸审查、技术服务'
            },
            76: {
                'name': '建达科技公司',
                'functions': ['负责科技创新研发', '负责技术成果转化', '负责科技项目管理', '负责知识产权管理'],
                'responsibilities': '科技创新、成果转化、科技管理、知识产权'
            },
            77: {
                'name': '路驰监理公司',
                'functions': ['负责工程监理咨询', '负责施工质量监督', '负责工程进度控制', '负责监理报告编制'],
                'responsibilities': '工程监理、质量监督、进度控制、报告编制'
            },
            78: {
                'name': '金艾检测中心',
                'functions': ['负责工程材料检测', '负责环境检测分析', '负责检测方法研究', '负责检测资质管理'],
                'responsibilities': '材料检测、环境检测、方法研究、资质管理'
            },
            79: {
                'name': '滨海分院',
                'functions': ['负责滨海新区市政规划', '负责区域工程设计', '负责技术咨询服务', '负责项目跟踪管理'],
                'responsibilities': '区域规划、工程设计、技术咨询、项目管理'
            },
            # 公路处下属单位（81-85）
            81: {
                'name': '第一公路管理所',
                'functions': ['负责辖区公路养护管理', '负责公路病害处理', '负责公路排水设施维护', '负责公路应急抢险'],
                'responsibilities': '公路养护、病害处理、排水维护、应急抢险'
            },
            82: {
                'name': '第二公路管理所',
                'functions': ['负责辖区公路养护管理', '负责公路病害处理', '负责公路排水设施维护', '负责公路应急抢险'],
                'responsibilities': '公路养护、病害处理、排水维护、应急抢险'
            },
            83: {
                'name': '第三公路管理所',
                'functions': ['负责辖区公路养护管理', '负责公路病害处理', '负责公路排水设施维护', '负责公路应急抢险'],
                'responsibilities': '公路养护、病害处理、排水维护、应急抢险'
            },
            84: {
                'name': '第四公路管理所',
                'functions': ['负责辖区公路养护管理', '负责公路病害处理', '负责公路排水设施维护', '负责公路应急抢险'],
                'responsibilities': '公路养护、病害处理、排水维护、应急抢险'
            },
            85: {
                'name': '外环公路管理所',
                'functions': ['负责外环线公路养护', '负责外环设施维护', '负责外环应急处置', '负责外环交通疏导'],
                'responsibilities': '外环养护、设施维护、应急处置、交通疏导'
            },
            # 建设公司下属单位（86-88）
            86: {
                'name': '天津道桥建设发展有限公司',
                'functions': ['负责道桥工程建设施工', '负责项目质量管理', '负责施工安全管理', '负责工程资料归档'],
                'responsibilities': '工程施工、质量管理、安全管理、资料归档'
            },
            87: {
                'name': '天津市政道桥建筑工程公司',
                'functions': ['负责市政建筑工程施工', '负责项目进度控制', '负责成本核算管理', '负责竣工验收移交'],
                'responsibilities': '工程施工、进度控制、成本核算、验收移交'
            },
            88: {
                'name': '天津道桥工程公司',
                'functions': ['负责道桥工程专业施工', '负责技术方案编制', '负责施工技术创新', '负责工程质量创优'],
                'responsibilities': '专业施工、技术创新、质量创优、工程优化'
            },
            # 设计院下属单位（62）
            62: {
                'name': '天津市市政工程设计研究院城市设计分院',
                'functions': ['负责城市设计规划', '负责市政工程方案设计', '负责设计技术创新', '负责设计质量管控'],
                'responsibilities': '城市设计、方案设计、技术创新、质量管控'
            },
            # 地铁处下属单位（63）
            63: {
                'name': '天津市地下铁道总公司',
                'functions': ['负责地铁运营管理', '负责地铁设备维护', '负责运营安全保障', '负责乘客服务管理'],
                'responsibilities': '地铁运营、设备维护、安全保障、乘客服务'
            },
        }

    def show(self, user=None):
        """显示单位概况"""
        self.user = user
        self._create_overview_tab(self.parent, user)

    def _create_overview_tab(self, parent, user):
        """创建单位概况选项卡 - 三栏布局"""
        # 清除现有内容
        for widget in self.parent.winfo_children():
            widget.destroy()

        # 创建主框架（三栏布局）
        main_frame = tk.Frame(self.parent, bg=self.COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = tk.Label(
            main_frame,
            text='单位概况',
            font=('SimHei', 20, 'bold'),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        )
        title_label.pack(pady=10)

        # 创建三栏容器
        content_frame = tk.Frame(main_frame, bg=self.COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧栏 - 市政工程局介绍
        left_frame = tk.Frame(content_frame, bg=self.COLORS['bg_secondary'],
                              highlightbackground="#ddd", highlightthickness=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(left_frame, text='天津市市政工程局',
                font=('SimHei', 14, 'bold'),
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['primary']).pack(pady=(15, 10))

        bureau_intro = """主要职能为：
（一）贯彻执行有关市政道桥、公路管理的法律、法规、规章和方针政策，起草相关地方性法规、规章草案和规范性文件并组织实施。
（二）拟订市政道桥、公路专项规划和建设计划；制定市政道桥、公路基础设施养护、维修计划；会同市财政局制定并下达市政道桥、公路养护维修资金计划；负责资金的安排和管理；负责已接收管理的道桥、公路范围内地下管网施工的协调管理。
（三）组织实施市政道桥、公路的养护及大中维修项目；负责对全市市政道桥、公路设施状况进行检测评定，并对运行服务进行监督考核；负责市政道桥、公路设施的综合统计工作；参与市政道桥、公路建设市场的管理。
（四）承担道路、公路运行设施执法监督的相关工作；负责有关行政复议工作；负责市政道桥、公路设施命名申报工作。
（五）负责市政道桥、公路养护维修工程的质量和安全监督。
（六）拟订市政道桥、公路设施有关收费标准；负责高速公路联网收费的管理；编制修订养护工程定额。
（七）组织推动市政道桥、公路养护维修技术发展，拟订行业技术标准及规范，组织科技攻关，推广科技成果；组织实施信息化建设工作。
（八）负责市政道桥、公路基础设施管理。
（九）负责市政道桥、公路养护管理；指导推动市政道桥、公路养护专业技能培训工作；配合有关部门负责专业人员技术资格评审工作；指导有关行业协会、学会工作。
（十）承办市委、市政府交办的其它事项。

组织架构：
• 局机关设有19个处室
• 下辖20个事业单位"""

        tk.Label(left_frame, text=bureau_intro,
                font=('SimHei', 10),
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['text_secondary'],
                justify=tk.LEFT, anchor=tk.W, wraplength=300,
                padx=15, pady=10).pack(fill=tk.BOTH, expand=True)

        # 右侧栏容器（上下两栏）
        right_frame = tk.Frame(content_frame, bg=self.COLORS['bg_primary'])
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 右上栏 - 内设处室
        top_right_frame = tk.Frame(right_frame, bg=self.COLORS['bg_secondary'],
                                   highlightbackground="#ddd", highlightthickness=1)
        top_right_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        tk.Label(top_right_frame, text='内设处室',
                font=('SimHei', 12, 'bold'),
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['primary']).pack(pady=(10, 5))

        # 处室容器 - 使用网格布局，3列
        dept_container = tk.Frame(top_right_frame, bg=self.COLORS['bg_secondary'])
        dept_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 遍历所有处室，创建可点击按钮，3列布局
        sorted_dept_ids = sorted(self.DEPARTMENT_DETAILS.keys())
        for idx, dept_id in enumerate(sorted_dept_ids):
            dept_info = self.DEPARTMENT_DETAILS[dept_id]
            row = idx // 3
            col = idx % 3

            btn_frame = tk.Frame(dept_container, bg=self.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            # 设置列权重
            dept_container.grid_columnconfigure(col, weight=1)

            dept_btn = tk.Label(
                btn_frame,
                text=f"{dept_id}. {dept_info['name']}",
                font=('SimHei', 10),
                bg=self.COLORS['bg_secondary'],
                fg='#1a5fb4',
                cursor='hand2',
                anchor=tk.W,
                padx=10,
                pady=8
            )
            dept_btn.pack(fill=tk.X)
            dept_btn.bind("<Button-1>", lambda e, did=dept_id: self._show_department_detail(did))
            dept_btn.bind("<Enter>", lambda e, btn=dept_btn: btn.config(bg='#e3f2fd'))
            dept_btn.bind("<Leave>", lambda e, btn=dept_btn: btn.config(bg=self.COLORS['bg_secondary']))

        # 右下栏 - 下属单位
        bottom_right_frame = tk.Frame(right_frame, bg=self.COLORS['bg_secondary'],
                                      highlightbackground="#ddd", highlightthickness=1)
        bottom_right_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(bottom_right_frame, text='下属单位',
                font=('SimHei', 12, 'bold'),
                bg=self.COLORS['bg_secondary'],
                fg=self.COLORS['primary']).pack(pady=(10, 5))

        # 下属单位容器 - 使用网格布局，2列
        unit_container = tk.Frame(bottom_right_frame, bg=self.COLORS['bg_secondary'])
        unit_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 遍历所有下属单位，创建可点击按钮，2列布局
        sorted_unit_ids = sorted(self.UNIT_DETAILS.keys())
        for idx, unit_id in enumerate(sorted_unit_ids):
            unit_info = self.UNIT_DETAILS[unit_id]
            unit_name = unit_info['name']

            # 简化名称显示
            display_name = unit_name
            if '（' in unit_name:
                display_name = unit_name.split('（')[0]
            elif '(' in unit_name:
                display_name = unit_name.split('(')[0]

            row = idx // 2
            col = idx % 2

            btn_frame = tk.Frame(unit_container, bg=self.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            # 设置列权重
            unit_container.grid_columnconfigure(col, weight=1)

            unit_btn = tk.Label(
                btn_frame,
                text=f"{idx + 1}. {display_name}",
                font=('SimHei', 10),
                bg=self.COLORS['bg_secondary'],
                fg='#1a5fb4',
                cursor='hand2',
                anchor=tk.W,
                padx=10,
                pady=8
            )
            unit_btn.pack(fill=tk.X)
            unit_btn.bind("<Button-1>", lambda e, uid=unit_id: self._show_unit_detail(uid))
            unit_btn.bind("<Enter>", lambda e, btn=unit_btn: btn.config(bg='#e3f2fd'))
            unit_btn.bind("<Leave>", lambda e, btn=unit_btn: btn.config(bg=self.COLORS['bg_secondary']))

            # 如果有下属单位，显示标记
            if 'sub_units' in unit_info and unit_info['sub_units']:
                sub_count = len(unit_info['sub_units'])
                tk.Label(
                    btn_frame,
                    text=f"    （包含 {sub_count} 个下属单位）",
                    font=('SimHei', 9),
                    bg=self.COLORS['bg_secondary'],
                    fg=self.COLORS['text_secondary'],
                    anchor=tk.W
                ).pack(fill=tk.X, padx=10)

    def _show_unit_detail(self, unit_id):
        """显示单位详情弹窗"""
        # 判断是下属单位还是基层单位
        if unit_id in self.UNIT_DETAILS:
            unit_info = self.UNIT_DETAILS[unit_id]
            unit_type = "下属单位"
        elif unit_id in self.SUB_UNIT_DETAILS:
            unit_info = self.SUB_UNIT_DETAILS[unit_id]
            unit_type = "基层单位"
        else:
            messagebox.showerror("错误", "未找到单位信息")
            return

        # 创建弹窗
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"{unit_type}详情")
        detail_window.geometry("600x500")
        detail_window.configure(bg=self.COLORS['bg_primary'])

        # 居中显示
        detail_window.update_idletasks()
        width = detail_window.winfo_width()
        height = detail_window.winfo_height()
        x = (detail_window.winfo_screenwidth() // 2) - (width // 2)
        y = (detail_window.winfo_screenheight() // 2) - (height // 2)
        detail_window.geometry(f'{width}x{height}+{x}+{y}')

        # 创建滚动区域
        canvas = tk.Canvas(detail_window, bg=self.COLORS['bg_primary'])
        scrollbar = ttk.Scrollbar(detail_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg_primary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 单位名称
        tk.Label(
            scrollable_frame,
            text=unit_info['name'],
            font=('SimHei', 18, 'bold'),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['primary']
        ).pack(pady=(10, 20))

        # 主要职能标题
        tk.Label(
            scrollable_frame,
            text='主要职能:',
            font=('SimHei', 12, 'bold'),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))

        # 职能列表
        for func in unit_info.get('functions', []):
            tk.Label(
                scrollable_frame,
                text=f'• {func}',
                font=('SimHei', 10),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                anchor=tk.W,
                wraplength=550
            ).pack(anchor=tk.W, padx=30, pady=2)

        # 职责概述
        tk.Label(
            scrollable_frame,
            text=f"职责概括: {unit_info.get('responsibilities', '暂无信息')}",
            font=('SimHei', 10, 'italic'),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['accent'],
            anchor=tk.W,
            wraplength=550
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))

        # 如果是下属单位，显示下属单位的下属单位
        if 'sub_units' in unit_info and unit_info['sub_units']:
            tk.Label(
                scrollable_frame,
                text='下属单位:',
                font=('SimHei', 12, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']
            ).pack(anchor=tk.W, padx=15, pady=(20, 5))

            tk.Label(
                scrollable_frame,
                text=unit_info.get('sub_unit_desc', ''),
                font=('SimHei', 10),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                anchor=tk.W,
                wraplength=550
            ).pack(anchor=tk.W, padx=15, pady=10)

            # 创建下属单位按钮列表
            for sub_id, sub_name in unit_info['sub_units'].items():
                sub_btn_frame = tk.Frame(scrollable_frame, bg=self.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
                sub_btn_frame.pack(fill=tk.X, padx=15, pady=3)

                sub_btn = tk.Label(
                    sub_btn_frame,
                    text=f"  {sub_name}",
                    font=('SimHei', 10),
                    bg=self.COLORS['bg_secondary'],
                    fg='#1a5fb4',
                    cursor='hand2',
                    anchor=tk.W,
                    padx=10,
                    pady=8
                )
                sub_btn.pack(fill=tk.X)

                # 绑定点击事件，显示基层单位详情
                sub_btn.bind("<Button-1>", lambda e, sid=sub_id: self._show_unit_detail(sid))

                # 鼠标悬停效果
                sub_btn.bind("<Enter>", lambda e, btn=sub_btn: btn.config(bg='#e3f2fd'))
                sub_btn.bind("<Leave>", lambda e, btn=sub_btn: btn.config(bg=self.COLORS['bg_secondary']))

    def _show_department_detail(self, dept_id):
        """显示处室详情弹窗"""
        if dept_id not in self.DEPARTMENT_DETAILS:
            messagebox.showerror("错误", "未找到处室信息")
            return

        dept_info = self.DEPARTMENT_DETAILS[dept_id]

        # 创建弹窗
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"处室详情 - {dept_info['name']}")
        detail_window.geometry("600x500")
        detail_window.configure(bg=self.COLORS['bg_primary'])

        # 居中显示
        detail_window.update_idletasks()
        width = detail_window.winfo_width()
        height = detail_window.winfo_height()
        x = (detail_window.winfo_screenwidth() // 2) - (width // 2)
        y = (detail_window.winfo_screenheight() // 2) - (height // 2)
        detail_window.geometry(f'{width}x{height}+{x}+{y}')

        # 创建滚动区域
        canvas = tk.Canvas(detail_window, bg=self.COLORS['bg_primary'])
        scrollbar = ttk.Scrollbar(detail_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg_primary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 处室名称
        tk.Label(
            scrollable_frame,
            text=dept_info['name'],
            font=('SimHei', 18, 'bold'),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['primary']
        ).pack(pady=(10, 20))

        # 主要职能标题
        tk.Label(
            scrollable_frame,
            text='主要职能:',
            font=('SimHei', 12, 'bold'),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['text_primary']
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))

        # 职能列表
        for func in dept_info.get('functions', []):
            tk.Label(
                scrollable_frame,
                text=f'• {func}',
                font=('SimHei', 10),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary'],
                anchor=tk.W,
                wraplength=550
            ).pack(anchor=tk.W, padx=30, pady=2)

        # 职责概述
        tk.Label(
            scrollable_frame,
            text=f"职责概括: {dept_info.get('responsibilities', '暂无信息')}",
            font=('SimHei', 10, 'italic'),
            bg=self.COLORS['bg_primary'],
            fg=self.COLORS['accent'],
            anchor=tk.W,
            wraplength=550
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))

        # 关闭按钮
        tk.Button(
            detail_window,
            text="关闭",
            command=detail_window.destroy,
            font=('SimHei', 10),
            bg=self.COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(pady=10)