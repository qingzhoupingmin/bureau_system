# -*- coding: utf-8 -*-
"""
统一处室窗口 - 根据不同处室显示相应业务功能
所有处室使用统一界面，在"业务办理"模块中显示各自的专业功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from services.asset_service import AssetService
from services.message_service import MessageService
from services.document_service import DocumentService
from services.research_service import ResearchService
from services.budget_service import BudgetService
from services.auth_service import AuthService
from db.connection import db


class UnifiedDepartmentWindow(MainWindow):
    """统一处室窗口"""

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

    def get_department_info(self):
        """获取当前处室的信息"""
        org_id = self.user.get('organization_id', 0)

        # 定义各处室的专业业务
        dept_business = {
            # 办公室
            1: {
                'name': '办公室',
                'business': [
                    ('公文管理', '公文创建、审核、发布流程'),
                    ('消息通知', '发送和接收系统消息'),
                    ('业务请示', '处理下级单位的业务请示'),
                ]
            },
            # 财务处
            7: {
                'name': '财务处',
                'business': [
                    ('预算审批', '审核各单位的预算申请'),
                    ('预算分配', '分配已批准的预算资金'),
                    ('预算统计', '查看预算执行统计报表'),
                ]
            },
            # 科技处
            12: {
                'name': '科技处',
                'business': [
                    ('科研项目管理', '管理科研项目立项和进度'),
                    ('科研经费管理', '管理和分配科研经费'),
                    ('申请审批', '审批科研相关申请'),
                ]
            },
            # 劳动人事处
            11: {
                'name': '劳动人事处',
                'business': [
                    ('人事管理', '管理人事档案'),
                    ('账号注册', '注册新用户账号'),
                    ('密码审批', '审批密码修改申请'),
                ]
            },
            # 资产管理处
            10: {
                'name': '资产管理处',
                'business': [
                    ('资产台账', '全局资产登记管理'),
                    ('资产调配', '跨单位资产调配审批'),
                    ('资产统计', '全局资产统计分析'),
                ]
            },
            # 其他处室的专业业务
            2: {'name': '计划处', 'business': [('项目计划管理', '编制和管理年度项目计划'), ('立项审批', '审批项目立项申请'), ('投资管理', '管理项目投资')]},
            3: {'name': '设施管理处', 'business': [('设施台账', '管理市政设施档案'), ('维护计划', '制定设施维护计划'), ('设施查询', '查询设施状态信息')]},
            4: {'name': '设施养护处', 'business': [('养护工程', '管理养护工程项目'), ('进度跟踪', '跟踪养护工程进度'), ('质量监督', '监督养护工程质量')]},
            5: {'name': '建设管理处', 'business': [('工程建设', '管理市政工程建设'), ('招投标管理', '管理工程招投标'), ('进度跟踪', '跟踪工程进度')]},
            6: {'name': '规划处', 'business': [('规划编制', '编制市政工程规划'), ('方案审查', '审查规划方案'), ('规划查询', '查询规划信息')]},
            8: {'name': '规费管理处', 'business': [('规费标准', '管理和制定规费标准'), ('征收管理', '管理规费征收工作'), ('统计报表', '生成规费统计报表')]},
            9: {'name': '审计处', 'business': [('审计计划', '制定年度审计计划'), ('审计执行', '执行审计工作'), ('问题整改', '监督问题整改')]},
            13: {'name': '安全保卫处', 'business': [('安全管理', '管理安全生产工作'), ('应急预案', '制定应急预案'), ('保卫管理', '管理保卫工作')]},
            14: {'name': '法规处', 'business': [('法规管理', '管理法规文件'), ('政策研究', '研究政策法规'), ('执法监督', '监督执法工作')]},
            15: {'name': '党委办公室', 'business': [('党委事务', '处理党委日常工作'), ('党建工作', '管理党建工作'), ('文件起草', '起草党委文件')]},
            16: {'name': '纪检委', 'business': [('纪检监察', '开展纪检监察工作'), ('案件查处', '查处违纪案件'), ('廉政教育', '开展廉政教育')]},
            17: {'name': '宣传部', 'business': [('宣传教育', '开展宣传教育工作'), ('精神文明', '管理精神文明建设'), ('新闻宣传', '管理新闻宣传工作')]},
            18: {'name': '组织部', 'business': [('干部管理', '管理干部选拔任用'), ('党员管理', '管理党员组织关系'), ('统战工作', '开展统战工作')]},
            19: {'name': '老干部处', 'business': [('老干部服务', '服务离退休干部'), ('待遇落实', '落实老干部待遇'), ('活动组织', '组织老干部活动')]},
        }

        # 默认处室信息
        default_info = {
            'name': '处室',
            'business': [('待开发', '功能开发中')]
        }

        return dept_business.get(org_id, default_info)

    def create_left_sidebar(self):
        """创建左侧导航栏"""
        sidebar = tk.Frame(self.main_frame, bg=self.COLORS['primary'], width=200)
        self.paned.add(sidebar, minsize=200)

        # 获取处室信息
        dept_info = self.get_department_info()
        dept_name = dept_info['name']

        # 导航标题
        nav_title = tk.Label(sidebar, text=dept_name, font=("Microsoft YaHei", 14, "bold"),
                            bg=self.COLORS['primary'], fg="white")
        nav_title.pack(pady=20)

        # 统一导航按钮 - 所有处室完全一样
        nav_items = [
            ("单位概况", self.show_overview),
            ("业务办理", self.show_business),
            ("部门资产", self.show_assets),
            ("资产申请", self.show_asset_apply),
            ("消息通知", self.show_messages),
            ("个人中心", self.show_profile),
        ]

        for text, command in nav_items:
            btn = tk.Button(sidebar, text=text, font=("Microsoft YaHei", 11),
                           bg=self.COLORS['secondary'], fg="white",
                           relief=tk.FLAT, cursor="hand2",
                           command=command)
            btn.pack(fill=tk.X, padx=15, pady=5)

    def clear_right_frame(self):
        """清空右侧内容区"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_overview(self):
        """显示单位概况"""
        self.clear_right_frame()
        from views.organization_overview import OrganizationOverview
        overview = OrganizationOverview(self.right_frame, self.COLORS)
        overview.show()

    def show_business(self):
        """显示业务办理 - 根据不同处室显示不同专业功能"""
        self.clear_right_frame()

        # 获取当前处室的业务信息
        dept_info = self.get_department_info()
        dept_name = dept_info['name']
        business_list = dept_info['business']

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text=f"{dept_name} - 业务办理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 业务功能卡片区域
        business_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_light'])
        business_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建业务卡片（每行3个）
        for i, (business_name, business_desc) in enumerate(business_list):
            row = i // 3
            col = i % 3

            # 业务卡片
            card_frame = tk.Frame(business_frame, bg=self.COLORS['bg_secondary'],
                                 relief=tk.RAISED, bd=1)
            card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # 业务名称
            name_label = tk.Label(card_frame, text=business_name,
                                 font=("Microsoft YaHei", 12, "bold"),
                                 bg=self.COLORS['bg_secondary'],
                                 fg=self.COLORS['primary'])
            name_label.pack(pady=(15, 5))

            # 业务描述
            desc_label = tk.Label(card_frame, text=business_desc,
                                 font=("Microsoft YaHei", 9),
                                 bg=self.COLORS['bg_secondary'],
                                 fg=self.COLORS['text_secondary'],
                                 wraplength=200)
            desc_label.pack(pady=(0, 10))

            # 操作按钮
            btn_frame = tk.Frame(card_frame, bg=self.COLORS['bg_secondary'])
            btn_frame.pack(pady=(0, 15))

            btn = tk.Button(btn_frame, text="进入办理",
                           bg=self.COLORS['primary'], fg="white",
                           font=("Microsoft YaHei", 9),
                           relief=tk.FLAT,
                           command=lambda name=business_name: self.handle_business(name))
            btn.pack()

        # 配置网格权重
        for i in range(3):
            business_frame.grid_columnconfigure(i, weight=1)

    def handle_business(self, business_name):
        """处理业务办理 - 所有处室统一跳转到对应页面"""
        # 统一根据业务名称显示页面
        method_map = {
            '公文管理': self.show_documents,
            '消息通知': self.show_messages,
            '业务请示': self.show_requests,
            '预算审批': self.show_budget_approvals,
            '预算分配': self.show_budget_allocation,
            '预算统计': self.show_budget_statistics,
            '科研项目管理': self.show_projects,
            '科研经费管理': self.show_funds,
            '申请审批': self.show_approvals,
            '账号注册': self.show_register_account,
            '密码审批': self.show_password_approvals,
            '人事管理': self.show_personnel_management,
            '资产台账': self.show_asset_ledger,
            '资产调配': self.show_asset_allocation,
            '资产统计': self.show_asset_statistics,
        }

        if business_name in method_map:
            method_map[business_name]()
        else:
            # 其他业务显示通用详情页
            self.show_business_detail(business_name)

    def show_business_detail(self, business_name):
        """显示业务详情（通用）"""
        self.clear_right_frame()

        # 获取处室信息
        dept_info = self.get_department_info()
        dept_name = dept_info['name']

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text=f"{dept_name} - {business_name}",
                font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 提示信息
        info_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_light'])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(info_frame,
                text=f"{business_name} 功能正在开发中\n\n{dept_name} 的业务流程将在此处实现。",
                font=("Microsoft YaHei", 12),
                bg=self.COLORS['bg_light'],
                fg=self.COLORS['text_secondary']).pack()

    def show_assets(self):
        """显示部门资产 - 所有处室统一界面"""
        self._show_content_page("部门资产")

    def show_asset_apply(self):
        """显示资产申请 - 所有处室统一界面"""
        self._show_content_page("资产申请")

    def show_messages(self):
        """显示消息通知 - 所有处室统一界面"""
        self._show_content_page("消息通知")

    def show_documents(self):
        """显示公文管理"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="公文管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 公文列表
        columns = ("ID", "标题", "类型", "状态", "创建时间")
        self.doc_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.doc_tree.heading(col, text=col)
            self.doc_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=scrollbar.set)

        self.doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮栏
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="新建公文", command=self.create_document,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_document,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_documents,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_documents()

    def refresh_documents(self):
        """刷新公文列表"""
        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)

        docs = DocumentService.get_all_documents()
        status_map = {'draft': '草稿', 'pending': '待审核', 'published': '已发布', 'replied': '已回复'}

        for doc in docs:
            self.doc_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], doc.get('doc_type', ''),
                status_map.get(doc.get('status', 'draft'), doc.get('status', '')),
                doc.get('create_date', '')
            ))

    def create_document(self):
        """创建新公文"""
        dialog = tk.Toplevel(self.root)
        dialog.title("新建公文")
        dialog.geometry("500x400")

        tk.Label(dialog, text="标题:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        title_entry = tk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, pady=5)

        tk.Label(dialog, text="类型:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        doc_type_var = tk.StringVar(value="通知")
        tk.Combobox(dialog, textvariable=doc_type_var, values=["通知", "决定", "批复", "报告", "请示"],
                   width=38).grid(row=1, column=1, pady=5)

        tk.Label(dialog, text="内容:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
        content_text = tk.Text(dialog, width=40, height=15)
        content_text.grid(row=2, column=1, pady=5)

        def submit():
            if not title_entry.get().strip():
                messagebox.showwarning("提示", "请输入公文标题")
                return

            DocumentService.create_document(
                title_entry.get().strip(),
                content_text.get(1.0, tk.END).strip(),
                self.user['id'],
                self.user['organization_id'],
                doc_type_var.get()
            )

            self.refresh_documents()
            dialog.destroy()
            messagebox.showinfo("成功", "公文创建成功")

        tk.Button(dialog, text="提交", command=submit, bg=self.COLORS['primary'], fg="white").grid(row=3, column=1, pady=20)

    def view_document(self):
        """查看公文详情"""
        selection = self.doc_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要查看的公文")
            return

        item = self.doc_tree.item(selection[0])
        doc_id = item['values'][0]

        doc = DocumentService.get_document_by_id(doc_id)
        if not doc:
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title("公文详情")
        detail_window.geometry("600x400")

        tk.Label(detail_window, text=doc['title'], font=("Microsoft YaHei", 14, "bold")).pack(pady=10)
        info_text = f"类型: {doc.get('doc_type', '')}\n状态: {doc.get('status', '')}\n创建时间: {doc.get('create_date', '')}"
        tk.Label(detail_window, text=info_text, font=("Microsoft YaHei", 10)).pack(anchor="w", padx=20)

        tk.Label(detail_window, text="内容:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        content_text = tk.Text(detail_window, wrap=tk.WORD, height=15)
        content_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        content_text.insert(1.0, doc.get('content', ''))
        content_text.config(state=tk.DISABLED)

    def show_messages(self):
        """显示消息通知"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="消息通知", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 消息列表
        columns = ("ID", "标题", "类型", "发送人", "发送时间")
        self.msg_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.msg_tree.heading(col, text=col)
            self.msg_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.msg_tree.yview)
        self.msg_tree.configure(yscrollcommand=scrollbar.set)

        self.msg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮栏
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="发送消息", command=self.send_message,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_message,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_messages,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_messages()

    def refresh_messages(self):
        """刷新消息列表"""
        for item in self.msg_tree.get_children():
            self.msg_tree.delete(item)

        # 获取当前用户所在组织的消息
        org_id = self.user.get('organization_id', 0)
        messages = MessageService.get_messages_by_org(org_id)
        type_map = {'official': '局名义通知', 'business': '业务通知', 'request': '业务请示'}

        for msg in messages:
            self.msg_tree.insert("", tk.END, values=(
                msg['id'], msg['title'],
                type_map.get(msg.get('message_type', 'business'), msg.get('message_type', '')),
                msg.get('sender_name', ''), msg.get('create_date', '')
            ))

    def send_message(self):
        """发送消息"""
        dialog = tk.Toplevel(self.root)
        dialog.title("发送消息")
        dialog.geometry("500x400")

        tk.Label(dialog, text="标题:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        title_entry = tk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, pady=5)

        tk.Label(dialog, text="类型:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        msg_type_var = tk.StringVar(value="business")
        tk.Combobox(dialog, textvariable=msg_type_var, values=[("business", "业务通知"), ("official", "局名义通知")],
                   width=38).grid(row=1, column=1, pady=5)

        tk.Label(dialog, text="内容:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
        content_text = tk.Text(dialog, width=40, height=12)
        content_text.grid(row=2, column=1, pady=5)

        def submit():
            if not title_entry.get().strip():
                messagebox.showwarning("提示", "请输入消息标题")
                return

            MessageService.send_message(
                title_entry.get().strip(),
                content_text.get(1.0, tk.END).strip(),
                self.user['id'],
                self.user['organization_id'],
                msg_type_var.get()
            )

            self.refresh_messages()
            dialog.destroy()
            messagebox.showinfo("成功", "发送成功")

        tk.Button(dialog, text="发送", command=submit, bg=self.COLORS['primary'], fg="white").grid(row=3, column=1, pady=20)

    def view_message(self):
        """查看消息详情"""
        selection = self.msg_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要查看的消息")
            return

        item = self.msg_tree.item(selection[0])
        msg_id = item['values'][0]

        msg = MessageService.get_message_by_id(msg_id)
        if not msg:
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title("消息详情")
        detail_window.geometry("500x350")

        tk.Label(detail_window, text=msg['title'], font=("Microsoft YaHei", 14, "bold")).pack(pady=10)
        info_text = f"发送人: {msg.get('sender_name', '')}\n发送时间: {msg.get('create_date', '')}"
        tk.Label(detail_window, text=info_text, font=("Microsoft YaHei", 10)).pack(anchor="w", padx=20)

        tk.Label(detail_window, text="内容:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        content_text = tk.Text(detail_window, wrap=tk.WORD, height=12)
        content_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        content_text.insert(1.0, msg.get('content', ''))
        content_text.config(state=tk.DISABLED)

    def show_requests(self):
        """显示业务请示"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="业务请示", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 请示列表
        columns = ("ID", "标题", "发送单位", "发送时间", "状态")
        self.req_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.req_tree.heading(col, text=col)
            self.req_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.req_tree.yview)
        self.req_tree.configure(yscrollcommand=scrollbar.set)

        self.req_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(toolbar, text="查看详情", command=self.view_request_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="回复", command=self.reply_request,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="刷新", command=self.refresh_requests,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_requests()

    def refresh_requests(self):
        """刷新请示列表"""
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)

        sql = """SELECT m.*, o.name as org_name
                 FROM messages m
                 LEFT JOIN organizations o ON m.sender_org_id = o.id
                 WHERE m.message_type = 'request'
                 ORDER BY m.create_date DESC"""
        requests = db.execute_query(sql)

        for req in requests:
            self.req_tree.insert("", tk.END, values=(
                req['id'], req['title'],
                req.get('org_name', ''), req.get('create_date', ''), '待处理'
            ))

    def view_request_detail(self):
        """查看请示详情"""
        selection = self.req_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要查看的请示")
            return

        item = self.req_tree.item(selection[0])
        msg_id = item['values'][0]

        sql = """SELECT m.*, o.name as org_name, u.full_name as sender_name
                 FROM messages m
                 LEFT JOIN organizations o ON m.sender_org_id = o.id
                 LEFT JOIN users u ON m.sender_id = u.id
                 WHERE m.id = %s"""
        msg = db.execute_query(sql, (msg_id,))

        if msg:
            msg = msg[0]
            detail_window = tk.Toplevel(self.root)
            detail_window.title("请示详情")
            detail_window.geometry("600x400")

            tk.Label(detail_window, text=msg['title'], font=("Microsoft YaHei", 14, "bold")).pack(pady=10)
            tk.Label(detail_window, text=f"发送单位: {msg.get('org_name', '')}").pack(anchor="w", padx=20)
            tk.Label(detail_window, text=f"发送人: {msg.get('sender_name', '')}").pack(anchor="w", padx=20)
            tk.Label(detail_window, text=f"发送时间: {msg.get('create_date', '')}").pack(anchor="w", padx=20)

            tk.Label(detail_window, text="内容:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
            content_text = tk.Text(detail_window, wrap=tk.WORD, height=12)
            content_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            content_text.insert(1.0, msg.get('content', ''))
            content_text.config(state=tk.DISABLED)

    def reply_request(self):
        """回复请示"""
        selection = self.req_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要回复的请示")
            return

        item = self.req_tree.item(selection[0])
        msg_id = item['values'][0]

        dialog = tk.Toplevel(self.root)
        dialog.title("回复请示")
        dialog.geometry("500x300")

        tk.Label(dialog, text="回复内容:").grid(row=0, column=0, padx=10, pady=10, sticky="ne")
        reply_text = tk.Text(dialog, width=40, height=12)
        reply_text.grid(row=0, column=1, padx=10, pady=10)

        def submit():
            if not reply_text.get(1.0, tk.END).strip():
                messagebox.showwarning("提示", "请输入回复内容")
                return

            sql = """INSERT INTO message_replies (message_id, reply_user_id, reply_org_id, content, reply_date)
                     VALUES (%s, %s, %s, %s, NOW())"""
            db.execute_update(sql, (
                msg_id,
                self.user['id'],
                self.user['organization_id'],
                reply_text.get(1.0, tk.END).strip()
            ))

            dialog.destroy()
            messagebox.showinfo("成功", "回复成功")

        tk.Button(dialog, text="提交回复", command=submit, bg=self.COLORS['primary'], fg="white").grid(row=1, column=1, pady=10)

    def show_projects(self):
        """显示科研项目管理 - 所有处室统一界面"""
        self._show_content_page("科研项目管理")

    def show_funds(self):
        """显示科研经费管理 - 所有处室统一界面"""
        self._show_content_page("科研经费管理")

    def show_approvals(self):
        """显示申请审批 - 所有处室统一界面"""
        self._show_content_page("申请审批")

    def show_budget_approvals(self):
        """显示预算审批"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="预算审批", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 待审批列表
        columns = ("ID", "申请单位", "年度", "预算金额", "申请时间", "状态")
        self.budget_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=scrollbar.set)

        self.budget_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_budget_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="批准", command=self.approve_budget,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="拒绝", command=self.reject_budget,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_budget_approvals,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_budget_approvals()

    def refresh_budget_approvals(self):
        """刷新预算审批列表"""
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)

        budgets = BudgetService.get_all_applications({'status': 'pending'})
        status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}

        for budget in budgets:
            amount = budget.get('amount', 0) or 0
            self.budget_tree.insert("", tk.END, values=(
                budget['id'], budget.get('org_name', ''), budget.get('year', ''),
                f"{amount:.2f}", budget.get('apply_date', ''),
                status_map.get(budget.get('status', 'pending'), budget.get('status', ''))
            ))

    def view_budget_detail(self):
        """查看预算详情"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要查看的预算申请")
            return

        item = self.budget_tree.item(selection[0])
        budget_id = item['values'][0]

        budget = BudgetService.get_application_by_id(budget_id)
        if not budget:
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title("预算申请详情")
        detail_window.geometry("600x400")

        tk.Label(detail_window, text=f"{budget.get('year', '')}年度预算申请",
                font=("Microsoft YaHei", 14, "bold")).pack(pady=10)

        info_frame = tk.Frame(detail_window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        amount = budget.get('amount', 0) or 0
        tk.Label(info_frame, text=f"申请单位: {budget.get('org_name', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"预算金额: {amount:.2f} 元", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"申请时间: {budget.get('apply_date', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)

        tk.Label(info_frame, text="申请理由:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", pady=(10, 5))
        desc_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
        desc_text.pack(fill=tk.BOTH, expand=True)
        desc_text.insert(1.0, budget.get('description', ''))
        desc_text.config(state=tk.DISABLED)

    def approve_budget(self):
        """批准预算"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要批准的预算申请")
            return

        item = self.budget_tree.item(selection[0])
        budget_id = item['values'][0]
        status = item['values'][5]

        if status != '待审批':
            messagebox.showwarning("提示", "该申请已处理")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("批准预算")
        dialog.geometry("400x200")

        tk.Label(dialog, text="审批意见:").pack(anchor="w", padx=20, pady=10)
        comment_text = tk.Text(dialog, width=40, height=6)
        comment_text.pack(fill=tk.X, padx=20, pady=5)

        def submit():
            comment = comment_text.get(1.0, tk.END).strip()
            BudgetService.approve_application(budget_id, self.user['id'], comment)
            dialog.destroy()
            self.refresh_budget_approvals()
            messagebox.showinfo("成功", "已批准该预算申请")

        tk.Button(dialog, text="确认批准", command=submit, bg=self.COLORS['success'], fg="white").pack(pady=10)

    def reject_budget(self):
        """拒绝预算"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要拒绝的预算申请")
            return

        item = self.budget_tree.item(selection[0])
        budget_id = item['values'][0]
        status = item['values'][5]

        if status != '待审批':
            messagebox.showwarning("提示", "该申请已处理")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("拒绝预算")
        dialog.geometry("400x200")

        tk.Label(dialog, text="拒绝原因:").pack(anchor="w", padx=20, pady=10)
        comment_text = tk.Text(dialog, width=40, height=6)
        comment_text.pack(fill=tk.X, padx=20, pady=5)

        def submit():
            comment = comment_text.get(1.0, tk.END).strip()
            if not comment:
                messagebox.showwarning("提示", "请输入拒绝原因")
                return
            BudgetService.reject_application(budget_id, self.user['id'], comment)
            dialog.destroy()
            self.refresh_budget_approvals()
            messagebox.showinfo("成功", "已拒绝该预算申请")

        tk.Button(dialog, text="确认拒绝", command=submit, bg=self.COLORS['accent'], fg="white").pack(pady=10)

    def show_budget_allocation(self):
        """显示预算分配"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="预算分配", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        columns = ("ID", "申请单位", "年度", "预算金额", "已分配", "申请时间")
        self.alloc_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.alloc_tree.heading(col, text=col)
            self.alloc_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.alloc_tree.yview)
        self.alloc_tree.configure(yscrollcommand=scrollbar.set)

        self.alloc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_allocations,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_allocations()

    def refresh_allocations(self):
        """刷新分配列表"""
        for item in self.alloc_tree.get_children():
            self.alloc_tree.delete(item)

        budgets = BudgetService.get_all_applications({'status': 'approved'})

        for budget in budgets:
            amount = budget.get('amount', 0) or 0
            self.alloc_tree.insert("", tk.END, values=(
                budget['id'], budget.get('org_name', ''), budget.get('year', ''),
                f"{amount:.2f}", "0.00", budget.get('apply_date', '')
            ))

    def show_budget_statistics(self):
        """显示预算统计"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="预算统计", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        search_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(search_frame, text="年度:").pack(side=tk.LEFT, padx=5)
        self.stat_year_entry = tk.Entry(search_frame, width=10)
        self.stat_year_entry.pack(side=tk.LEFT, padx=5)
        self.stat_year_entry.insert(0, "2026")
        tk.Button(search_frame, text="查询", command=self.load_statistics,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.stat_text = tk.Text(self.right_frame, font=("Consolas", 12), wrap=tk.WORD)
        self.stat_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.load_statistics()

    def load_statistics(self):
        """加载统计信息"""
        year = self.stat_year_entry.get().strip()
        stats = BudgetService.get_statistics(year if year else None)

        total = 0
        text = f"\n预算统计报表\n================================\n\n"

        if year:
            text += f"年度: {year}\n\n"
        else:
            text += "年度: 全部\n\n"

        text += "按单位预算统计:\n"
        text += "-" * 40 + "\n"

        for item in stats:
            org_name = item.get('org_name', '未知')
            amount = item.get('total', 0) or 0
            total += amount
            text += f"{org_name}: {amount:.2f} 元\n"

        text += "-" * 40 + "\n"
        text += f"预算总计: {total:.2f} 元\n"

        all_budgets = BudgetService.get_all_applications()
        status_stats = {'pending': 0, 'approved': 0, 'rejected': 0}
        for b in all_budgets:
            status = b.get('status', 'pending')
            if status in status_stats:
                status_stats[status] += 1

        text += f"""
