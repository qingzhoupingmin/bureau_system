# -*- coding: utf-8 -*-
"""
财务处窗口 - 预算管理
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from services.budget_service import BudgetService
from db.connection import db


class FinanceWindow(MainWindow):
    """财务处窗口"""

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
            ("预算审批", self.show_budget_approvals),
            ("预算分配", self.show_budget_allocation),
            ("预算统计", self.show_budget_statistics),
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

    def show_budget_approvals(self):
        """显示预算审批"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="预算审批", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 工具栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(toolbar, text="查看详情", command=self.view_budget_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="批准", command=self.approve_budget,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="拒绝", command=self.reject_budget,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="刷新", command=self.refresh_budget_approvals,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        # 预算申请列表
        columns = ("ID", "申请单位", "年度", "预算金额", "类型", "申请时间", "状态")
        self.budget_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.budget_tree.heading(col, text=col)
            if col == "预算金额":
                self.budget_tree.column(col, width=100)
            else:
                self.budget_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=scrollbar.set)

        self.budget_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.refresh_budget_approvals()

    def refresh_budget_approvals(self):
        """刷新预算审批列表"""
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)

        budgets = BudgetService.get_all_applications()
        status_map = {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}

        for budget in budgets:
            status_name = status_map.get(budget.get('status', 'pending'), budget.get('status', ''))
            amount = budget.get('amount', 0) or 0
            self.budget_tree.insert("", tk.END, values=(
                budget['id'], budget.get('org_name', ''), budget.get('year', ''),
                f"{amount:.2f}", budget.get('type', ''),
                budget.get('apply_date', ''), status_name
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
        detail_window.geometry("500x400")

        tk.Label(detail_window, text=f"申请单位: {budget.get('org_name', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", padx=20, pady=5)
        tk.Label(detail_window, text=f"预算年度: {budget.get('year', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", padx=20, pady=5)
        tk.Label(detail_window, text=f"预算金额: {budget.get('amount', 0):.2f} 元", font=("Microsoft YaHei", 11)).pack(anchor="w", padx=20, pady=5)
        tk.Label(detail_window, text=f"申请类型: {budget.get('type', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", padx=20, pady=5)
        tk.Label(detail_window, text=f"申请时间: {budget.get('apply_date', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", padx=20, pady=5)
        tk.Label(detail_window, text=f"状态: {budget.get('status', '')}", font=("Microsoft YaHei", 11)).pack(anchor="w", padx=20, pady=5)

        tk.Label(detail_window, text="用途说明:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        purpose_text = tk.Text(detail_window, wrap=tk.WORD, height=8)
        purpose_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        purpose_text.insert(1.0, budget.get('purpose', ''))
        purpose_text.config(state=tk.DISABLED)

        if budget.get('approve_comment'):
            tk.Label(detail_window, text="审批意见:", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
            comment_text = tk.Text(detail_window, wrap=tk.WORD, height=4)
            comment_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            comment_text.insert(1.0, budget.get('approve_comment', ''))
            comment_text.config(state=tk.DISABLED)

    def approve_budget(self):
        """批准预算"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要批准的预算申请")
            return

        item = self.budget_tree.item(selection[0])
        budget_id = item['values'][0]
        status = item['values'][6]

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
        status = item['values'][6]

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

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="预算分配", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 已批准预算列表（可分配）
        columns = ("ID", "申请单位", "年度", "预算金额", "已分配", "申请时间")
        self.alloc_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=18)

        for col in columns:
            self.alloc_tree.heading(col, text=col)
            self.alloc_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.alloc_tree.yview)
        self.alloc_tree.configure(yscrollcommand=scrollbar.set)

        self.alloc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 分配工具栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(toolbar, text="查看详情", command=self.view_allocation_detail,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="刷新", command=self.refresh_allocations,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        self.refresh_allocations()

    def refresh_allocations(self):
        """刷新分配列表"""
        for item in self.alloc_tree.get_children():
            self.alloc_tree.delete(item)

        # 只显示已批准的预算
        budgets = BudgetService.get_all_applications({'status': 'approved'})

        for budget in budgets:
            amount = budget.get('amount', 0) or 0
            self.alloc_tree.insert("", tk.END, values=(
                budget['id'], budget.get('org_name', ''), budget.get('year', ''),
                f"{amount:.2f}", "0.00", budget.get('apply_date', '')
            ))

    def view_allocation_detail(self):
        """查看分配详情"""
        selection = self.alloc_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择预算")
            return

        item = self.alloc_tree.item(selection[0])
        budget_id = item['values'][0]

        budget = BudgetService.get_application_by_id(budget_id)
        if budget:
            self.view_budget_detail()

    def show_budget_statistics(self):
        """显示预算统计"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="预算统计", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 搜索栏
        search_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(search_frame, text="年度:").pack(side=tk.LEFT, padx=5)
        self.stat_year_entry = tk.Entry(search_frame, width=10)
        self.stat_year_entry.pack(side=tk.LEFT, padx=5)
        self.stat_year_entry.insert(0, "2026")
        tk.Button(search_frame, text="查询", command=self.load_statistics,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        # 统计结果
        self.stat_text = tk.Text(self.right_frame, font=("Consolas", 12), wrap=tk.WORD)
        self.stat_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.load_statistics()

    def load_statistics(self):
        """加载统计信息"""
        year = self.stat_year_entry.get().strip()
        stats = BudgetService.get_statistics(year if year else None)

        total = 0
        text = f"""
预算统计报表
================================

"""

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

        # 按状态统计
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