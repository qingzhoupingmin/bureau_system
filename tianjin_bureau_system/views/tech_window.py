# -*- coding: utf-8 -*-
"""
科技处窗口 - 科研项目管理
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from services.research_service import ResearchService
from db.connection import db


class TechWindow(MainWindow):
    """科技处窗口"""

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
            ("科研项目管理", self.show_projects),
            ("科研经费管理", self.show_funds),
            ("申请审批", self.show_approvals),
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

    def show_projects(self):
        """显示科研项目管理"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="科研项目管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 搜索栏
        search_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.project_search_entry = tk.Entry(search_frame, width=30)
        self.project_search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="查询", command=self.search_projects).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="刷新", command=self.refresh_projects,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        # 项目列表
        columns = ("ID", "项目名称", "申请单位", "预算金额", "状态", "申请时间")
        self.project_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=scrollbar.set)

        self.project_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.refresh_projects()

    def refresh_projects(self):
        """刷新项目列表"""
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        projects = ResearchService.get_all_projects()
        status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}

        for project in projects:
            status_name = status_map.get(project.get('status', 'pending'), project.get('status', ''))
            budget = project.get('budget', 0) or 0
            self.project_tree.insert("", tk.END, values=(
                project['id'], project['name'],
                project.get('org_name', ''), f"{budget:.2f}",
                status_name, project.get('apply_date', '')
            ))

    def search_projects(self):
        """搜索项目"""
        keyword = self.project_search_entry.get().strip()
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        if keyword:
            projects = ResearchService.get_all_projects()
            keyword_lower = keyword.lower()
            projects = [p for p in projects if keyword_lower in p.get('name', '').lower()]
        else:
            projects = ResearchService.get_all_projects()

        status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}
        for project in projects:
            status_name = status_map.get(project.get('status', 'pending'), project.get('status', ''))
            budget = project.get('budget', 0) or 0
            self.project_tree.insert("", tk.END, values=(
                project['id'], project['name'],
                project.get('org_name', ''), f"{budget:.2f}",
                status_name, project.get('apply_date', '')
            ))

    def show_funds(self):
        """显示科研经费管理"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="科研经费管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 选择项目
        select_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        select_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(select_frame, text="选择项目:").pack(side=tk.LEFT, padx=5)
        self.fund_project_combo = ttk.Combobox(select_frame, width=40)
        self.fund_project_combo['values'] = self.get_project_names()
        self.fund_project_combo.pack(side=tk.LEFT, padx=5)
        tk.Button(select_frame, text="查看经费", command=self.view_fund_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        # 经费详情区域
        detail_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 经费卡片
        fund_card = self.create_card(detail_frame, "经费详情")
        fund_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fund_text = tk.Text(fund_card, font=("Consolas", 12), wrap=tk.WORD)
        self.fund_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 拨付工具栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(toolbar, text="拨付金额:").pack(side=tk.LEFT, padx=5)
        self.allocate_amount = tk.Entry(toolbar, width=15)
        self.allocate_amount.pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="拨付经费", command=self.allocate_fund,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)

    def get_project_names(self):
        """获取已批准的项目名称列表"""
        projects = ResearchService.get_all_projects({'status': 'approved'})
        return [f"{p['id']} - {p['name']}" for p in projects]

    def view_fund_detail(self):
        """查看经费详情"""
        selection = self.fund_project_combo.get()
        if not selection:
            messagebox.showwarning("提示", "请选择项目")
            return

        try:
            project_id = int(selection.split(" - ")[0])
        except:
            messagebox.showwarning("提示", "请选择有效项目")
            return

        fund = ResearchService.get_funds(project_id)
        project = ResearchService.get_project_by_id(project_id)

        if not project:
            messagebox.showerror("错误", "项目不存在")
            return

        text = f"""
科研项目经费详情
================================

项目名称: {project['name']}
申请单位: {project.get('org_name', '')}
申请时间: {project.get('apply_date', '')}
"""

        if fund:
            text += f"""
经费信息:
  预算总额: {fund.get('total_budget', 0):.2f} 元
  已拨付: {fund.get('allocated', 0):.2f} 元
  已使用: {fund.get('used', 0):.2f} 元
  剩余可用: {(fund.get('total_budget', 0) or 0) - (fund.get('allocated', 0) or 0):.2f} 元
"""
        else:
            text += "\n经费信息: 暂无拨付记录"

        self.fund_text.delete(1.0, tk.END)
        self.fund_text.insert(1.0, text)

    def allocate_fund(self):
        """拨付经费"""
        selection = self.fund_project_combo.get()
        if not selection:
            messagebox.showwarning("提示", "请选择项目")
            return

        try:
            project_id = int(selection.split(" - ")[0])
            amount = float(self.allocate_amount.get())
            if amount <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("提示", "请输入有效的项目和金额")
            return

        # 检查是否已有经费记录
        fund = ResearchService.get_funds(project_id)
        if not fund:
            messagebox.showerror("错误", "该项目暂无经费记录，请先审批通过")
            return

        # 检查余额
        remaining = (fund.get('total_budget', 0) or 0) - (fund.get('allocated', 0) or 0)
        if amount > remaining:
            messagebox.showwarning("提示", f"拨付金额超过可用余额 {remaining:.2f} 元")
            return

        ResearchService.allocate_fund(project_id, amount)
        messagebox.showinfo("成功", f"已拨付 {amount:.2f} 元")
        self.allocate_amount.delete(0, tk.END)
        self.view_fund_detail()

    def show_approvals(self):
        """显示申请审批"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="科研项目审批", font=("Microsoft YaHei", 18, "bold"),
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

        # 只显示待审批的项目
        projects = ResearchService.get_all_projects({'status': 'pending'})

        for project in projects:
            budget = project.get('budget', 0) or 0
            self.approval_tree.insert("", tk.END, values=(
                project['id'], project['name'],
                project.get('org_name', ''), f"{budget:.2f}",
                project.get('apply_date', ''), '待审批'
            ))

    def view_project_detail(self):
        """查看项目详情"""
        selection = self.approval_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要查看的项目")
            return

        item = self.approval_tree.item(selection[0])
        project_id = item['values'][0]

        project = ResearchService.get_project_by_id(project_id)
        if not project:
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title("项目详情")
        detail_window.geometry("600x450")

        tk.Label(detail_window, text=project['name'], font=("Microsoft YaHei", 14, "bold")).pack(pady=10)

        info_frame = tk.Frame(detail_window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(info_frame, text=f"申请单位: {project.get('org_name', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"申请人: {project.get('applicant_name', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"预算金额: {project.get('budget', 0):.2f} 元", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)
        tk.Label(info_frame, text=f"申请时间: {project.get('apply_date', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=3)

        tk.Label(info_frame, text="项目描述:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", pady=(10, 5))
        desc_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
        desc_text.pack(fill=tk.BOTH, expand=True)
        desc_text.insert(1.0, project.get('description', ''))
        desc_text.config(state=tk.DISABLED)

    def approve_project(self):
        """批准项目"""
        selection = self.approval_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要批准的项目")
            return

        item = self.approval_tree.item(selection[0])
        project_id = item['values'][0]

        # 弹出对话框输入审批意见
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

        # 弹出对话框输入拒绝原因
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

        # 说明
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