按状态统计:
  待审批: {status_stats['pending']} 个
  已批准: {status_stats['approved']} 个
  已拒绝: {status_stats['rejected']} 个
"""

        self.stat_text.delete(1.0, tk.END)
        self.stat_text.insert(1.0, text)

    def show_projects(self):
        """显示科研项目管理"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="科研项目管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        columns = ("ID", "项目名称", "申请单位", "预算金额", "申请时间", "状态")
        self.project_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=scrollbar.set)

        self.project_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_project_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_projects,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_projects()

    def refresh_projects(self):
        """刷新科研项目列表"""
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        projects = ResearchService.get_all_projects({})
        status_map = {'draft': '草稿', 'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}

        for project in projects:
            budget = project.get('budget', 0) or 0
            self.project_tree.insert("", tk.END, values=(
                project['id'], project['name'],
                project.get('org_name', ''), f"{budget:.2f}",
                project.get('apply_date', ''),
                status_map.get(project.get('status', 'draft'), project.get('status', ''))
            ))

    def view_project_detail(self):
        """查看项目详情"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要查看的项目")
            return

        item = self.project_tree.item(selection[0])
        project_id = item['values'][0]

        project = ResearchService.get_project_by_id(project_id)
        if not project:
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title("项目详情")
        detail_window.geometry("600x400")

        tk.Label(detail_window, text=project['name'], font=("Microsoft YaHei", 14, "bold")).pack(pady=10)

        info_frame = tk.Frame(detail_window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        budget = project.get('budget', 0) or 0
        tk.Label(info_frame, text=f"申请单位: {project.get('org_name', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"申请人: {project.get('applicant_name', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"预算金额: {budget:.2f} 元", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"申请时间: {project.get('apply_date', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)

        tk.Label(info_frame, text="项目描述:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", pady=(10, 5))
        desc_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
        desc_text.pack(fill=tk.BOTH, expand=True)
        desc_text.insert(1.0, project.get('description', ''))
        desc_text.config(state=tk.DISABLED)

    def show_funds(self):
        """显示科研经费管理"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="科研经费管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        columns = ("ID", "项目名称", "申请单位", "预算金额", "状态")
        self.fund_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.fund_tree.heading(col, text=col)
            self.fund_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.fund_tree.yview)
        self.fund_tree.configure(yscrollcommand=scrollbar.set)

        self.fund_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_funds,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_funds()

    def refresh_funds(self):
        """刷新经费列表"""
        for item in self.fund_tree.get_children():
            self.fund_tree.delete(item)

        projects = ResearchService.get_all_projects({})
        status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}

        for project in projects:
            budget = project.get('budget', 0) or 0
            self.fund_tree.insert("", tk.END, values=(
                project['id'], project['name'],
                project.get('org_name', ''), f"{budget:.2f}",
                status_map.get(project.get('status', 'pending'), project.get('status', ''))
            ))

    def show_approvals(self):
        """显示申请审批 - 科技处"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="申请审批", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 待审批列表
        columns = ("ID", "项目名称", "申请单位", "预算金额", "申请时间", "状态")
        self.approval_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.approval_tree.heading(col, text=col)
            self.approval_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.approval_tree.yview)
        self.approval_tree.configure(yscrollcommand=scrollbar.set)

        self.approval_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_project_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="批准", command=self.approve_project,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="拒绝", command=self.reject_project,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_approvals,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_approvals()

    def refresh_approvals(self):
        """刷新审批列表"""
        for item in self.approval_tree.get_children():
            self.approval_tree.delete(item)

        projects = ResearchService.get_all_projects({'status': 'pending'})

        for project in projects:
            budget = project.get('budget', 0) or 0
            self.approval_tree.insert("", tk.END, values=(
                project['id'], project['name'],
                project.get('org_name', ''), f"{budget:.2f}",
                project.get('apply_date', ''), '待审批'
            ))

    def approve_project(self):
        """批准项目"""
        selection = self.approval_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要批准的项目")
            return

        item = self.approval_tree.item(selection[0])
        project_id = item['values'][0]

        dialog = tk.Toplevel(self.root)
        dialog.title("批准项目")
        dialog.geometry("400x200")

        tk.Label(dialog, text="审批意见:").pack(anchor="w", padx=20, pady=10)
        comment_text = tk.Text(dialog, width=40, height=6)
        comment_text.pack(fill=tk.X, padx=20, pady=5)

        def submit():
            comment = comment_text.get(1.0, tk.END).strip()
            ResearchService.approve_project(project_id, self.user['id'], comment)
            dialog.destroy()
            self.refresh_approvals()
            messagebox.showinfo("成功", "已批准该项目")

        tk.Button(dialog, text="确认批准", command=submit, bg=self.COLORS['success'], fg="white").pack(pady=10)

    def reject_project(self):
        """拒绝项目"""
        selection = self.approval_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要拒绝的项目")
            return

        item = self.approval_tree.item(selection[0])
        project_id = item['values'][0]

        dialog = tk.Toplevel(self.root)
        dialog.title("拒绝项目")
        dialog.geometry("400x200")

        tk.Label(dialog, text="拒绝原因:").pack(anchor="w", padx=20, pady=10)
        comment_text = tk.Text(dialog, width=40, height=6)
        comment_text.pack(fill=tk.X, padx=20, pady=5)

        def submit():
            comment = comment_text.get(1.0, tk.END).strip()
            if not comment:
                messagebox.showwarning("提示", "请输入拒绝原因")
                return
            ResearchService.reject_project(project_id, self.user['id'], comment)
            dialog.destroy()
            self.refresh_approvals()
            messagebox.showinfo("成功", "已拒绝该项目")

        tk.Button(dialog, text="确认拒绝", command=submit, bg=self.COLORS['accent'], fg="white").pack(pady=10)

    def show_register_account(self):
        """显示账号注册 - 劳动人事处"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="账号注册", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 注册表单
        form_card = self.create_card(self.right_frame, "新用户注册")
        form_card.pack(fill=tk.X, padx=20, pady=10)

        form_frame = tk.Frame(form_card, bg=self.COLORS['bg_white'])
        form_frame.pack(padx=20, pady=20)

        tk.Label(form_frame, text="用户名:", font=("Microsoft YaHei", 11)).grid(row=0, column=0, sticky="e", pady=5)
        username_entry = tk.Entry(form_frame, width=25)
        username_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="密码:", font=("Microsoft YaHei", 11)).grid(row=1, column=0, sticky="e", pady=5)
        password_entry = tk.Entry(form_frame, show="*", width=25)
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="姓名:", font=("Microsoft YaHei", 11)).grid(row=2, column=0, sticky="e", pady=5)
        fullname_entry = tk.Entry(form_frame, width=25)
        fullname_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="组织:", font=("Microsoft YaHei", 11)).grid(row=3, column=0, sticky="e", pady=5)
        org_var = tk.StringVar()
        from models.organization import Organization
        all_orgs = Organization.get_all_organizations()
        org_options = [f"{o['id']}: {o['name']}" for o in all_orgs[:20]]
        tk.Combobox(form_frame, textvariable=org_var, values=org_options, width=23).grid(row=3, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="角色:", font=("Microsoft YaHei", 11)).grid(row=4, column=0, sticky="e", pady=5)
        role_var = tk.StringVar(value="unit_user")
        tk.Combobox(form_frame, textvariable=role_var, values=[
            ("unit_user", "下属单位"),
            ("sub_unit_user", "基层单位"),
            ("office_staff", "办公室"),
            ("tech_staff", "科技处"),
            ("finance_staff", "财务处"),
        ], width=23).grid(row=4, column=1, padx=10, pady=5)

        def submit():
            if not username_entry.get() or not password_entry.get() or not fullname_entry.get():
                messagebox.showwarning("提示", "请填写完整信息")
                return

            org_id = int(org_var.get().split(":")[0]) if org_var.get() else 0
            role = role_var.get()

            from models.user import User
            try:
                User.create_user(username_entry.get(), password_entry.get(), role, org_id, fullname_entry.get())
                messagebox.showinfo("成功", "用户创建成功")
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                fullname_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("错误", f"创建失败: {e}")

        tk.Button(form_frame, text="注册", command=submit, bg=self.COLORS['primary'], fg="white").grid(row=5, column=1, pady=15)

    def show_password_approvals(self):
        """显示密码审批 - 劳动人事处"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="密码审批", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        columns = ("ID", "用户名", "申请时间", "状态")
        self.pwd_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.pwd_tree.heading(col, text=col)
            self.pwd_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.pwd_tree.yview)
        self.pwd_tree.configure(yscrollcommand=scrollbar.set)

        self.pwd_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="批准", command=self.approve_password,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="拒绝", command=self.reject_password,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_password_approvals,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_password_approvals()

    def refresh_password_approvals(self):
        """刷新密码审批列表"""
        for item in self.pwd_tree.get_children():
            self.pwd_tree.delete(item)

        sql = "SELECT * FROM password_change_applications WHERE status='pending' ORDER BY apply_date DESC"
        applications = db.execute_query(sql)

        for app in applications:
            self.pwd_tree.insert("", tk.END, values=(
                app['id'], app['username'], app['apply_date'], '待审批'
            ))

    def approve_password(self):
        """批准密码修改"""
        selection = self.pwd_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要批准的申请")
            return

        item = self.pwd_tree.item(selection[0])
        app_id = item['values'][0]

        sql = "SELECT * FROM password_change_applications WHERE id=%s"
        app = db.execute_query(sql, (app_id,))
        if not app:
            return

        app = app[0]
        from models.user import User
        User.update_password_by_hash(app['user_id'], app['new_password'])

        sql = "UPDATE password_change_applications SET status='approved', approve_date=NOW() WHERE id=%s"
        db.execute_update(sql, (app_id,))

        self.refresh_password_approvals()
        messagebox.showinfo("成功", "已批准密码修改")

    def reject_password(self):
        """拒绝密码修改"""
        selection = self.pwd_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要拒绝的申请")
            return

        item = self.pwd_tree.item(selection[0])
        app_id = item['values'][0]

        sql = "UPDATE password_change_applications SET status='rejected', approve_date=NOW() WHERE id=%s"
        db.execute_update(sql, (app_id,))

        self.refresh_password_approvals()
        messagebox.showinfo("成功", "已拒绝密码修改")

    def show_personnel_management(self):
        """显示人事管理"""
        self._show_content_page("人事管理", "人事档案管理功能正在完善中...")

    def show_profile(self):
        """显示个人中心"""
        self.clear_right_frame()

        tk.Label(self.right_frame, text="个人中心", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)

        card = self.create_card(self.right_frame, "个人信息")
        card.pack(fill=tk.X, padx=20, pady=10)

        info_frame = tk.Frame(card, bg=self.COLORS['bg_white'])
        info_frame.pack(padx=20, pady=20)

        dept_info = self.get_department_info()

        tk.Label(info_frame, text="用户名:", font=("Microsoft YaHei", 11)).grid(row=0, column=0, sticky="e", pady=5)
        tk.Label(info_frame, text=self.user['username'], font=("Microsoft YaHei", 11)).grid(row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(info_frame, text="姓名:", font=("Microsoft YaHei", 11)).grid(row=1, column=0, sticky="e", pady=5)
        tk.Label(info_frame, text=self.user['full_name'], font=("Microsoft YaHei", 11)).grid(row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(info_frame, text="部门:", font=("Microsoft YaHei", 11)).grid(row=2, column=0, sticky="e", pady=5)
        tk.Label(info_frame, text=dept_info['name'], font=("Microsoft YaHei", 11)).grid(row=2, column=1, sticky="w", padx=10, pady=5)

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

        note_text = "说明：密码修改申请将提交至劳动人事处审批，审批通过后密码才会生效。"
        tk.Label(pwd_frame, text=note_text, font=("Microsoft YaHei", 9), fg="gray",
                wraplength=350, justify=tk.LEFT).grid(row=3, column=0, columnspan=2, pady=10)

        def change_pwd():
            import hashlib
            from models.user import User

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

            user = User.get_by_id(self.user['id'])
            old_hash = hashlib.sha256(old_password.encode()).hexdigest()
            if user['password'] != old_hash:
                messagebox.showerror("错误", "原密码错误")
                return

            try:
                new_hash = hashlib.sha256(new_password.encode()).hexdigest()
                sql = """INSERT INTO password_change_applications
                         (user_id, username, old_password, new_password, status, apply_date)
                         VALUES (%s, %s, %s, %s, 'pending', NOW())"""
                db.execute_update(sql, (self.user['id'], self.user['username'], old_hash, new_hash))
                messagebox.showinfo("成功", "密码修改申请已提交至劳动人事处，请等待审批。")
                old_pwd.delete(0, tk.END)
                new_pwd.delete(0, tk.END)
                confirm_pwd.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("错误", f"提交申请失败: {e}")

        tk.Button(pwd_frame, text="提交申请", command=change_pwd,
                 bg=self.COLORS['primary'], fg="white").grid(row=4, column=1, pady=10)

    def show_asset_ledger(self):
        """显示资产台账 - 资产管理处专用"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="全局资产台账", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 搜索栏
        search_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(search_frame, text="资产名称:").pack(side=tk.LEFT, padx=5)
        self.asset_search_entry = tk.Entry(search_frame, width=20)
        self.asset_search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="查询", command=self.search_assets,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="添加资产", command=self.add_asset,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.RIGHT, padx=5)

        # 资产列表
        columns = ("ID", "资产名称", "类别", "型号", "位置", "状态", "使用单位")
        self.asset_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=16)

        for col in columns:
            self.asset_tree.heading(col, text=col)
            self.asset_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.asset_tree.yview)
        self.asset_tree.configure(yscrollcommand=scrollbar.set)

        self.asset_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮栏
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_asset_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑", command=self.edit_asset,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除", command=self.delete_asset,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_assets,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_assets()

    def refresh_assets(self):
        """刷新资产列表"""
        for item in self.asset_tree.get_children():
            self.asset_tree.delete(item)

        filters = {}
        if hasattr(self, 'asset_search_entry') and self.asset_search_entry.get().strip():
            filters['name'] = self.asset_search_entry.get().strip()

        assets = AssetService.get_all_assets(filters)
        status_map = {'normal': '正常', 'borrowed': '已借出', 'maintenance': '维修中', 'scrapped': '已报废'}

        for asset in assets:
            self.asset_tree.insert("", tk.END, values=(
                asset['id'], asset['name'], asset.get('category', ''),
                asset.get('model', ''), asset.get('location', ''),
                status_map.get(asset.get('status', 'normal'), asset.get('status', '')),
                asset.get('org_name', '')
            ))

    def search_assets(self):
        """搜索资产"""
        self.refresh_assets()

    def add_asset(self):
        """添加资产"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加资产")
        dialog.geometry("500x500")

        fields = [
            ("资产名称:", 0), ("类别:", 1), ("型号:", 2),
            ("序列号:", 3), ("购入日期:", 4), ("价格:", 5),
            ("位置:", 6), ("保管人:", 7)
        ]
        entries = {}

        for label, row in fields:
            tk.Label(dialog, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(dialog, width=35)
            entry.grid(row=row, column=1, pady=5)
            entries[label.rstrip(':')] = entry

        # 状态选择
        tk.Label(dialog, text="状态:").grid(row=8, column=0, padx=10, pady=5, sticky="e")
        status_var = tk.StringVar(value="normal")
        tk.Combobox(dialog, textvariable=status_var, values=["normal", "borrowed", "maintenance", "scrapped"],
                   width=33).grid(row=8, column=1, pady=5)

        # 是否全局资产
        is_public_var = tk.IntVar(value=1)
        tk.Checkbutton(dialog, text="全局资产(所有处室可见)", variable=is_public_var).grid(row=9, column=1, sticky="w", pady=5)

        def submit():
            if not entries['资产名称'].get().strip():
                messagebox.showwarning("提示", "请输入资产名称")
                return

            try:
                AssetService.create_asset({
                    'name': entries['资产名称'].get().strip(),
                    'category': entries['类别'].get().strip(),
                    'model': entries['型号'].get().strip(),
                    'serial_number': entries['序列号'].get().strip(),
                    'purchase_date': entries['购入日期'].get().strip(),
                    'price': float(entries['价格'].get().strip() or 0),
                    'location': entries['位置'].get().strip(),
                    'status': status_var.get(),
                    'organization_id': self.user['organization_id'],
                    'is_public': is_public_var.get(),
                    'caretaker': entries['保管人'].get().strip()
                })
                self.refresh_assets()
                dialog.destroy()
                messagebox.showinfo("成功", "资产添加成功")
            except Exception as e:
                messagebox.showerror("错误", f"添加失败: {e}")

        tk.Button(dialog, text="提交", command=submit, bg=self.COLORS['primary'], fg="white").grid(row=10, column=1, pady=15)

    def view_asset_detail(self):
        """查看资产详情"""
        selection = self.asset_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择资产")
            return

        item = self.asset_tree.item(selection[0])
        asset_id = item['values'][0]

        asset = AssetService.get_asset_by_id(asset_id)
        if not asset:
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title("资产详情")
        detail_window.geometry("500x400")

        status_map = {'normal': '正常', 'borrowed': '已借出', 'maintenance': '维修中', 'scrapped': '已报废'}
        info = f"""资产名称: {asset.get('name', '')}
