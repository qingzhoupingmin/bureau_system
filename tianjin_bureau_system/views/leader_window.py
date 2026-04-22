# -*- coding: utf-8 -*-
"""
局领导窗口 - 综合仪表盘
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from db.connection import db


class LeaderWindow(MainWindow):
    """局领导窗口"""

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

    def create_left_sidebar(self):
        """创建左侧导航栏"""
        sidebar = tk.Frame(self.main_frame, bg=self.COLORS['primary'], width=200)
        self.paned.add(sidebar, minsize=200)

        # 导航标题
        nav_title = tk.Label(sidebar, text="功能导航", font=("Microsoft YaHei", 14, "bold"),
                            bg=self.COLORS['primary'], fg="white")
        nav_title.pack(pady=20)

        # 导航按钮
        nav_items = [
            ("单位概况", self.show_overview),
            ("综合仪表盘", self.show_dashboard),
            ("待办审批", self.show_approvals),
            ("公文查看", self.show_documents),
            ("消息通知", self.show_messages),
            ("统计分析", self.show_statistics),
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

    def show_dashboard(self):
        """显示综合仪表盘"""
        self.clear_right_frame()

        # 标题
        tk.Label(self.right_frame, text="综合仪表盘", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)

        # 统计卡片区域
        stats_container = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        stats_container.pack(fill=tk.X, padx=20, pady=10)

        # 获取统计数据
        stats = self.get_dashboard_stats()

        # 第一行统计卡片
        row1 = tk.Frame(stats_container, bg=self.COLORS['bg_white'])
        row1.pack(fill=tk.X, pady=10)

        # 资产总数
        self.create_stat_card(row1, "资产总数", str(stats.get('total_assets', 0)), self.COLORS['primary'])
        # 预算总额
        self.create_stat_card(row1, "预算总额", f"{stats.get('total_budget', 0):.2f}万", self.COLORS['secondary'])
        # 科研项目
        self.create_stat_card(row1, "科研项目", str(stats.get('total_projects', 0)), self.COLORS['success'])

        # 第二行统计卡片
        row2 = tk.Frame(stats_container, bg=self.COLORS['bg_white'])
        row2.pack(fill=tk.X, pady=10)

        # 待审批
        self.create_stat_card(row2, "待审批公文", str(stats.get('pending_docs', 0)), self.COLORS['warning'])
        # 待审批预算
        self.create_stat_card(row2, "待审批预算", str(stats.get('pending_budgets', 0)), self.COLORS['accent'])
        # 待审批科研
        self.create_stat_card(row2, "待审批科研", str(stats.get('pending_projects', 0)), '#9b59b6')

        # 待办事项区域
        todo_card = self.create_card(self.right_frame, "待办事项")
        todo_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 待办列表
        columns = ("类型", "标题", "来源单位", "时间")
        self.todo_tree = ttk.Treeview(todo_card, columns=columns, show="headings", height=10)

        for col in columns:
            self.todo_tree.heading(col, text=col)
            self.todo_tree.column(col, width=150)

        self.todo_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(todo_card, orient=tk.VERTICAL, command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.refresh_todo_list()

    def create_stat_card(self, parent, title, value, color):
        """创建统计卡片"""
        card = tk.Frame(parent, bg=color, width=200, height=80)
        card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        card.pack_propagate(False)

        tk.Label(card, text=title, font=("Microsoft YaHei", 11),
                bg=color, fg="white").pack(pady=(15, 5))
        tk.Label(card, text=value, font=("Microsoft YaHei", 20, "bold"),
                bg=color, fg="white").pack()

    def get_dashboard_stats(self):
        """获取仪表盘统计数据"""
        stats = {
            'total_assets': 0,
            'total_budget': 0,
            'total_projects': 0,
            'pending_docs': 0,
            'pending_budgets': 0,
            'pending_projects': 0,
        }

        try:
            # 资产总数
            result = db.execute_query("SELECT COUNT(*) as cnt FROM assets")
            if result:
                stats['total_assets'] = result[0].get('cnt', 0)

            # 预算总额（已批准的）
            result = db.execute_query("SELECT SUM(amount) as total FROM budget_applications WHERE status='approved'")
            if result and result[0].get('total'):
                stats['total_budget'] = result[0].get('total', 0) / 10000  # 转换为万元

            # 科研项目总数
            result = db.execute_query("SELECT COUNT(*) as cnt FROM research_projects")
            if result:
                stats['total_projects'] = result[0].get('cnt', 0)

            # 待审批公文
            result = db.execute_query("SELECT COUNT(*) as cnt FROM documents WHERE status='pending'")
            if result:
                stats['pending_docs'] = result[0].get('cnt', 0)

            # 待审批预算
            result = db.execute_query("SELECT COUNT(*) as cnt FROM budget_applications WHERE status='pending'")
            if result:
                stats['pending_budgets'] = result[0].get('cnt', 0)

            # 待审批科研
            result = db.execute_query("SELECT COUNT(*) as cnt FROM research_projects WHERE status='pending'")
            if result:
                stats['pending_projects'] = result[0].get('cnt', 0)

        except Exception as e:
            print(f"获取统计数据失败: {e}")

        return stats

    def refresh_todo_list(self):
        """刷新待办列表"""
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)

        # 获取所有待审批事项
        # 待审批公文
        docs = db.execute_query("SELECT d.title, d.create_date, o.name as org_name FROM documents d LEFT JOIN organizations o ON d.sender_org_id = o.id WHERE d.status='pending' LIMIT 5")
        for doc in docs:
            self.todo_tree.insert("", tk.END, values=(
                "公文", doc.get('title', ''), doc.get('org_name', ''), doc.get('create_date', '')
            ))

        # 待审批预算
        budgets = db.execute_query("SELECT b.year, b.amount, o.name as org_name, b.apply_date FROM budget_applications b LEFT JOIN organizations o ON b.organization_id = o.id WHERE b.status='pending' LIMIT 5")
        for b in budgets:
            self.todo_tree.insert("", tk.END, values=(
                "预算", f"{b.get('year', '')}年度预算 {b.get('amount', 0):.2f}", b.get('org_name', ''), b.get('apply_date', '')
            ))

        # 待审批科研
        projects = db.execute_query("SELECT r.name, r.budget, o.name as org_name, r.apply_date FROM research_projects r LEFT JOIN organizations o ON r.applicant_org_id = o.id WHERE r.status='pending' LIMIT 5")
        for p in projects:
            self.todo_tree.insert("", tk.END, values=(
                "科研", p.get('name', ''), p.get('org_name', ''), p.get('apply_date', '')
            ))

    def show_approvals(self):
        """显示待办审批"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="待办审批", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 创建Notebook用于切换不同类型的审批
        approval_notebook = ttk.Notebook(self.right_frame)
        approval_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 公文审批页
        doc_frame = tk.Frame(approval_notebook)
        approval_notebook.add(doc_frame, text="公文审批")

        columns = ("ID", "标题", "类型", "发送单位", "创建时间")
        self.doc_approval_tree = ttk.Treeview(doc_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.doc_approval_tree.heading(col, text=col)
            self.doc_approval_tree.column(col, width=120)

        self.doc_approval_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(doc_frame, orient=tk.VERTICAL, command=self.doc_approval_tree.yview)
        self.doc_approval_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 预算审批页
        budget_frame = tk.Frame(approval_notebook)
        approval_notebook.add(budget_frame, text="预算审批")

        columns = ("ID", "申请单位", "年度", "金额", "申请时间")
        self.budget_approval_tree = ttk.Treeview(budget_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.budget_approval_tree.heading(col, text=col)
            self.budget_approval_tree.column(col, width=120)

        self.budget_approval_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(budget_frame, orient=tk.VERTICAL, command=self.budget_approval_tree.yview)
        self.budget_approval_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 科研审批页
        project_frame = tk.Frame(approval_notebook)
        approval_notebook.add(project_frame, text="科研审批")

        columns = ("ID", "项目名称", "申请单位", "预算", "申请时间")
        self.project_approval_tree = ttk.Treeview(project_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.project_approval_tree.heading(col, text=col)
            self.project_approval_tree.column(col, width=120)

        self.project_approval_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(project_frame, orient=tk.VERTICAL, command=self.project_approval_tree.yview)
        self.project_approval_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 按钮栏
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_all_approvals,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_all_approvals()

    def refresh_all_approvals(self):
        """刷新所有审批列表"""
        # 刷新公文审批
        for item in self.doc_approval_tree.get_children():
            self.doc_approval_tree.delete(item)

        docs = db.execute_query("SELECT d.*, o.name as org_name FROM documents d LEFT JOIN organizations o ON d.sender_org_id = o.id WHERE d.status='pending'")
        for doc in docs:
            self.doc_approval_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], doc.get('doc_type', ''),
                doc.get('org_name', ''), doc.get('create_date', '')
            ))

        # 刷新预算审批
        for item in self.budget_approval_tree.get_children():
            self.budget_approval_tree.delete(item)

        budgets = db.execute_query("SELECT b.*, o.name as org_name FROM budget_applications b LEFT JOIN organizations o ON b.organization_id = o.id WHERE b.status='pending'")
        for b in budgets:
            self.budget_approval_tree.insert("", tk.END, values=(
                b['id'], b.get('org_name', ''), b.get('year', ''),
                f"{b.get('amount', 0):.2f}", b.get('apply_date', '')
            ))

        # 刷新科研审批
        for item in self.project_approval_tree.get_children():
            self.project_approval_tree.delete(item)

        projects = db.execute_query("SELECT r.*, o.name as org_name FROM research_projects r LEFT JOIN organizations o ON r.applicant_org_id = o.id WHERE r.status='pending'")
        for p in projects:
            self.project_approval_tree.insert("", tk.END, values=(
                p['id'], p['name'], p.get('org_name', ''),
                f"{p.get('budget', 0):.2f}", p.get('apply_date', '')
            ))

    def show_documents(self):
        """显示公文列表"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="公文查看", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 公文列表
        columns = ("ID", "标题", "类型", "发送单位", "状态", "创建时间")
        self.leader_doc_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.leader_doc_tree.heading(col, text=col)
            self.leader_doc_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.leader_doc_tree.yview)
        self.leader_doc_tree.configure(yscrollcommand=scrollbar.set)

        self.leader_doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_leader_docs,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_leader_docs()

    def refresh_leader_docs(self):
        """刷新公文列表"""
        for item in self.leader_doc_tree.get_children():
            self.leader_doc_tree.delete(item)

        docs = db.execute_query("SELECT d.*, o.name as org_name FROM documents d LEFT JOIN organizations o ON d.sender_org_id = o.id ORDER BY d.create_date DESC")
        status_map = {'draft': '草稿', 'pending': '待审核', 'published': '已发布', 'replied': '已回复'}

        for doc in docs:
            self.leader_doc_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], doc.get('doc_type', ''),
                doc.get('org_name', ''), status_map.get(doc.get('status', 'draft'), doc.get('status', '')),
                doc.get('create_date', '')
            ))

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
        self.leader_msg_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.leader_msg_tree.heading(col, text=col)
            self.leader_msg_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.leader_msg_tree.yview)
        self.leader_msg_tree.configure(yscrollcommand=scrollbar.set)

        self.leader_msg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_leader_messages,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_leader_messages()

    def refresh_leader_messages(self):
        """刷新消息列表"""
        for item in self.leader_msg_tree.get_children():
            self.leader_msg_tree.delete(item)

        msgs = db.execute_query("SELECT m.*, u.full_name as sender_name FROM messages m LEFT JOIN users u ON m.sender_id = u.id ORDER BY m.create_date DESC")
        type_map = {'official': '局名义通知', 'business': '业务通知', 'request': '业务请示'}

        for msg in msgs:
            self.leader_msg_tree.insert("", tk.END, values=(
                msg['id'], msg['title'], type_map.get(msg.get('message_type', 'business'), msg.get('message_type', '')),
                msg.get('sender_name', ''), msg.get('create_date', '')
            ))

    def show_statistics(self):
        """显示统计分析"""
        self.clear_right_frame()

        tk.Label(self.right_frame, text="统计分析", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)

        # 统计文本区
        self.leader_stat_text = tk.Text(self.right_frame, font=("Consolas", 12), wrap=tk.WORD)
        self.leader_stat_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.load_leader_statistics()

    def load_leader_statistics(self):
        """加载统计分析"""
        text = """
