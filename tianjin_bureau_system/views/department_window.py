# -*- coding: utf-8 -*-
"""
专业处室综合窗口 - 用于没有专属窗口的处室
包括: 计划处、设施处、养护处、建设处、规划处、规费处、审计处、人事处、安保处、法规处、党委办、纪检委、宣传部、组织部、老干部处
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from services.asset_service import AssetService
from services.message_service import MessageService
from services.auth_service import AuthService
from db.connection import db


class DepartmentWindow(MainWindow):
    """专业处室综合窗口"""

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

        # 根据处室显示不同功能
        self.show_overview()

    def get_department_function(self):
        """获取当前处室的专业功能"""
        # 根据organization_id返回处室名称和功能
        dept_functions = {
            2: ("计划处", ["项目计划", "立项审批", "投资管理"]),
            3: ("设施管理处", ["设施台账", "维护计划", "设施查询"]),
            4: ("设施养护处", ["养护工程", "进度跟踪", "质量监督"]),
            5: ("建设管理处", ["工程建设", "招投标管理", "进度跟踪"]),
            6: ("规划处", ["规划编制", "方案审查", "规划查询"]),
            8: ("规费管理处", ["规费标准", "征收管理", "统计报表"]),
            9: ("审计处", ["审计计划", "审计执行", "问题整改"]),
            11: ("劳动人事处", ["人事管理", "职称评审", "工资福利", "密码审批"]),
            13: ("安全保卫处", ["安全管理", "应急预案", "保卫管理"]),
            14: ("法规处", ["法规管理", "政策研究", "执法监督"]),
            15: ("党委办公室", ["党委事务", "党建工作", "文件起草"]),
            16: ("纪检委", ["纪检监察", "案件查处", "廉政教育"]),
            17: ("宣传部", ["宣传教育", "精神文明", "新闻宣传"]),
            18: ("组织部", ["干部管理", "党员管理", "统战工作"]),
            19: ("老干部处", ["老干部服务", "待遇落实", "活动组织"]),
        }
        return dept_functions.get(self.user.get('organization_id', 0), ("通用功能", []))

    def create_left_sidebar(self):
        """创建左侧导航栏"""
        sidebar = tk.Frame(self.main_frame, bg=self.COLORS['primary'], width=200)
        self.paned.add(sidebar, minsize=200)

        # 获取处室名称
        dept_name, _ = self.get_department_function()

        # 导航标题
        nav_title = tk.Label(sidebar, text=dept_name, font=("Microsoft YaHei", 14, "bold"),
                            bg=self.COLORS['primary'], fg="white")
        nav_title.pack(pady=20)

        # 导航按钮
        nav_items = [
            ("单位概况", self.show_overview),
            ("部门资产", self.show_assets),
            ("资产申请", self.show_asset_apply),
            ("消息通知", self.show_messages),
            ("专业功能", self.show_professional),
            ("个人中心", self.show_profile),
        ]

        # 劳动人事处特殊功能 - 账号注册
        if self.user.get('organization_id') == 11:
            nav_items.insert(5, ("账号注册", self.show_register_account))

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

        # 使用组织概况模块
        from views.organization_overview import OrganizationOverview
        overview = OrganizationOverview(self.right_frame, self.COLORS)
        overview.show()

    def show_assets(self):
        """显示部门资产"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="部门资产", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 资产列表
        columns = ("ID", "名称", "类别", "型号", "金额", "状态", "保管人")
        self.dept_asset_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.dept_asset_tree.heading(col, text=col)
            self.dept_asset_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.dept_asset_tree.yview)
        self.dept_asset_tree.configure(yscrollcommand=scrollbar.set)

        self.dept_asset_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_dept_assets,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_dept_assets()

    def refresh_dept_assets(self):
        """刷新资产列表"""
        for item in self.dept_asset_tree.get_children():
            self.dept_asset_tree.delete(item)

        org_id = self.user.get('organization_id', 0)
        if org_id > 0:
            assets = AssetService.get_all_assets({'organization_id': org_id})
        else:
            assets = AssetService.get_all_assets()

        for asset in assets:
            self.dept_asset_tree.insert("", tk.END, values=(
                asset['id'], asset['name'], asset['category'], asset['model'],
                asset.get('price', 0), asset.get('status', ''), asset.get('caretaker', '')
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
        self.apply_device_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.apply_device_tree.heading(col, text=col)
            self.apply_device_tree.column(col, width=120)

        self.apply_device_tree.pack(fill=tk.X, padx=20, pady=5)

        # 申请表单
        form_frame = tk.LabelFrame(self.right_frame, text="申请使用", font=("Microsoft YaHei", 11))
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(form_frame, text="申请原因:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.apply_reason_text = tk.Text(form_frame, width=50, height=4)
        self.apply_reason_text.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(form_frame, text="提交申请", command=self.submit_asset_apply,
                 bg=self.COLORS['success'], fg="white").grid(row=1, column=1, pady=10)

        # 我的申请记录
        tk.Label(self.right_frame, text="我的申请记录:", font=("Microsoft YaHei", 11, "bold"),
                bg=self.COLORS['bg_white']).pack(anchor="w", padx=20, pady=(10, 5))

        columns2 = ("ID", "资产", "申请时间", "状态", "审批意见")
        self.my_apply_tree = ttk.Treeview(self.right_frame, columns=columns2, show="headings", height=8)

        for col in columns2:
            self.my_apply_tree.heading(col, text=col)
            self.my_apply_tree.column(col, width=150)

        self.my_apply_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.refresh_apply_devices()
        self.refresh_my_applications()

    def refresh_apply_devices(self):
        """刷新可申请设备"""
        for item in self.apply_device_tree.get_children():
            self.apply_device_tree.delete(item)

        devices = AssetService.get_all_assets({'is_public': 1})
        for device in devices:
            self.apply_device_tree.insert("", tk.END, values=(
                device['id'], device['name'], device['category'], device['model'],
                device.get('price', 0), device.get('status', '')
            ))

    def refresh_my_applications(self):
        """刷新我的申请"""
        for item in self.my_apply_tree.get_children():
            self.my_apply_tree.delete(item)

        apps = AssetService.get_applications({'applicant_id': self.user['id']})
        for app in apps:
            self.my_apply_tree.insert("", tk.END, values=(
                app['id'], app.get('asset_name', ''), app.get('apply_date', ''),
                app.get('status', ''), app.get('approve_comment', '')
            ))

    def submit_asset_apply(self):
        """提交资产申请"""
        selection = self.apply_device_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要申请的设备")
            return

        reason = self.apply_reason_text.get(1.0, tk.END).strip()
        if not reason:
            messagebox.showwarning("提示", "请填写申请原因")
            return

        item = self.apply_device_tree.item(selection[0])
        asset_id = item['values'][0]

        AssetService.apply_for_asset(asset_id, self.user['id'], self.user.get('organization_id', 0), reason)
        self.apply_reason_text.delete(1.0, tk.END)
        self.refresh_my_applications()
        messagebox.showinfo("成功", "申请已提交")

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
        self.dept_msg_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.dept_msg_tree.heading(col, text=col)
            self.dept_msg_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.dept_msg_tree.yview)
        self.dept_msg_tree.configure(yscrollcommand=scrollbar.set)

        self.dept_msg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tk.Button(self.right_frame, text="刷新", command=self.refresh_dept_messages,
                 bg=self.COLORS['primary'], fg="white").pack(pady=5)

        self.refresh_dept_messages()

    def refresh_dept_messages(self):
        """刷新消息列表"""
        for item in self.dept_msg_tree.get_children():
            self.dept_msg_tree.delete(item)

        org_id = self.user.get('organization_id', 0)
        msgs = MessageService.get_received_messages(org_id)
        type_map = {'official': '局名义通知', 'business': '业务通知', 'request': '业务请示'}

        for msg in msgs:
            type_name = type_map.get(msg.get('message_type', 'business'), msg.get('message_type', ''))
            self.dept_msg_tree.insert("", tk.END, values=(
                msg['id'], msg['title'], type_name, msg.get('sender_name', ''), msg.get('create_date', '')
            ))

    def show_professional(self):
        """显示专业功能"""
        self.clear_right_frame()

        dept_name, functions = self.get_department_function()

        # 标题
        tk.Label(self.right_frame, text=f"{dept_name} - 专业功能",
                font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)

        # 功能说明卡片
        if functions:
            card = self.create_card(self.right_frame, "功能模块")
            card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            for i, func in enumerate(functions):
                func_frame = tk.Frame(card, bg=self.COLORS['bg_white'], relief=tk.RIDGE, bd=1)
                func_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(func_frame, text=func, font=("Microsoft YaHei", 12),
                        bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(padx=10, pady=10)

                # 按钮
                btn_frame = tk.Frame(func_frame, bg=self.COLORS['bg_white'])
                btn_frame.pack(padx=10, pady=(0, 10))
                tk.Button(btn_frame, text="进入", command=lambda f=func: self.open_professional_module(f),
                         bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        else:
            # 通用功能
            card = self.create_card(self.right_frame, "功能说明")
            card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            tk.Label(card, text="您所在处室的基础功能模块",
                    font=("Microsoft YaHei", 12), bg=self.COLORS['bg_white']).pack(pady=20)

        # 劳动人事处特殊功能 - 密码审批
        if self.user.get('organization_id') == 11:
            pwd_card = self.create_card(self.right_frame, "密码修改审批")
            pwd_card.pack(fill=tk.X, padx=20, pady=10)

            tk.Label(pwd_card, text="密码修改审批", font=("Microsoft YaHei", 11, "bold"),
                    bg=self.COLORS['bg_light']).pack(anchor="w", padx=15, pady=5)

            # 待审批列表
            columns = ("ID", "用户名", "申请时间", "状态")
            self.pwd_approval_tree = ttk.Treeview(pwd_card, columns=columns, show="headings", height=8)

            for col in columns:
                self.pwd_approval_tree.heading(col, text=col)
                self.pwd_approval_tree.column(col, width=120)

            self.pwd_approval_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

            btn_frame = tk.Frame(pwd_card, bg=self.COLORS['bg_white'])
            btn_frame.pack(padx=15, pady=10)
            tk.Button(btn_frame, text="批准", command=self.approve_password,
                     bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="拒绝", command=self.reject_password,
                     bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="刷新", command=self.refresh_password_approvals,
                     bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

            self.refresh_password_approvals()

    def open_professional_module(self, func_name):
        """打开专业功能模块"""
        messagebox.showinfo("提示", f"正在打开: {func_name}\n该功能模块开发中...")

    def refresh_password_approvals(self):
        """刷新密码审批列表"""
        for item in self.pwd_approval_tree.get_children():
            self.pwd_approval_tree.delete(item)

        sql = """SELECT id, username, apply_date, status FROM password_change_applications WHERE status='pending'"""
        records = db.execute_query(sql)

        for r in records:
            self.pwd_approval_tree.insert("", tk.END, values=(
                r['id'], r['username'], r['apply_date'], r['status']
            ))

    def approve_password(self):
        """批准密码修改"""
        selection = self.pwd_approval_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要批准的申请")
            return

        item = self.pwd_approval_tree.item(selection[0])
        app_id = item['values'][0]

        # 更新状态
        db.execute_update("UPDATE password_change_applications SET status='approved', approver_id=%s, approve_date=NOW() WHERE id=%s",
                         (self.user['id'], app_id))

        # 获取新密码并更新用户密码
        result = db.execute_query("SELECT user_id, new_password FROM password_change_applications WHERE id=%s", (app_id,))
        if result:
            user_id = result[0]['user_id']
            new_pwd = result[0]['new_password']
            db.execute_update("UPDATE users SET password=%s WHERE id=%s", (new_pwd, user_id))

        self.refresh_password_approvals()
        messagebox.showinfo("成功", "已批准密码修改")

    def reject_password(self):
        """拒绝密码修改"""
        selection = self.pwd_approval_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要拒绝的申请")
            return

        item = self.pwd_approval_tree.item(selection[0])
        app_id = item['values'][0]

        db.execute_update("UPDATE password_change_applications SET status='rejected', approver_id=%s, approve_date=NOW() WHERE id=%s",
                         (self.user['id'], app_id))

        self.refresh_password_approvals()
        messagebox.showinfo("成功", "已拒绝密码修改")

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

    def show_register_account(self):
        """显示账号注册页面"""
        self.clear_right_frame()

        # 标题
        tk.Label(self.right_frame, text="账号注册", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)

        # 说明
        note_card = self.create_card(self.right_frame, "说明")
        note_card.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(note_card, text="在此处可以为下属单位或新员工创建账号。账号创建后可直接使用。",
                font=("Microsoft YaHei", 10), bg=self.COLORS['bg_white'], fg="gray").pack(padx=15, pady=10)

        # 注册表单
        form_card = self.create_card(self.right_frame, "注册新账号")
        form_card.pack(fill=tk.X, padx=20, pady=10)

        form_frame = tk.Frame(form_card, bg=self.COLORS['bg_white'])
        form_frame.pack(padx=20, pady=20)

        # 获取组织列表
        from models.organization import Organization
        orgs = Organization.get_all_organizations()
        org_list = [(o['id'], o['name']) for o in orgs]
        org_values = [f"{o[0]} - {o[1]}" for o in org_list]

        # 角色列表
        role_list = [
            ('normal_user', '普通用户'),
            ('unit_user', '下属单位用户'),
            ('office_staff', '办公室职员'),
            ('finance_staff', '财务处职员'),
            ('tech_staff', '科技处职员'),
            ('asset_manager', '资产管理处职员'),
        ]
        role_values = [f"{r[0]} - {r[1]}" for r in role_list]

        # 表单字段
        tk.Label(form_frame, text="用户名:", font=("Microsoft YaHei", 11)).grid(row=0, column=0, padx=10, pady=8, sticky="e")
        username_entry = tk.Entry(form_frame, width=25)
        username_entry.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(form_frame, text="姓名:", font=("Microsoft YaHei", 11)).grid(row=1, column=0, padx=10, pady=8, sticky="e")
        fullname_entry = tk.Entry(form_frame, width=25)
        fullname_entry.grid(row=1, column=1, padx=10, pady=8)

        tk.Label(form_frame, text="初始密码:", font=("Microsoft YaHei", 11)).grid(row=2, column=0, padx=10, pady=8, sticky="e")
        password_entry = tk.Entry(form_frame, width=25, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=8)

        tk.Label(form_frame, text="确认密码:", font=("Microsoft YaHei", 11)).grid(row=3, column=0, padx=10, pady=8, sticky="e")
        confirm_entry = tk.Entry(form_frame, width=25, show="*")
        confirm_entry.grid(row=3, column=1, padx=10, pady=8)

        tk.Label(form_frame, text="归属单位:", font=("Microsoft YaHei", 11)).grid(row=4, column=0, padx=10, pady=8, sticky="e")
        org_var = tk.StringVar()
        org_combo = ttk.Combobox(form_frame, textvariable=org_var, width=23, values=org_values)
        org_combo.grid(row=4, column=1, padx=10, pady=8)
        if org_values:
            org_combo.current(0)

        tk.Label(form_frame, text="角色:", font=("Microsoft YaHei", 11)).grid(row=5, column=0, padx=10, pady=8, sticky="e")
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, width=23, values=role_values)
        role_combo.grid(row=5, column=1, padx=10, pady=8)
        role_combo.current(0)

        def register():
            import hashlib

            username = username_entry.get().strip()
            fullname = fullname_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()

            # 验证输入
            if not username or not fullname or not password:
                messagebox.showwarning("提示", "请填写所有必填字段")
                return

            if password != confirm:
                messagebox.showerror("错误", "两次输入的密码不一致")
                return

            if len(password) < 6:
                messagebox.showwarning("提示", "密码长度至少6位")
                return

            # 获取组织ID
            org_value = org_var.get()
            if org_value and " - " in org_value:
                org_id = int(org_value.split(" - ")[0])
            else:
                messagebox.showwarning("提示", "请选择归属单位")
                return

            # 获取角色
            role_value = role_var.get()
            if role_value and " - " in role_value:
                role = role_value.split(" - ")[0]
            else:
                role = "normal_user"

            # 检查用户名是否已存在
            check_sql = "SELECT COUNT(*) as cnt FROM users WHERE username=%s"
            result = db.execute_query(check_sql, (username,))
            if result and result[0]['cnt'] > 0:
                messagebox.showerror("错误", "用户名已存在")
                return

            # 创建用户
            try:
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                insert_sql = """INSERT INTO users (username, password, role, organization_id, full_name, created_at)
                                VALUES (%s, %s, %s, %s, %s, NOW())"""
                db.execute_update(insert_sql, (username, pwd_hash, role, org_id, fullname))

                messagebox.showinfo("成功", f"账号创建成功！\n用户名: {username}\n密码: {password}")

                # 清空表单
                username_entry.delete(0, tk.END)
                fullname_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                confirm_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("错误", f"创建账号失败: {e}")

        tk.Button(form_frame, text="创建账号", command=register,
                 bg=self.COLORS['success'], fg="white", width=15).grid(row=6, column=1, pady=15)