类别: {asset.get('category', '')}
型号: {asset.get('model', '')}
序列号: {asset.get('serial_number', '')}
购入日期: {asset.get('purchase_date', '')}
价格: {asset.get('price', 0)} 元
位置: {asset.get('location', '')}
状态: {status_map.get(asset.get('status', 'normal'), asset.get('status', ''))}
保管人: {asset.get('caretaker', '')}"""

        tk.Label(detail_window, text=info, font=("Microsoft YaHei", 11), justify=tk.LEFT).pack(padx=20, pady=20)

    def edit_asset(self):
        """编辑资产"""
        selection = self.asset_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择资产")
            return

        item = self.asset_tree.item(selection[0])
        asset_id = item['values'][0]

        asset = AssetService.get_asset_by_id(asset_id)
        if not asset:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("编辑资产")
        dialog.geometry("500x500")

        fields = [
            ("资产名称:", 0, asset.get('name', '')),
            ("类别:", 1, asset.get('category', '')),
            ("型号:", 2, asset.get('model', '')),
            ("位置:", 3, asset.get('location', '')),
            ("保管人:", 4, asset.get('caretaker', ''))
        ]
        entries = {}

        for label, row, default in fields:
            tk.Label(dialog, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(dialog, width=35)
            entry.insert(0, default)
            entry.grid(row=row, column=1, pady=5)
            entries[label.rstrip(':')] = entry

        tk.Label(dialog, text="状态:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        status_var = tk.StringVar(value=asset.get('status', 'normal'))
        tk.Combobox(dialog, textvariable=status_var, values=["normal", "borrowed", "maintenance", "scrapped"],
                   width=33).grid(row=5, column=1, pady=5)

        def submit():
            try:
                AssetService.update_asset(asset_id, {
                    'name': entries['资产名称'].get().strip(),
                    'category': entries['类别'].get().strip(),
                    'model': entries['型号'].get().strip(),
                    'location': entries['位置'].get().strip(),
                    'status': status_var.get(),
                    'caretaker': entries['保管人'].get().strip()
                })
                self.refresh_assets()
                dialog.destroy()
                messagebox.showinfo("成功", "资产更新成功")
            except Exception as e:
                messagebox.showerror("错误", f"更新失败: {e}")

        tk.Button(dialog, text="保存", command=submit, bg=self.COLORS['primary'], fg="white").grid(row=6, column=1, pady=15)

    def delete_asset(self):
        """删除资产"""
        selection = self.asset_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择资产")
            return

        if not messagebox.askyesno("确认", "确定要删除该资产吗?"):
            return

        item = self.asset_tree.item(selection[0])
        asset_id = item['values'][0]

        AssetService.delete_asset(asset_id)
        self.refresh_assets()
        messagebox.showinfo("成功", "资产已删除")

    def show_asset_allocation(self):
        """显示资产调配 - 资产管理处专用"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="资产调配审批", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        columns = ("ID", "资产名称", "申请单位", "申请人", "申请时间", "状态")
        self.alloc_req_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.alloc_req_tree.heading(col, text=col)
            self.alloc_req_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.alloc_req_tree.yview)
        self.alloc_req_tree.configure(yscrollcommand=scrollbar.set)

        self.alloc_req_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="查看详情", command=self.view_alloc_request,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="批准", command=self.approve_asset_alloc,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="拒绝", command=self.reject_asset_alloc,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_alloc_requests,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_alloc_requests()

    def refresh_alloc_requests(self):
        """刷新调配申请列表"""
        for item in self.alloc_req_tree.get_children():
            self.alloc_req_tree.delete(item)

        apps = AssetService.get_applications({'status': 'pending'})
        status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}

        for app in apps:
            self.alloc_req_tree.insert("", tk.END, values=(
                app['id'], app.get('asset_name', ''), app.get('org_name', ''),
                app.get('applicant_name', ''), app.get('apply_date', ''),
                status_map.get(app.get('status', 'pending'), app.get('status', ''))
            ))

    def view_alloc_request(self):
        """查看调配申请详情"""
        selection = self.alloc_req_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择申请")
            return

        item = self.alloc_req_tree.item(selection[0])
        app_id = item['values'][0]

        apps = AssetService.get_applications()
        app = next((a for a in apps if a['id'] == app_id), None)
        if not app:
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title("申请详情")
        detail_window.geometry("500x300")

        info = f"""资产名称: {app.get('asset_name', '')}
申请单位: {app.get('org_name', '')}
申请人: {app.get('applicant_name', '')}
申请时间: {app.get('apply_date', '')}

申请理由:
{app.get('reason', '')}"""

        tk.Label(detail_window, text=info, font=("Microsoft YaHei", 11), justify=tk.LEFT).pack(padx=20, pady=20)

    def approve_asset_alloc(self):
        """批准资产调配"""
        selection = self.alloc_req_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择申请")
            return

        item = self.alloc_req_tree.item(selection[0])
        app_id = item['values'][0]

        dialog = tk.Toplevel(self.root)
        dialog.title("批准调配")
        dialog.geometry("400x200")

        tk.Label(dialog, text="审批意见:").pack(anchor="w", padx=20, pady=10)
        comment_text = tk.Text(dialog, width=40, height=6)
        comment_text.pack(fill=tk.X, padx=20, pady=5)

        def submit():
            comment = comment_text.get(1.0, tk.END).strip()
            AssetService.approve_application(app_id, self.user['id'], comment)
            dialog.destroy()
            self.refresh_alloc_requests()
            messagebox.showinfo("成功", "已批准该调配申请")

        tk.Button(dialog, text="确认批准", command=submit, bg=self.COLORS['success'], fg="white").pack(pady=10)

    def reject_asset_alloc(self):
        """拒绝资产调配"""
        selection = self.alloc_req_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择申请")
            return

        item = self.alloc_req_tree.item(selection[0])
        app_id = item['values'][0]

        dialog = tk.Toplevel(self.root)
        dialog.title("拒绝调配")
        dialog.geometry("400x200")

        tk.Label(dialog, text="拒绝原因:").pack(anchor="w", padx=20, pady=10)
        comment_text = tk.Text(dialog, width=40, height=6)
        comment_text.pack(fill=tk.X, padx=20, pady=5)

        def submit():
            comment = comment_text.get(1.0, tk.END).strip()
            if not comment:
                messagebox.showwarning("提示", "请输入拒绝原因")
                return
            AssetService.reject_application(app_id, self.user['id'], comment)
            dialog.destroy()
            self.refresh_alloc_requests()
            messagebox.showinfo("成功", "已拒绝该调配申请")

        tk.Button(dialog, text="确认拒绝", command=submit, bg=self.COLORS['accent'], fg="white").pack(pady=10)

    def show_asset_statistics(self):
        """显示资产统计 - 资产管理处专用"""
        self.clear_right_frame()

        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="资产统计报表", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        tk.Button(title_frame, text="刷新", command=self.load_asset_statistics,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.RIGHT, padx=5)

        self.asset_stat_text = tk.Text(self.right_frame, font=("Consolas", 12), wrap=tk.WORD)
        self.asset_stat_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.load_asset_statistics()

    def load_asset_statistics(self):
        """加载资产统计"""
        stats = AssetService.get_statistics()

        text = "\n资产统计报表\n================================\n\n"

        # 按状态统计
        status_stats = {'normal': 0, 'borrowed': 0, 'maintenance': 0, 'scrapped': 0}
        total_value = 0

        for s in stats:
            status = s.get('status', 'normal')
            if status in status_stats:
                status_stats[status] = s.get('count', 0)
            total_value += s.get('total_value', 0) or 0

        status_map = {'normal': '正常', 'borrowed': '已借出', 'maintenance': '维修中', 'scrapped': '已报废'}

        text += "按状态统计:\n"
        text += "-" * 40 + "\n"
        for status, count in status_stats.items():
            text += f"  {status_map.get(status, status)}: {count} 项\n"

        text += f"\n资产总价值: {total_value:.2f} 元\n"

        # 获取各类别资产
        sql = """SELECT category, COUNT(*) as count, SUM(price) as total
                 FROM assets GROUP BY category"""
        categories = db.execute_query(sql)

        text += "\n按类别统计:\n"
        text += "-" * 40 + "\n"
        for cat in categories:
            cat_name = cat.get('category', '未知')
            count = cat.get('count', 0)
            value = cat.get('total', 0) or 0
            text += f"  {cat_name}: {count} 项, 价值 {value:.2f} 元\n"

        self.asset_stat_text.delete(1.0, tk.END)
        self.asset_stat_text.insert(1.0, text)

    def _show_content_page(self, title, content=None):
        """统一的内容显示页面"""
        self.clear_right_frame()

        if content is None:
            content = f"{title}功能正在开发中..."

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