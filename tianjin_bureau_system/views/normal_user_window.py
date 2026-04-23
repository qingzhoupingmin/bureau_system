# -*- coding: utf-8 -*-
"""
下属单位窗口 - 根据中层/基层单位显示不同功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from services.asset_service import AssetService
from services.message_service import MessageService
from services.auth_service import AuthService
from services.research_service import ResearchService
from services.budget_service import BudgetService
from services.document_service import DocumentService
from db.connection import db


# 中层单位ID列表
MIDDLE_UNITS = {21, 22, 23, 26, 27, 31, 38, 39, 41, 42}  # 公路处、高速处、道桥处、研究院、设计院、建设公司、地铁处、巡查处、超治办、养护工程处


class NormalUserWindow(MainWindow):
    """下属单位窗口"""

    def create_notebook(self):
        """创建标签页"""
        # 创建左右分栏布局
        self.paned = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 左侧导航栏
        self.create_left_sidebar()

        # 右侧内容区
        self.right_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_white'])
        self.paned.add(self.right_frame, minsize=800)

        # 默认显示单位概况
        self.show_overview()

    def is_middle_unit(self):
        """判断是否为中层单位"""
        return self.user.get('organization_id', 0) in MIDDLE_UNITS

    def create_left_sidebar(self):
        """创建左侧导航栏"""
        sidebar = tk.Frame(self.main_frame, bg=self.COLORS['primary'], width=200)
        self.paned.add(sidebar, minsize=200)

        # 获取单位信息
        from models.organization import Organization
        org = Organization.get_by_id(self.user.get('organization_id', 0))
        org_name = org['name'] if org else '下属单位'

        # 导航标题
        nav_title = tk.Label(sidebar, text=org_name, font=("Microsoft YaHei", 14, "bold"),
                            bg=self.COLORS['primary'], fg="white")
        nav_title.pack(pady=20)

        # 根据是否为中层单位显示不同菜单
        if self.is_middle_unit():
            # 中层单位菜单
            nav_items = [
                ("单位概况", self.show_overview),
                ("业务办理", self.show_business),
                ("单位资产", self.show_assets),
                ("资产申请", self.show_asset_apply),
                ("公文管理", self.show_documents),
                ("预算申报", self.show_budget_apply),
                ("个人中心", self.show_profile),
            ]
        else:
            # 基层单位菜单 - 简化版
            nav_items = [
                ("单位概况", self.show_overview),
                ("单位资产", self.show_assets),
                ("资产申请", self.show_asset_apply),
                ("公文沟通", self.show_documents),
                ("个人中心", self.show_profile),
            ]

        for text, command in nav_items:
            btn = tk.Button(sidebar, text=text, font=("Microsoft YaHei", 11),
                           bg=self.COLORS['secondary'], fg="white",
                           relief=tk.FLAT, cursor="hand2",
                           command=command)
            btn.pack(fill=tk.X, padx=15, pady=5)

    def get_unit_business(self):
        """获取中层单位的业务功能"""
        org_id = self.user.get('organization_id', 0)

        unit_business = {
            21: {  # 公路处
                'name': '公路处',
                'business': [
                    ('公路养护', '管理公路养护工作'),
                    ('路政管理', '管理路政执法'),
                    ('经费管理', '管理养护经费'),
                ]
            },
            22: {  # 高速处
                'name': '高速公路管理处',
                'business': [
                    ('收费管理', '高速公路收费管理'),
                    ('路政管理', '高速路政执法'),
                    ('养护管理', '高速公路养护'),
                ]
            },
            23: {  # 道桥处
                'name': '道路桥梁管理处',
                'business': [
                    ('设施管理', '管理市政设施'),
                    ('养护工程', '管理养护项目'),
                    ('应急处置', '应急抢险管理'),
                ]
            },
            26: {  # 研究院
                'name': '市政工程研究院',
                'business': [
                    ('科研管理', '科研项目管理'),
                    ('检测服务', '工程质量检测'),
                    ('技术咨询', '技术服务咨询'),
                ]
            },
            27: {  # 设计院
                'name': '市政工程设计研究院',
                'business': [
                    ('工程设计', '市政工程设计'),
                    ('方案审查', '设计方案审查'),
                    ('技术服务', '技术支持服务'),
                ]
            },
            31: {  # 建设公司
                'name': '市政工程建设公司',
                'business': [
                    ('工程建设', '工程建设管理'),
                    ('安全管理', '施工安全管理'),
                    ('质量监督', '工程质量监督'),
                ]
            },
            38: {  # 地铁处
                'name': '地铁管理处',
                'business': [
                    ('运营管理', '地铁运营管理'),
                    ('设备管理', '地铁设备管理'),
                    ('安全管理', '安全管理'),
                ]
            },
            39: {  # 市政公路巡查管理处
                'name': '市政公路巡查管理处',
                'business': [
                    ('公路巡查', '公路路政巡查管理'),
                    ('病害上报', '道路病害信息采集上报'),
                    ('巡查统计', '巡查工作统计报表'),
                ]
            },
            41: {  # 公路治理车辆超限超载管理办公室
                'name': '公路治理车辆超限超载管理办公室',
                'business': [
                    ('超限治理', '治理车辆超限超载'),
                    ('源头监管', '货运源头监管'),
                    ('案件处理', '超限违法案件处理'),
                ]
            },
            42: {  # 公路养护工程处
                'name': '公路养护工程处',
                'business': [
                    ('养护工程', '公路养护工程管理'),
                    ('设施维护', '公路设施维护'),
                    ('应急养护', '公路应急养护抢修'),
                ]
            },
        }

        return unit_business.get(org_id, {'name': '下属单位', 'business': [('业务管理', '单位业务管理')]})

    def show_business(self):
        """显示业务办理 - 中层单位"""
        self.clear_right_frame()

        unit_info = self.get_unit_business()
        unit_name = unit_info['name']
        business_list = unit_info['business']

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text=f"{unit_name} - 业务办理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 业务功能卡片区域
        business_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_light'])
        business_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建业务卡片（每行3个）
        for i, (business_name, business_desc) in enumerate(business_list):
            row = i // 3
            col = i % 3

            card_frame = tk.Frame(business_frame, bg=self.COLORS['bg_secondary'],
                                 relief=tk.RAISED, bd=1)
            card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            name_label = tk.Label(card_frame, text=business_name,
                                 font=("Microsoft YaHei", 12, "bold"),
                                 bg=self.COLORS['bg_secondary'],
                                 fg=self.COLORS['primary'])
            name_label.pack(pady=(15, 5))

            desc_label = tk.Label(card_frame, text=business_desc,
                                 font=("Microsoft YaHei", 9),
                                 bg=self.COLORS['bg_secondary'],
                                 fg=self.COLORS['text_secondary'],
                                 wraplength=200)
            desc_label.pack(pady=(0, 10))

            btn_frame = tk.Frame(card_frame, bg=self.COLORS['bg_secondary'])
            btn_frame.pack(pady=(0, 15))

            btn = tk.Button(btn_frame, text="进入办理",
                           bg=self.COLORS['primary'], fg="white",
                           font=("Microsoft YaHei", 9),
                           relief=tk.FLAT,
                           command=lambda name=business_name: self.handle_unit_business(name))
            btn.pack()

        for i in range(3):
            business_frame.grid_columnconfigure(i, weight=1)

    def handle_unit_business(self, business_name):
        """处理中层单位业务 - 与上级处室业务对应"""
        org_id = self.user.get('organization_id', 0)

        # 中层单位业务与上级处室业务的映射关系
        # 公路处(21)→设施养护处(4), 高速处(22)→设施养护处(4), 道桥处(23)→设施管理处(3)+设施养护处(4)
        # 研究院(26)→科技处(12), 设计院(27)→规划处(6)+建设管理处(5)
        # 建设公司(31)→建设管理处(5), 地铁处(38)→建设管理处(5)+安全保卫处(13)

        business_map = {
            # 公路处业务
            '公路养护': ('show_facility_maintenance', '公路养护管理'),
            '路政管理': ('show_facility_management', '路政执法管理'),
            '经费管理': ('show_budget_apply', '养护经费管理'),

            # 高速处业务
            '收费管理': ('show_facility_management', '收费管理'),
            '高速路政': ('show_facility_management', '高速路政管理'),
            '养护管理': ('show_facility_maintenance', '高速公路养护'),

            # 道桥处业务
            '设施管理': ('show_facility_management', '市政设施管理'),
            '养护工程': ('show_facility_maintenance', '养护工程项目'),
            '应急处置': ('show_emergency', '应急抢险管理'),

            # 研究院业务
            '科研管理': ('show_research', '科研项目管理'),
            '检测服务': ('show_tech_service', '质量检测服务'),
            '技术咨询': ('show_tech_service', '技术服务咨询'),

            # 设计院业务
            '工程设计': ('show_design', '工程设计管理'),
            '方案审查': ('show_design_review', '设计方案审查'),
            '技术支持': ('show_tech_service', '技术支持服务'),

            # 建设公司业务
            '工程建设': ('show_construction', '工程建设管理'),
            '安全管理': ('show_safety', '施工安全管理'),
            '质量监督': ('show_quality', '工程质量监督'),

            # 地铁处业务
            '运营管理': ('show_operation', '地铁运营管理'),
            '设备管理': ('show_facility_management', '地铁设备管理'),
            '安全管理': ('show_safety', '地铁安全管理'),

            # 市政公路巡查管理处业务
            '公路巡查': ('show_inspection', '公路巡查管理'),
            '病害上报': ('show_damage_report', '道路病害上报'),
            '巡查统计': ('show_inspection_stats', '巡查统计报表'),

            # 超治办业务
            '超限治理': ('show_overload_control', '超限超载治理'),
            '源头监管': ('show_source_supervision', '货运源头监管'),
            '案件处理': ('show_overload_case', '超限违法案件处理'),

            # 公路养护工程处业务
            '养护工程': ('show_maintenance_project', '公路养护工程'),
            '设施维护': ('show_facility_maintenance', '公路设施维护'),
            '应急养护': ('show_emergency_maintenance', '公路应急养护'),
        }

        if business_name in business_map:
            method_name, title = business_map[business_name]
            if hasattr(self, method_name):
                getattr(self, method_name)()
            else:
                self._show_content_page(title, f"{title}功能正在完善中...")
        else:
            self._show_content_page(business_name, f"{business_name}功能正在完善中...")

    def show_documents(self):
        """显示公文沟通 - 统一界面"""
        self.clear_right_frame()

        # 根据单位类型显示不同内容
        if self.is_middle_unit():
            # 中层单位：公文管理（可提交、接收、查看）
            self.show_document_manage()
        else:
            # 基层单位：公文沟通（提交给上级、接收上级公文）
            self.show_document_comm()

    def show_document_manage(self):
        """中层单位公文管理"""
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="公文管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 选项卡
        notebook = ttk.Notebook(self.right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 发文-tab
        send_frame = tk.Frame(notebook)
        notebook.add(send_frame, text="发文")

        columns = ("ID", "标题", "接收单位", "状态", "时间")
        self.doc_send_tree = ttk.Treeview(send_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.doc_send_tree.heading(col, text=col)
            self.doc_send_tree.column(col, width=120)

        self.doc_send_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(send_frame, orient=tk.VERTICAL, command=self.doc_send_tree.yview)
        self.doc_send_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(send_frame, text="新建公文", command=self.show_document_submit,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        # 收文-tab
        recv_frame = tk.Frame(notebook)
        notebook.add(recv_frame, text="收文")

        columns = ("ID", "标题", "发送单位", "状态", "时间")
        self.doc_recv_tree = ttk.Treeview(recv_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.doc_recv_tree.heading(col, text=col)
            self.doc_recv_tree.column(col, width=120)

        self.doc_recv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(recv_frame, orient=tk.VERTICAL, command=self.doc_recv_tree.yview)
        self.doc_recv_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.refresh_doc_manage()

    def refresh_doc_manage(self):
        """刷新公文管理列表"""
        # 发文
        for item in self.doc_send_tree.get_children():
            self.doc_send_tree.delete(item)

        org_id = self.user.get('organization_id', 0)
        docs = DocumentService.get_documents_by_org(org_id)

        for doc in docs:
            self.doc_send_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], doc.get('receiver_org', '未知'),
                doc.get('status', ''), doc.get('create_date', '')
            ))

        # 收文
        for item in self.doc_recv_tree.get_children():
            self.doc_recv_tree.delete(item)

        recv_docs = DocumentService.get_received_documents(org_id)
        for doc in recv_docs:
            self.doc_recv_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], doc.get('sender_org', '未知'),
                doc.get('status', ''), doc.get('create_date', '')
            ))

    def show_document_comm(self):
        """基层单位公文沟通"""
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="公文沟通", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 选项卡
        notebook = ttk.Notebook(self.right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 提交公文
        submit_frame = tk.Frame(notebook)
        notebook.add(submit_frame, text="向上级提交")
        tk.Button(submit_frame, text="新建公文", command=self.show_document_submit,
                 bg=self.COLORS['primary'], fg="white").pack(pady=10)

        # 接收公文
        recv_frame = tk.Frame(notebook)
        notebook.add(recv_frame, text="收文查看")

        columns = ("ID", "标题", "发送单位", "时间")
        self基层_recv_tree = ttk.Treeview(recv_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self基层_recv_tree.heading(col, text=col)
            self基层_recv_tree.column(col, width=150)

        self基层_recv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(recv_frame, orient=tk.VERTICAL, command=self基层_recv_tree.yview)
        self基层_recv_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.refresh_基层_recv()

    def refresh_基层_recv(self):
        """刷新基层单位收文"""
        for item in self基层_recv_tree.get_children():
            self基层_recv_tree.delete(item)

        org_id = self.user.get('organization_id', 0)
        recv_docs = DocumentService.get_received_documents(org_id)

        for doc in recv_docs:
            self基层_recv_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], doc.get('sender_org', '未知'),
                doc.get('create_date', '')
            ))

    def _show_content_page(self, title, content):
        """统一内容页面"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text=title, font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        content_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_light'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(content_frame, text=content,
                font=("Microsoft YaHei", 12),
                bg=self.COLORS['bg_light'],
                fg=self.COLORS['text_secondary']).pack()

    def clear_right_frame(self):
        """清空右侧内容区"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_overview(self):
        """显示单位概况"""
        self.clear_right_frame()
        from views.organization_overview import OrganizationOverview
        overview = OrganizationOverview(self.right_frame, self.COLORS, self.user)
        overview.show(self.user)

    def show_assets(self):
        """显示单位资产"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)

        my_org_id = self.user.get('organization_id', 0)

        # 判断是否为中层机关（parent unit）
        parent_units = {
            21: '公路处',
            22: '高速处',
            23: '道桥处',
            26: '研究院',
            27: '设计院',
            31: '建设公司',
            38: '地铁处'
        }
        is_parent = my_org_id in parent_units

        if is_parent:
            tk.Label(title_frame, text="本单位及下属单位资产", font=("Microsoft YaHei", 18, "bold"),
                    bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)
        else:
            tk.Label(title_frame, text="单位资产", font=("Microsoft YaHei", 18, "bold"),
                    bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 资产列表
        columns = ("ID", "名称", "类别", "型号", "金额", "状态", "保管人", "所属单位")
        self.unit_asset_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.unit_asset_tree.heading(col, text=col)
            self.unit_asset_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.unit_asset_tree.yview)
        self.unit_asset_tree.configure(yscrollcommand=scrollbar.set)

        self.unit_asset_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_unit_assets,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_unit_assets()

    def refresh_unit_assets(self):
        """刷新资产列表"""
        for item in self.unit_asset_tree.get_children():
            self.unit_asset_tree.delete(item)

        my_org_id = self.user['organization_id']

        # 判断是否为中层机关
        parent_sub_units = {
            21: list(range(81, 91)),  # 公路处下属: 81-90
            22: list(range(61, 73)),  # 高速处下属: 61-72
            23: list(range(51, 61)),  # 道桥处下属: 51-60
            26: list(range(73, 80)),  # 研究院下属: 73-79
            27: [62, 91, 92, 93, 94, 95, 96, 97, 98],  # 设计院下属: 62, 91-98
            31: list(range(86, 89)),  # 建设公司下属: 86-88
            38: [63],                   # 地铁处下属: 63
            39: [],                     # 巡查处下属: 暂无
            41: [],                     # 超治办下属: 暂无
            42: list(range(101, 111))   # 养护工程处下属: 101-110
        }

        from models.organization import Organization
        all_orgs = Organization.get_all_organizations()
        org_map = {o['id']: o['name'] for o in all_orgs}

        if my_org_id in parent_sub_units:
            # 中层机关：先显示本单位资产，再显示下属单位资产
            # 本单位资产
            my_org_name = org_map.get(my_org_id, f'单位{my_org_id}')
            assets = AssetService.get_all_assets({'organization_id': my_org_id})
            for asset in assets:
                self.unit_asset_tree.insert("", tk.END, values=(
                    asset['id'], asset['name'], asset['category'], asset['model'],
                    asset.get('price', 0), asset.get('status', ''), asset.get('caretaker', ''), f"【本单位】{my_org_name}"
                ))
            # 下属单位资产
            sub_ids = parent_sub_units[my_org_id]
            for sub_id in sub_ids:
                assets = AssetService.get_all_assets({'organization_id': sub_id})
                org_name = org_map.get(sub_id, f'单位{sub_id}')
                for asset in assets:
                    self.unit_asset_tree.insert("", tk.END, values=(
                        asset['id'], asset['name'], asset['category'], asset['model'],
                        asset.get('price', 0), asset.get('status', ''), asset.get('caretaker', ''), org_name
                    ))
        else:
            # 普通单位：只查看本单位资产
            assets = AssetService.get_all_assets({'organization_id': my_org_id})
            my_org_name = org_map.get(my_org_id, '')
            for asset in assets:
                self.unit_asset_tree.insert("", tk.END, values=(
                    asset['id'], asset['name'], asset['category'], asset['model'],
                    asset.get('price', 0), asset.get('status', ''), asset.get('caretaker', ''), my_org_name
                ))

    def show_asset_apply(self):
        """显示资产申请"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="资产申请", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 可申请的公用设备
        tk.Label(self.right_frame, text="可申请的公用设备:", font=("Microsoft YaHei", 11, "bold"),
                bg=self.COLORS['bg_white']).pack(anchor="w", padx=20, pady=(10, 5))

        columns = ("ID", "名称", "类别", "型号", "金额", "状态")
        self.unit_apply_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.unit_apply_tree.heading(col, text=col)
            self.unit_apply_tree.column(col, width=120)

        self.unit_apply_tree.pack(fill=tk.X, padx=20, pady=5)

        # 申请表单
        form_frame = tk.LabelFrame(self.right_frame, text="申请使用", font=("Microsoft YaHei", 11))
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(form_frame, text="申请原因:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.unit_apply_reason = tk.Text(form_frame, width=50, height=4)
        self.unit_apply_reason.grid(row=0, column=1, padx=10, pady=10)

        def submit_apply():
            selected = self.unit_apply_tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请选择要申请的资产")
                return
            item = self.unit_apply_tree.item(selected[0])
            asset_id = item['values'][0]
            reason = self.unit_apply_reason.get(1.0, tk.END).strip()
            if not reason:
                messagebox.showwarning("提示", "请填写申请原因")
                return

            AssetService.apply_for_asset(asset_id, self.user['id'], self.user['organization_id'], reason)
            self.unit_apply_reason.delete(1.0, tk.END)
            messagebox.showinfo("成功", "申请已提交")

        tk.Button(form_frame, text="提交申请", command=submit_apply,
                 bg=self.COLORS['success'], fg="white").grid(row=1, column=1, pady=10)

        self.refresh_public_assets()

    def refresh_public_assets(self):
        """刷新可申请的公用资产"""
        for item in self.unit_apply_tree.get_children():
            self.unit_apply_tree.delete(item)

        assets = AssetService.get_all_assets({'is_public': 1})
        for asset in assets:
            self.unit_apply_tree.insert("", tk.END, values=(
                asset['id'], asset['name'], asset['category'], asset['model'],
                asset.get('price', 0), asset.get('status', '')
            ))

    def show_document_submit(self):
        """显示公文提交 - 支持向上级、平级、下级提交"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="公文提交", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 提交表单
        form_card = self.create_card(self.right_frame, "提交公文")
        form_card.pack(fill=tk.X, padx=20, pady=10)

        form_frame = tk.Frame(form_card, bg=self.COLORS['bg_white'])
        form_frame.pack(padx=20, pady=15, fill=tk.X)

        my_org_id = self.user.get('organization_id', 0)

        # 定义中层单位与上下级关系
        parent_sub_units = {
            21: {'parent': None, 'subs': list(range(81, 86)), 'name': '天津市公路处'},      # 公路处
            22: {'parent': None, 'subs': list(range(61, 73)), 'name': '天津市高速公路管理处'}, # 高速处
            23: {'parent': None, 'subs': list(range(51, 61)), 'name': '天津市道路桥梁管理处'},  # 道桥处
            26: {'parent': None, 'subs': list(range(73, 80)), 'name': '天津市市政工程研究院'},  # 研究院
            27: {'parent': None, 'subs': [62, 91, 92, 93, 94, 95, 96, 97, 98], 'name': '天津市市政工程设计研究院'},  # 设计院
            31: {'parent': None, 'subs': list(range(86, 89)), 'name': '天津市市政工程建设公司'}, # 建设公司
            38: {'parent': None, 'subs': [63], 'name': '天津市地铁管理处'},  # 地铁处
            39: {'parent': None, 'subs': [], 'name': '天津市市政公路巡查管理处'},  # 巡查处
            41: {'parent': None, 'subs': [], 'name': '天津市公路治理车辆超限超载管理办公室'},  # 超治办
            42: {'parent': None, 'subs': list(range(101, 111)), 'name': '天津市公路养护工程处'}  # 养护工程处
        }

        # 判断用户类型
        is_sub_unit = (51 <= my_org_id <= 60) or (61 <= my_org_id <= 72) or \
                      (73 <= my_org_id <= 79) or (81 <= my_org_id <= 90) or \
                      (86 <= my_org_id <= 88) or (101 <= my_org_id <= 110) or \
                      (my_org_id in [62, 63, 91, 92, 93, 94, 95, 96, 97, 98])
        is_middle_level = my_org_id in parent_sub_units

        # 获取可选的接收单位
        all_orgs = []
        from models.organization import Organization
        all_orgs_data = Organization.get_all_organizations()
        org_map = {o['id']: o['name'] for o in all_orgs_data}

        # 接收单位选项（根据用户类型决定）
        receiver_options = []
        receiver_values = {}  # {显示名称: org_id}

        if is_sub_unit:
            # 基层单位：只能提交给上级（直属中层单位）
            for mid_id, info in parent_sub_units.items():
                if my_org_id in info['subs']:
                    receiver_options.append(f"上级: {info['name']}")
                    receiver_values[f"上级: {info['name']}"] = str(mid_id)
                    break

        elif is_middle_level:
            # 中层单位：可以提交给上级(局机关)、平级(其他中层单位)、下级(下属基层单位)
            # 上级选项（局机关相关处室）
            receiver_options.append("── 提交给上级(局机关) ──")
            # 可选的处室
            dept_options = [
                (1, "办公室"), (7, "财务处"), (10, "资产管理处"), (11, "劳动人事处"),
                (12, "科技处"), (2, "计划处"), (3, "设施管理处"), (4, "设施养护处"),
                (5, "建设管理处"), (6, "规划处"), (8, "规费管理处"), (9, "审计处")
            ]
            for dept_id, dept_name in dept_options:
                receiver_options.append(f"  → {dept_name}")
                receiver_values[f"  → {dept_name}"] = str(dept_id)

            # 平级选项（其他中层单位）
            receiver_options.append("── 提交给平级单位 ──")
            for mid_id, info in parent_sub_units.items():
                if mid_id != my_org_id:
                    receiver_options.append(f"  → {info['name']}")
                    receiver_values[f"  → {info['name']}"] = str(mid_id)

            # 下级选项（下属基层单位）
            if parent_sub_units[my_org_id]['subs']:
                receiver_options.append("── 提交给下属单位 ──")
                for sub_id in parent_sub_units[my_org_id]['subs']:
                    sub_name = org_map.get(sub_id, f'单位{sub_id}')
                    receiver_options.append(f"  → {sub_name}")
                    receiver_values[f"  → {sub_name}"] = str(sub_id)

        # 收文单位选择
        tk.Label(form_frame, text="收文单位:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.doc_receiver_var = tk.StringVar()
        if receiver_options:
            self.doc_receiver_var.set(receiver_options[0])
        receiver_combo = ttk.Combobox(form_frame, textvariable=self.doc_receiver_var,
                                       values=receiver_options, width=38, state="readonly")
        receiver_combo.grid(row=0, column=1, pady=8)

        tk.Label(form_frame, text="标题:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.doc_title_entry = tk.Entry(form_frame, width=40)
        self.doc_title_entry.grid(row=1, column=1, pady=8)

        tk.Label(form_frame, text="类型:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        self.doc_type_var = tk.StringVar(value="report")
        doc_type_combo = ttk.Combobox(form_frame, textvariable=self.doc_type_var, width=38)
        doc_type_combo['values'] = ('报告', '请示', '通知')
        doc_type_combo.grid(row=2, column=1, pady=8)

        tk.Label(form_frame, text="内容:").grid(row=3, column=0, padx=10, pady=8, sticky="ne")
        self.doc_content_text = tk.Text(form_frame, width=40, height=8)
        self.doc_content_text.grid(row=3, column=1, pady=8)

        # 附件上传
        tk.Label(form_frame, text="附件:").grid(row=4, column=0, padx=10, pady=8, sticky="e")

        self.doc_attachment_var = tk.StringVar()
        attach_entry = tk.Entry(form_frame, textvariable=self.doc_attachment_var, width=28)
        attach_entry.grid(row=4, column=1, pady=8, sticky="w", padx=(0, 5))

        def select_file():
            from tkinter import filedialog
            filename = filedialog.askopenfilename(title="选择附件", filetypes=[("所有文件", "*.*"), ("文档", "*.doc *.docx *.pdf"), ("图片", "*.jpg *.png")])
            if filename:
                self.doc_attachment_var.set(filename)

        tk.Button(form_frame, text="浏览", command=select_file, bg=self.COLORS['secondary'], fg="white",
                 width=8).grid(row=4, column=1, pady=8, sticky="e", padx=(0, 10))

        # 保存接收单位映射
        self.doc_receiver_values = receiver_values

        tk.Button(form_frame, text="提交公文", command=self.submit_document,
                 bg=self.COLORS['success'], fg="white").grid(row=5, column=1, pady=15)

        # 我提交的公文
        tk.Label(self.right_frame, text="我提交的公文:", font=("Microsoft YaHei", 11, "bold"),
                bg=self.COLORS['bg_white']).pack(anchor="w", padx=20, pady=(10, 5))

        columns = ("ID", "标题", "类型", "接收单位", "提交时间", "状态")
        self.unit_doc_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.unit_doc_tree.heading(col, text=col)
            self.unit_doc_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.unit_doc_tree.yview)
        self.unit_doc_tree.configure(yscrollcommand=scrollbar.set)

        self.unit_doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.refresh_unit_documents()

    def refresh_unit_documents(self):
        """刷新公文列表"""
        for item in self.unit_doc_tree.get_children():
            self.unit_doc_tree.delete(item)

        # 先获取所有组织映射
        from models.organization import Organization
        all_orgs = Organization.get_all_organizations()
        org_map = {o['id']: o['name'] for o in all_orgs}

        sql = """SELECT * FROM documents WHERE sender_id = %s ORDER BY create_date DESC"""
        docs = db.execute_query(sql, (self.user['id'],))

        type_map = {'notice': '通知', 'report': '报告', 'request': '请示'}
        status_map = {'draft': '草稿', 'pending': '待审核', 'published': '已发布', 'replied': '已回复'}

        for doc in docs:
            # 获取接收单位名称
            receiver_ids = doc.get('receiver_org_ids', '')
            if receiver_ids:
                # 尝试将receiver_org_ids转为整数来查找
                try:
                    receiver_id = int(receiver_ids)
                    receiver_name = org_map.get(receiver_id, receiver_ids)
                except (ValueError, TypeError):
                    receiver_name = receiver_ids
            else:
                receiver_name = ''

            self.unit_doc_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], type_map.get(doc.get('doc_type', 'report'), doc.get('doc_type', '')),
                receiver_name, doc.get('create_date', ''), status_map.get(doc.get('status', 'draft'), doc.get('status', ''))
            ))

    def submit_document(self):
        """提交公文"""
        title = self.doc_title_entry.get().strip()
        content = self.doc_content_text.get(1.0, tk.END).strip()
        doc_type_cn = self.doc_type_var.get()

        type_map = {'报告': 'report', '请示': 'request', '通知': 'notice'}
        doc_type = type_map.get(doc_type_cn, 'report')

        if not title or not content:
            messagebox.showwarning("提示", "请填写标题和内容")
            return

        # 获取选中的收文单位
        selected = self.doc_receiver_var.get()
        receiver_org_ids = ''
        if hasattr(self, 'doc_receiver_values'):
            receiver_org_ids = self.doc_receiver_values.get(selected, '')
        if not receiver_org_ids:
            messagebox.showwarning("提示", "请选择收文单位")
            return

        from services.document_service import DocumentService
        # 获取附件路径
        attachment = self.doc_attachment_var.get() if hasattr(self, 'doc_attachment_var') else ''

        data = {
            'title': title,
            'content': content,
            'doc_type': doc_type,
            'receiver_org_ids': receiver_org_ids,
            'is_official': 0,
            'attachment': attachment
        }
        DocumentService.create_document(data, self.user['id'], self.user['organization_id'])

        self.doc_title_entry.delete(0, tk.END)
        self.doc_content_text.delete(1.0, tk.END)
        if hasattr(self, 'doc_attachment_var'):
            self.doc_attachment_var.set('')
        self.refresh_unit_documents()
        messagebox.showinfo("成功", "公文已提交")

    def show_document_receive(self):
        """显示收文查看 - 查看收到的公文"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="收文查看", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        my_org_id = self.user.get('organization_id', 0)

        # 收文列表
        columns = ("ID", "标题", "类型", "发送单位", "发送时间", "状态")
        self.receive_doc_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.receive_doc_tree.heading(col, text=col)
            self.receive_doc_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.receive_doc_tree.yview)
        self.receive_doc_tree.configure(yscrollcommand=scrollbar.set)

        self.receive_doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_receive_documents,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_receive_documents()

    def refresh_receive_documents(self):
        """刷新收文列表"""
        for item in self.receive_doc_tree.get_children():
            self.receive_doc_tree.delete(item)

        my_org_id = self.user.get('organization_id', 0)

        # 获取所有组织映射
        from models.organization import Organization
        all_orgs = Organization.get_all_organizations()
        org_map = {o['id']: o['name'] for o in all_orgs}

        # 查询发送给本单位的公文（只显示已发布的定稿）
        sql = """SELECT d.*, o.name as sender_name
                 FROM documents d
                 LEFT JOIN organizations o ON d.sender_org_id = o.id
                 WHERE (d.receiver_org_ids = %s OR d.receiver_org_ids LIKE %s OR d.receiver_org_ids LIKE %s OR d.receiver_org_ids LIKE %s)
                 AND d.status = 'published'
                 ORDER BY d.create_date DESC"""
        # 匹配模式：精确匹配、以ID开头、以ID结尾、包含ID（逗号分隔）
        like_start = f'{my_org_id},%'
        like_end = f'%,{my_org_id}'
        like_middle = f'%,{my_org_id},%'
        docs = db.execute_query(sql, (my_org_id, like_start, like_end, like_middle))

        type_map = {'notice': '通知', 'report': '报告', 'request': '请示'}
        status_map = {'draft': '草稿', 'pending': '待审核', 'published': '已发布', 'replied': '已回复'}

        for doc in docs:
            sender_name = doc.get('sender_name', org_map.get(doc.get('sender_org_id', ''), ''))
            self.receive_doc_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], type_map.get(doc.get('doc_type', 'report'), doc.get('doc_type', '')),
                sender_name, doc.get('create_date', ''), status_map.get(doc.get('status', 'draft'), doc.get('status', ''))
            ))

    def show_draft_manage(self):
        """显示草稿管理 - 中层单位管理下属提交的公文"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="草稿管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 获取当前单位ID
        my_org_id = self.user.get('organization_id', 0)

        # 判断是否为中层单位
        parent_sub_units = {
            21: list(range(81, 91)),  # 公路处下属: 81-90
            22: list(range(61, 73)),  # 高速处下属: 61-72
            23: list(range(51, 61)),  # 道桥处下属: 51-60
            26: list(range(73, 80)),  # 研究院下属: 73-79
            27: [62, 91, 92, 93, 94, 95, 96, 97, 98],  # 设计院下属: 62, 91-98
            31: list(range(86, 89)),  # 建设公司下属: 86-88
            38: [63],                   # 地铁处下属: 63
            39: [],                     # 巡查处下属: 暂无
            41: [],                     # 超治办下属: 暂无
            42: list(range(101, 111))   # 养护工程处下属: 101-110
        }

        # 判断是否为基层单位
        is_sub_unit = (51 <= my_org_id <= 60) or (61 <= my_org_id <= 72) or \
                      (73 <= my_org_id <= 79) or (81 <= my_org_id <= 90) or \
                      (86 <= my_org_id <= 88) or (my_org_id in [62, 63, 91, 92, 93, 94, 95, 96, 97, 98])

        if my_org_id in parent_sub_units:
            # 中层单位：查看本单位及下属单位的草稿
            sub_ids = parent_sub_units.get(my_org_id, [])
            all_org_ids = [my_org_id] + sub_ids
            self.draft_view_mode = 'middle'
        elif is_sub_unit:
            # 基层单位：只查看本单位草稿
            all_org_ids = [my_org_id]
            self.draft_view_mode = 'sub'
        else:
            # 其他单位：只查看本单位
            all_org_ids = [my_org_id]
            self.draft_view_mode = 'other'

        # 草稿列表
        columns = ("ID", "标题", "类型", "发送单位", "提交时间", "状态")
        self.draft_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.draft_tree.heading(col, text=col)
            self.draft_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.draft_tree.yview)
        self.draft_tree.configure(yscrollcommand=scrollbar.set)

        self.draft_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 操作按钮
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Button(btn_frame, text="新建草稿", command=self.create_new_draft,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="编辑", command=self.edit_selected_draft,
                 bg=self.COLORS['secondary'], fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="发布定稿", command=self.publish_selected_draft,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="删除", command=self.delete_selected_draft,
                 bg=self.COLORS['danger'], fg="white").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="刷新", command=self.refresh_draft_list,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.draft_all_org_ids = all_org_ids
        self.refresh_draft_list()

    def create_new_draft(self):
        """创建新草稿"""
        self.clear_right_frame()

        tk.Label(self.right_frame, text="新建草稿", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=10)

        form_card = self.create_card(self.right_frame, "草稿内容")
        form_card.pack(fill=tk.X, padx=20, pady=10)

        form_frame = tk.Frame(form_card, bg=self.COLORS['bg_white'])
        form_frame.pack(padx=20, pady=15, fill=tk.X)

        my_org_id = self.user.get('organization_id', 0)

        # 获取可选的接收单位
        parent_sub_units = {
            21: {'parent': None, 'subs': list(range(81, 86)), 'name': '天津市公路处'},
            22: {'parent': None, 'subs': list(range(61, 73)), 'name': '天津市高速公路管理处'},
            23: {'parent': None, 'subs': list(range(51, 61)), 'name': '天津市道路桥梁管理处'},
            26: {'parent': None, 'subs': list(range(73, 80)), 'name': '天津市市政工程研究院'},
            27: {'parent': None, 'subs': [62, 71, 72, 73, 74, 75, 76, 77, 78], 'name': '天津市市政工程设计研究院'},
            31: {'parent': None, 'subs': list(range(86, 89)), 'name': '天津市市政工程建设公司'},
            38: {'parent': None, 'subs': [63], 'name': '天津市地铁管理处'}
        }

        # 判断用户类型
        is_sub_unit = (51 <= my_org_id <= 60) or (61 <= my_org_id <= 72) or \
                      (73 <= my_org_id <= 79) or (81 <= my_org_id <= 90) or \
                      (86 <= my_org_id <= 88) or (101 <= my_org_id <= 110) or \
                      (my_org_id in [62, 63, 91, 92, 93, 94, 95, 96, 97, 98])
        is_middle_level = my_org_id in parent_sub_units

        # 获取组织映射
        from models.organization import Organization
        all_orgs_data = Organization.get_all_organizations()
        org_map = {o['id']: o['name'] for o in all_orgs_data}

        # 接收单位选项
        receiver_options = []
        receiver_values = {}

        if is_sub_unit:
            # 基层单位：只能提交给上级（直属中层单位）
            for mid_id, info in parent_sub_units.items():
                if my_org_id in info['subs']:
                    receiver_options.append(f"上级: {info['name']}")
                    receiver_values[f"上级: {info['name']}"] = str(mid_id)
                    break

        elif is_middle_level:
            # 中层单位：可以提交给上级(局机关)、平级(其他中层单位)、下级(下属基层单位)
            receiver_options.append("── 提交给上级(局机关) ──")
            dept_options = [
                (1, "办公室"), (7, "财务处"), (10, "资产管理处"), (11, "劳动人事处"),
                (12, "科技处"), (2, "计划处"), (3, "设施管理处"), (4, "设施养护处"),
                (5, "建设管理处"), (6, "规划处"), (8, "规费管理处"), (9, "审计处")
            ]
            for dept_id, dept_name in dept_options:
                receiver_options.append(f"  → {dept_name}")
                receiver_values[f"  → {dept_name}"] = str(dept_id)

            receiver_options.append("── 提交给平级单位 ──")
            for mid_id, info in parent_sub_units.items():
                if mid_id != my_org_id:
                    receiver_options.append(f"  → {info['name']}")
                    receiver_values[f"  → {info['name']}"] = str(mid_id)

            if parent_sub_units[my_org_id]['subs']:
                receiver_options.append("── 提交给下属单位 ──")
                for sub_id in parent_sub_units[my_org_id]['subs']:
                    sub_name = org_map.get(sub_id, f'单位{sub_id}')
                    receiver_options.append(f"  → {sub_name}")
                    receiver_values[f"  → {sub_name}"] = str(sub_id)

        tk.Label(form_frame, text="收文单位:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.new_draft_receiver_var = tk.StringVar()
        if receiver_options:
            self.new_draft_receiver_var.set(receiver_options[0])
        receiver_combo = ttk.Combobox(form_frame, textvariable=self.new_draft_receiver_var,
                                       values=receiver_options, width=38, state="readonly")
        receiver_combo.grid(row=0, column=1, pady=8)

        tk.Label(form_frame, text="标题:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.new_draft_title = tk.Entry(form_frame, width=40)
        self.new_draft_title.grid(row=1, column=1, pady=8)

        tk.Label(form_frame, text="类型:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        self.new_draft_type = tk.StringVar(value="report")
        doc_type_combo = ttk.Combobox(form_frame, textvariable=self.new_draft_type, width=38)
        doc_type_combo['values'] = ('报告', '请示', '通知')
        doc_type_combo.grid(row=2, column=1, pady=8)

        tk.Label(form_frame, text="内容:").grid(row=3, column=0, padx=10, pady=8, sticky="ne")
        self.new_draft_content = tk.Text(form_frame, width=40, height=8)
        self.new_draft_content.grid(row=3, column=1, pady=8)

        # 附件
        tk.Label(form_frame, text="附件:").grid(row=4, column=0, padx=10, pady=8, sticky="e")
        self.new_draft_attachment = tk.StringVar()
        attach_entry = tk.Entry(form_frame, textvariable=self.new_draft_attachment, width=28)
        attach_entry.grid(row=4, column=1, pady=8, sticky="w", padx=(0, 5))

        def select_file():
            from tkinter import filedialog
            filename = filedialog.askopenfilename(title="选择附件", filetypes=[("所有文件", "*.*"), ("文档", "*.doc *.docx *.pdf"), ("图片", "*.jpg *.png")])
            if filename:
                self.new_draft_attachment.set(filename)

        tk.Button(form_frame, text="浏览", command=select_file, bg=self.COLORS['secondary'], fg="white",
                 width=8).grid(row=4, column=1, pady=8, sticky="e", padx=(0, 10))

        self.new_draft_receiver_values = receiver_values

        tk.Button(form_frame, text="保存草稿", command=self.save_new_draft,
                 bg=self.COLORS['primary'], fg="white").grid(row=5, column=1, pady=15)

    def save_new_draft(self):
        """保存新草稿"""
        title = self.new_draft_title.get().strip()
        content = self.new_draft_content.get(1.0, tk.END).strip()
        doc_type_cn = self.new_draft_type.get()
        attachment = self.new_draft_attachment.get()

        type_map = {'报告': 'report', '请示': 'request', '通知': 'notice'}
        doc_type = type_map.get(doc_type_cn, 'report')

        if not title or not content:
            messagebox.showwarning("提示", "请填写标题和内容")
            return

        # 获取收文单位
        selected = self.new_draft_receiver_var.get()
        receiver_org_ids = ''
        if hasattr(self, 'new_draft_receiver_values'):
            receiver_org_ids = self.new_draft_receiver_values.get(selected, '')

        from services.document_service import DocumentService
        data = {
            'title': title,
            'content': content,
            'doc_type': doc_type,
            'receiver_org_ids': receiver_org_ids,
            'is_official': 0,
            'attachment': attachment
        }
        DocumentService.create_document(data, self.user['id'], self.user['organization_id'])

        messagebox.showinfo("成功", "草稿已保存")
        self.show_draft_manage()

    def edit_selected_draft(self):
        """编辑选中的草稿"""
        selected = self.draft_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要编辑的草稿")
            return

        item = selected[0]
        values = self.draft_tree.item(item, 'values')
        doc_id = values[0]

        # 获取公文详情
        from services.document_service import DocumentService
        doc = DocumentService.get_document_by_id(doc_id)
        if not doc:
            messagebox.showerror("错误", "无法获取公文信息")
            return

        # 创建编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑草稿")
        dialog.geometry("600x500")

        # 表单
        tk.Label(dialog, text="标题:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        title_entry = tk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        title_entry.insert(0, doc.get('title', ''))

        tk.Label(dialog, text="类型:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        type_var = tk.StringVar(value=doc.get('doc_type', 'report'))
        type_combo = ttk.Combobox(dialog, textvariable=type_var, width=38)
        type_combo['values'] = ('report', 'request', 'notice')
        type_combo.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(dialog, text="内容:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        content_text = tk.Text(dialog, width=40, height=15)
        content_text.grid(row=2, column=1, padx=10, pady=10)
        content_text.insert(1.0, doc.get('content', ''))

        tk.Label(dialog, text="收文单位ID:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        receiver_entry = tk.Entry(dialog, width=40)
        receiver_entry.grid(row=3, column=1, padx=10, pady=10)
        receiver_entry.insert(0, doc.get('receiver_org_ids', ''))

        tk.Label(dialog, text="附件:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        attachment_var = tk.StringVar(value=doc.get('attachment', ''))
        tk.Entry(dialog, textvariable=attachment_var, width=30).grid(row=4, column=1, padx=10, pady=10, sticky="w")

        def save_edit():
            data = {
                'title': title_entry.get(),
                'doc_type': type_var.get(),
                'content': content_text.get(1.0, tk.END).strip(),
                'receiver_org_ids': receiver_entry.get(),
                'is_official': doc.get('is_official', 0),
                'attachment': attachment_var.get()
            }
            DocumentService.update_document(doc_id, data)
            dialog.destroy()
            self.refresh_draft_list()
            messagebox.showinfo("成功", "草稿已更新")

        tk.Button(dialog, text="保存", command=save_edit, bg=self.COLORS['primary'], fg="white").grid(row=5, column=1, pady=20)

    def refresh_draft_list(self):
        """刷新草稿列表"""
        for item in self.draft_tree.get_children():
            self.draft_tree.delete(item)

        if not hasattr(self, 'draft_all_org_ids'):
            return

        all_org_ids = self.draft_all_org_ids
        placeholders = ','.join(['%s'] * len(all_org_ids))

        # 获取所有组织映射
        from models.organization import Organization
        all_orgs = Organization.get_all_organizations()
        org_map = {o['id']: o['name'] for o in all_orgs}

        # 查询本单位及下属单位提交的草稿
        sql = f"""SELECT d.*, o.name as sender_name
                  FROM documents d
                  LEFT JOIN organizations o ON d.sender_org_id = o.id
                  WHERE d.sender_org_id IN ({placeholders}) AND d.status = 'draft'
                  ORDER BY d.create_date DESC"""
        docs = db.execute_query(sql, tuple(all_org_ids))

        type_map = {'notice': '通知', 'report': '报告', 'request': '请示'}
        status_map = {'draft': '草稿', 'pending': '待审核', 'published': '已发布', 'replied': '已回复'}

        for doc in docs:
            sender_name = doc.get('sender_name', org_map.get(doc.get('sender_org_id', ''), ''))
            self.draft_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], type_map.get(doc.get('doc_type', 'report'), doc.get('doc_type', '')),
                sender_name, doc.get('create_date', ''), status_map.get(doc.get('status', 'draft'), doc.get('status', ''))
            ))

    def publish_selected_draft(self):
        """发布选中的草稿"""
        selected = self.draft_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要发布的草稿")
            return

        item = selected[0]
        values = self.draft_tree.item(item, 'values')
        doc_id = values[0]

        if messagebox.askyesno("确认", "确定要发布这份公文吗？发布后接收方即可看到。"):
            from services.document_service import DocumentService
            DocumentService.publish_document(doc_id)
            self.refresh_draft_list()
            messagebox.showinfo("成功", "公文已发布")

    def delete_selected_draft(self):
        """删除选中的草稿"""
        selected = self.draft_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要删除的草稿")
            return

        item = selected[0]
        values = self.draft_tree.item(item, 'values')
        doc_id = values[0]

        if messagebox.askyesno("确认", "确定要删除这份草稿吗？"):
            from services.document_service import DocumentService
            DocumentService.delete_document(doc_id)
            self.refresh_draft_list()
            messagebox.showinfo("成功", "草稿已删除")

    def submit_research(self):
        """提交科研项目"""
        name = self.research_name.get().strip()
        budget = self.research_budget.get().strip()
        description = self.research_desc.get(1.0, tk.END).strip()

        if not name or not budget:
            messagebox.showwarning("提示", "请填写项目名称和预算金额")
            return

        try:
            budget_float = float(budget)
        except:
            messagebox.showwarning("提示", "请输入有效的预算金额")
            return

        ResearchService.create_project({
            'name': name,
            'budget': budget_float,
            'description': description
        }, self.user['id'], self.user['organization_id'])

        self.research_name.delete(0, tk.END)
        self.research_budget.delete(0, tk.END)
        self.research_desc.delete(1.0, tk.END)
        self.refresh_unit_research()
        messagebox.showinfo("成功", "科研项目已提交")

    def show_budget_apply(self):
        """显示预算申报"""
        self.clear_right_frame()

        my_org_id = self.user.get('organization_id', 0)

        # 判断是否为中层机关
        parent_sub_units = {
            22: list(range(61, 73)),  # 高速处下属: 61-72
            23: list(range(51, 61)),  # 道桥处下属: 51-60
            26: list(range(73, 80)),  # 研究院下属: 73-79
            27: [62, 91, 92, 93, 94, 95, 96, 97, 98],  # 设计院下属: 62, 91-98
            38: [63],  # 地铁处下属: 63
            39: [],    # 巡查处下属: 暂无
            40: []     # 执法总队下属: 暂无
        }
        is_parent = my_org_id in parent_sub_units

        # 判断是否为下属单位
        is_sub_unit = (51 <= my_org_id <= 60) or (61 <= my_org_id <= 72) or (73 <= my_org_id <= 79) or (81 <= my_org_id <= 90) or (86 <= my_org_id <= 88) or (101 <= my_org_id <= 110) or (my_org_id in [62, 63, 91, 92, 93, 94, 95, 96, 97, 98])

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)

        if is_parent:
            tk.Label(title_frame, text="下属单位预算申报", font=("Microsoft YaHei", 18, "bold"),
                    bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)
        else:
            tk.Label(title_frame, text="预算申报", font=("Microsoft YaHei", 18, "bold"),
                    bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        if is_sub_unit:
            # 下属单位只能由上级单位代为申报，显示提示
            info_card = self.create_card(self.right_frame, "申报说明")
            info_card.pack(fill=tk.X, padx=20, pady=10)
            tk.Label(info_card, text="您所属的下属单位，预算申报由上级单位（所属机关）统一管理。请联系上级单位办理预算申报。",
                    font=("Microsoft YaHei", 11), bg=self.COLORS['bg_white'],
                    fg=self.COLORS['warning'], wraplength=600).pack(padx=20, pady=20)
        else:
            # 申报表单（parent unit 或普通单位）
            form_card = self.create_card(self.right_frame, "申报预算")
            form_card.pack(fill=tk.X, padx=20, pady=10)

            form_frame = tk.Frame(form_card, bg=self.COLORS['bg_white'])
            form_frame.pack(padx=20, pady=15, fill=tk.X)

            tk.Label(form_frame, text="预算年度:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
            self.budget_year = tk.Entry(form_frame, width=40)
            self.budget_year.grid(row=0, column=1, pady=8)
            self.budget_year.insert(0, "2026")

            tk.Label(form_frame, text="预算金额:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
            self.budget_amount = tk.Entry(form_frame, width=40)
            self.budget_amount.grid(row=1, column=1, pady=8)

            tk.Label(form_frame, text="用途说明:").grid(row=2, column=0, padx=10, pady=8, sticky="ne")
            self.budget_purpose = tk.Text(form_frame, width=40, height=6)
            self.budget_purpose.grid(row=2, column=1, pady=8)

            tk.Button(form_frame, text="提交申报", command=self.submit_budget,
                     bg=self.COLORS['success'], fg="white").grid(row=3, column=1, pady=15)

        # 申报列表
        if is_parent:
            tk.Label(self.right_frame, text="下属单位申报:", font=("Microsoft YaHei", 11, "bold"),
                    bg=self.COLORS['bg_white']).pack(anchor="w", padx=20, pady=(10, 5))
        else:
            tk.Label(self.right_frame, text="我的申报:", font=("Microsoft YaHei", 11, "bold"),
                    bg=self.COLORS['bg_white']).pack(anchor="w", padx=20, pady=(10, 5))

        columns = ("ID", "年度", "金额", "申请单位", "申请时间", "状态")
        self.unit_budget_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.unit_budget_tree.heading(col, text=col)
            self.unit_budget_tree.column(col, width=100)

        self.unit_budget_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.refresh_unit_budget()

    def refresh_unit_budget(self):
        """刷新预算申报列表"""
        for item in self.unit_budget_tree.get_children():
            self.unit_budget_tree.delete(item)

        my_org_id = self.user.get('organization_id', 0)

        # 判断是否为中层机关
        parent_sub_units = {
            22: list(range(61, 73)),  # 高速处下属: 61-72
            23: list(range(51, 61)),  # 道桥处下属: 51-60
            26: list(range(73, 80)),  # 研究院下属: 73-79
            27: [62, 91, 92, 93, 94, 95, 96, 97, 98],  # 设计院下属: 62, 91-98
            38: [63],  # 地铁处下属: 63
            39: [],    # 巡查处下属: 暂无
            40: []     # 执法总队下属: 暂无
        }

        from models.organization import Organization
        all_orgs = Organization.get_all_organizations()
        org_map = {o['id']: o['name'] for o in all_orgs}

        if my_org_id in parent_sub_units:
            # 中层机关：查看所有下属单位的预算申报
            sub_ids = parent_sub_units[my_org_id]
            placeholders = ','.join(['%s'] * len(sub_ids))
            sql = f"""SELECT ba.*, o.name as org_name FROM budget_applications ba
                     LEFT JOIN organizations o ON ba.organization_id = o.id
                     WHERE ba.organization_id IN ({placeholders}) ORDER BY ba.apply_date DESC"""
            budgets = db.execute_query(sql, sub_ids)

            status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}
            for b in budgets:
                amount = b.get('amount', 0) or 0
                org_name = b.get('org_name', org_map.get(b.get('organization_id', 0), ''))
                self.unit_budget_tree.insert("", tk.END, values=(
                    b['id'], b.get('year', ''), f"{amount:.2f}", org_name, b.get('apply_date', ''),
                    status_map.get(b.get('status', 'pending'), b.get('status', ''))
                ))
        else:
            # 普通单位：只查看本单位预算申报
            sql = """SELECT ba.*, o.name as org_name FROM budget_applications ba
                     LEFT JOIN organizations o ON ba.organization_id = o.id
                     WHERE ba.organization_id = %s ORDER BY ba.apply_date DESC"""
            budgets = db.execute_query(sql, (my_org_id,))

            status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}
            for b in budgets:
                amount = b.get('amount', 0) or 0
                org_name = b.get('org_name', '')
                self.unit_budget_tree.insert("", tk.END, values=(
                    b['id'], b.get('year', ''), f"{amount:.2f}", org_name, b.get('apply_date', ''),
                    status_map.get(b.get('status', 'pending'), b.get('status', ''))
                ))

    def submit_budget(self):
        """提交预算申请"""
        year = self.budget_year.get().strip()
        amount = self.budget_amount.get().strip()
        purpose = self.budget_purpose.get(1.0, tk.END).strip()

        if not year or not amount:
            messagebox.showwarning("提示", "请填写年度和金额")
            return

        try:
            year_int = int(year)
            amount_float = float(amount)
        except:
            messagebox.showwarning("提示", "请输入有效的年度和金额")
            return

        BudgetService.create_application({
            'year': year_int,
            'amount': amount_float,
            'purpose': purpose,
            'type': '下属单位'
        }, self.user['organization_id'])

        self.budget_amount.delete(0, tk.END)
        self.budget_purpose.delete(1.0, tk.END)
        self.refresh_unit_budget()
        messagebox.showinfo("成功", "预算申请已提交")

    def show_profile(self):
        """显示个人中心"""
        self.clear_right_frame()

        tk.Label(self.right_frame, text="个人中心", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)

        # 信息卡片
        card = self.create_card(self.right_frame, "个人信息")
        card.pack(fill=tk.X, padx=20, pady=10)

        info_frame = tk.Frame(card, bg=self.COLORS['bg_white'])
        info_frame.pack(padx=20, pady=20)

        tk.Label(info_frame, text="用户名:", font=("Microsoft YaHei", 11)).grid(row=0, column=0, sticky="e", pady=5)
        tk.Label(info_frame, text=self.user['username'], font=("Microsoft YaHei", 11)).grid(row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(info_frame, text="姓名:", font=("Microsoft YaHei", 11)).grid(row=1, column=0, sticky="e", pady=5)
        tk.Label(info_frame, text=self.user['full_name'], font=("Microsoft YaHei", 11)).grid(row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(info_frame, text="角色:", font=("Microsoft YaHei", 11)).grid(row=2, column=0, sticky="e", pady=5)
        tk.Label(info_frame, text=self.get_role_name(), font=("Microsoft YaHei", 11)).grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # 修改密码 - 需申请审批
        pwd_card = self.create_card(self.right_frame, "申请修改密码")
        pwd_card.pack(fill=tk.X, padx=20, pady=10)

        pwd_frame = tk.Frame(pwd_card, bg=self.COLORS['bg_white'])
        pwd_frame.pack(padx=20, pady=20)

        tk.Label(pwd_frame, text="原密码:", font=("Microsoft YaHei", 11)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        old_pwd = tk.Entry(pwd_frame, show="*", width=25)
        old_pwd.grid(row=0, column=1, pady=5)

        tk.Label(pwd_frame, text="新密码:", font=("Microsoft YaHei", 11)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        new_pwd = tk.Entry(pwd_frame, show="*", width=25)
        new_pwd.grid(row=1, column=1, pady=5)

        tk.Label(pwd_frame, text="确认密码:", font=("Microsoft YaHei", 11)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        confirm_pwd = tk.Entry(pwd_frame, show="*", width=25)
        confirm_pwd.grid(row=2, column=1, pady=5)

        # 说明文字
        note_text = "说明：密码修改申请将提交至劳动人事处审批，审批通过后密码才会生效。"
        tk.Label(pwd_frame, text=note_text, font=("Microsoft YaHei", 9), fg="gray",
                wraplength=350, justify=tk.LEFT).grid(row=3, column=0, columnspan=2, pady=10)

        # 申请记录
        tk.Label(pwd_frame, text="我的申请记录:", font=("Microsoft YaHei", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 5))

        columns = ("申请时间", "状态", "审批时间")
        self.pwd_record_tree = ttk.Treeview(pwd_frame, columns=columns, show="headings", height=5)
        for col in columns:
            self.pwd_record_tree.heading(col, text=col)
            self.pwd_record_tree.column(col, width=100)
        self.pwd_record_tree.grid(row=5, column=0, columnspan=2, pady=5)

        def change_pwd():
            old_password = old_pwd.get()
            new_password = new_pwd.get()
            confirm_password = confirm_pwd.get()

            if not old_password or not new_password or not confirm_password:
                messagebox.showwarning("提示", "请填写所有密码字段")
                return

            if new_password != confirm_password:
                messagebox.showerror("错误", "新密码与确认密码不一致")
                return

            if len(new_password) < 6:
                messagebox.showwarning("提示", "新密码长度至少6位")
                return

            # 验证原密码是否正确
            import hashlib
            from models.user import User
            user = User.get_by_id(self.user['id'])
            old_hash = hashlib.sha256(old_password.encode()).hexdigest()
            if user['password'] != old_hash:
                messagebox.showerror("错误", "原密码错误")
                return

            # 提交申请到劳动人事处审批
            try:
                import hashlib
                new_hash = hashlib.sha256(new_password.encode()).hexdigest()
                sql = """INSERT INTO password_change_applications
                         (user_id, username, old_password, new_password, status, apply_date)
                         VALUES (%s, %s, %s, %s, 'pending', NOW())"""
                db.execute_update(sql, (self.user['id'], self.user['username'], old_hash, new_hash))

                messagebox.showinfo("成功", "密码修改申请已提交至劳动人事处，请等待审批。")
                old_pwd.delete(0, tk.END)
                new_pwd.delete(0, tk.END)
                confirm_pwd.delete(0, tk.END)
                self.refresh_pwd_records()
            except Exception as e:
                messagebox.showerror("错误", f"提交申请失败: {e}")

        tk.Button(pwd_frame, text="提交申请", command=change_pwd,
                 bg=self.COLORS['primary'], fg="white").grid(row=6, column=1, pady=10)

        # 刷新申请记录
        self.refresh_pwd_records()

    def refresh_pwd_records(self):
        """刷新密码修改申请记录"""
        if hasattr(self, 'pwd_record_tree'):
            for item in self.pwd_record_tree.get_children():
                self.pwd_record_tree.delete(item)

            try:
                sql = """SELECT apply_date, status, approve_date
                         FROM password_change_applications
                         WHERE user_id = %s ORDER BY apply_date DESC"""
                records = db.execute_query(sql, (self.user['id'],))

                status_map = {'pending': '待审批', 'approved': '已通过', 'rejected': '已拒绝'}
                for record in records:
                    status = status_map.get(record['status'], record['status'])
                    approve_date = record['approve_date'] if record['approve_date'] else '-'
                    self.pwd_record_tree.insert("", tk.END, values=(
                        record['apply_date'], status, approve_date
                    ))
            except Exception as e:
                print(f"加载密码修改记录失败: {e}")

    # ============== 中层单位业务功能方法 ==============

    def show_facility_management(self):
        """设施管理"""
        self._show_content_page("设施管理", "设施管理功能\n\n查看和管理本单位负责的市政设施...")

    def show_facility_maintenance(self):
        """养护工程"""
        self._show_content_page("养护工程", "养护工程管理\n\n管理养护工程项目和进度...")

    def show_emergency(self):
        """应急处置"""
        self._show_content_page("应急处置", "应急抢险管理\n\n应急预案和应急响应管理...")

    def show_research(self):
        """科研项目管理"""
        self._show_content_page("科研项目管理", "科研项目管理\n\n管理科研项目立项和进度...")

    def show_tech_service(self):
        """技术服务"""
        self._show_content_page("技术服务", "技术服务和检测\n\n提供技术咨询和工程质量检测服务...")

    def show_design(self):
        """工程设计"""
        self._show_content_page("工程设计", "工程设计管理\n\n市政工程设计管理...")

    def show_design_review(self):
        """方案审查"""
        self._show_content_page("方案审查", "设计方案审查\n\n审查设计方案...")

    def show_construction(self):
        """工程建设"""
        self._show_content_page("工程建设", "工程建设管理\n\n管理工程建设和施工...")

    def show_safety(self):
        """安全管理"""
        self._show_content_page("安全管理", "安全管理\n\n施工安全和生产安全管理...")

    def show_quality(self):
        """质量监督"""
        self._show_content_page("质量监督", "工程质量监督\n\n监督工程质量...")

    def show_operation(self):
        """运营管理"""
        self._show_content_page("运营管理", "地铁运营管理\n\n地铁运营和调度管理...")

    # ============== 巡查处和执法总队业务功能方法 ==============

    def show_inspection(self):
        """公路巡查"""
        self._show_content_page("公路巡查管理", "公路路政巡查管理\n\n负责公路巡查任务分配和执行...")

    def show_damage_report(self):
        """病害上报"""
        self._show_content_page("道路病害上报", "道路病害信息采集上报\n\n采集和上报道路病害信息...")

    def show_inspection_stats(self):
        """巡查统计"""
        self._show_content_page("巡查统计报表", "巡查工作统计报表\n\n巡查工作量和问题统计...")

    def show_enforcement(self):
        """路政执法"""
        self._show_content_page("路政执法", "路政违法行为查处\n\n查处路政违法案件...")

    def show_case_management(self):
        """案件管理"""
        self._show_content_page("路政案件管理", "路政案件处理\n\n路政案件登记和处理...")

    def show_enforcement_supervision(self):
        """执法监督"""
        self._show_content_page("行政执法监督", "行政执法监督\n\n监督路政执法工作规范...")

    # ============== 超治办业务功能方法 ==============

    def show_overload_control(self):
        """超限治理"""
        self._show_content_page("超限超载治理", "治理车辆超限超载\n\n超限车辆检查和处理...")

    def show_source_supervision(self):
        """源头监管"""
        self._show_content_page("货运源头监管", "货运源头监管\n\n对货运企业源头进行监管...")

    def show_overload_case(self):
        """案件处理"""
        self._show_content_page("超限违法案件处理", "超限违法案件处理\n\n超限违法案件登记和处理...")

    # ============== 公路养护工程处业务功能方法 ==============

    def show_maintenance_project(self):
        """养护工程"""
        self._show_content_page("公路养护工程", "公路养护工程管理\n\n养护工程计划制定和实施...")

    def show_facility_maintenance(self):
        """设施维护"""
        self._show_content_page("公路设施维护", "公路设施维护\n\n公路设施日常维护管理...")

    def show_emergency_maintenance(self):
        """应急养护"""
        self._show_content_page("公路应急养护", "公路应急养护抢修\n\n公路应急养护和抢修管理...")