天津市市政工程局综合管理系统
统计分析报告
================================

"""

        # 资产统计
        result = db.execute_query("SELECT COUNT(*) as cnt, SUM(price) as total FROM assets")
        if result:
            text += f"""
【资产概况】
  资产总数: {result[0].get('cnt', 0)} 件
  资产总值: {result[0].get('total', 0) or 0:.2f} 元
"""

        # 预算统计
        result = db.execute_query("SELECT status, COUNT(*) as cnt, SUM(amount) as total FROM budget_applications GROUP BY status")
        text += "\n【预算申请统计】\n"
        pending_budget = approved_budget = rejected_budget = 0
        for r in result:
            status = r.get('status', '')
            cnt = r.get('cnt', 0)
            total = r.get('total', 0) or 0
            if status == 'pending':
                pending_budget = cnt
            elif status == 'approved':
                approved_budget = cnt
            elif status == 'rejected':
                rejected_budget = cnt
            text += f"  {status}: {cnt} 个, 金额 {total:.2f} 元\n"

        # 科研统计
        result = db.execute_query("SELECT status, COUNT(*) as cnt FROM research_projects GROUP BY status")
        text += "\n【科研项目统计】\n"
        for r in result:
            text += f"  {r.get('status', '')}: {r.get('cnt', 0)} 个\n"

        # 公文统计
        result = db.execute_query("SELECT status, COUNT(*) as cnt FROM documents GROUP BY status")
        text += "\n【公文统计】\n"
        for r in result:
            text += f"  {r.get('status', '')}: {r.get('cnt', 0)} 份\n"

        # 用户统计
        result = db.execute_query("SELECT role, COUNT(*) as cnt FROM users GROUP BY role")
        text += "\n【用户统计】\n"
        role_names = {'system_admin': '系统管理员', 'leader': '局领导', 'asset_manager': '资产管理处',
                     'office_staff': '办公室', 'tech_staff': '科技处', 'finance_staff': '财务处',
                     'unit_user': '下属单位', 'normal_user': '普通用户'}
        for r in result:
            role = r.get('role', '')
            name = role_names.get(role, role)
            text += f"  {name}: {r.get('cnt', 0)} 人\n"

        self.leader_stat_text.delete(1.0, tk.END)
        self.leader_stat_text.insert(1.0, text)

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

        note_text = "说明：密码修改申请将提交至劳动人事处审批，审批通过后密码才会生效。"
        tk.Label(pwd_frame, text=note_text, font=("Microsoft YaHei", 9), fg="gray",
                wraplength=350, justify=tk.LEFT).grid(row=3, column=0, columnspan=2, pady=10)

        def change_pwd():
            from db.connection import db
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