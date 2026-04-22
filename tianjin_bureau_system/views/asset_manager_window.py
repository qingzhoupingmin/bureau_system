# -*- coding: utf-8 -*-
"""
资产管理处窗口 - 完整功能版
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from services.asset_service import AssetService
from services.auth_service import AuthService
from models.organization import Organization
from models.user import User
from models.asset import Asset
from db.connection import db


class AssetManagerWindow(MainWindow):
    """资产管理处窗口"""

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
            ("资产管理", self.show_assets),
            ("申请审批", self.show_applications),
            ("资产统计", self.show_statistics),
            ("用户管理", self.show_users),
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
        
        # 标题
        title = tk.Label(self.right_frame, text="单位概况", 
                        font=("Microsoft YaHei", 18, "bold"),
                        bg=self.COLORS['bg_white'], fg=self.COLORS['primary'])
        title.pack(pady=20)
        
        # 创建左右分栏
        content_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧 - 单位职能介绍
        left_card = self.create_card(content_frame, "单位职能介绍")
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        intro_text = """天津市市政工程局是负责全市市政工程建设和管理的具体行政职能的市政府直属事业单位。

主要职能：
• 制定市政工程发展规划和年度计划
• 负责城市道路、桥梁、隧道等基础设施的建设与维护
• 组织市政工程项目的立项、审批和监督管理
• 管理市政工程质量和安全生产
• 负责市政设施养护和应急抢险
• 指导下属单位开展业务工作

组织架构：
• 局机关设有19个处室
• 下辖20个事业单位
• 负责全市市政公路行业管理"""
        
        intro_label = tk.Label(left_card, text=intro_text, font=("Microsoft YaHei", 11),
                              bg=self.COLORS['bg_white'], justify=tk.LEFT, wraplength=400)
        intro_label.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 右侧 - 内设机构与下属单位
        right_frame = tk.Frame(content_frame, bg=self.COLORS['bg_white'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 内设机构 - 使用Canvas实现滚动
        dept_card = self.create_card(right_frame, "内设机构（19个处室）")
        dept_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Canvas和滚动条
        dept_canvas = tk.Canvas(dept_card, bg=self.COLORS['bg_white'], highlightthickness=0)
        dept_scrollbar = ttk.Scrollbar(dept_card, orient="vertical", command=dept_canvas.yview)
        dept_canvas.configure(yscrollcommand=dept_scrollbar.set)
        
        dept_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        dept_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        dept_frame = tk.Frame(dept_canvas, bg=self.COLORS['bg_white'])
        dept_canvas.create_window((0, 0), window=dept_frame, anchor="nw", width=380)
        
        depts = [
            ("办公室", "综合协调、文秘、后勤、信访、外事"),
            ("计划处", "计划编制、项目立项、投资管理"),
            ("设施管理处", "设施维护计划、设施台账管理"),
            ("设施养护处", "道路桥梁养护、养护工程质量监督"),
            ("建设管理处", "工程建设管理、招投标监管、工程进度"),
            ("规划处", "市政规划编制、规划方案审查"),
            ("财务处", "预算管理、资金拨付、财务核算"),
            ("规费管理处", "规费征收、费用标准制定"),
            ("审计处", "内部审计、财务监督、项目审计"),
            ("资产管理处", "资产登记、资产调拨、资产统计"),
            ("劳动人事处", "人事管理、职称评定、工资福利"),
            ("科技处", "科研项目管理、技术创新、信息化"),
            ("安全保卫处", "安全生产、武装工作、保卫"),
            ("法规处", "法规政策研究、行政执法监督"),
            ("党委办公室", "党委日常事务、党建"),
            ("纪检委", "纪检监察、廉政建设"),
            ("宣传部", "宣传教育、精神文明建设"),
            ("组织部", "干部管理、党员管理、统战"),
            ("老干部处", "老干部服务、离休退休管理"),
        ]
        
        for dept_name, desc in depts:
            dept_btn = tk.Button(dept_frame, text=f"{dept_name} - {desc}",
                                font=("Microsoft YaHei", 10),
                                bg=self.COLORS['bg_light'], fg=self.COLORS['text_dark'],
                                relief=tk.FLAT, anchor="w",
                                command=lambda n=dept_name, d=desc: self.show_dept_detail(n, d))
            dept_btn.pack(fill=tk.X, pady=2)
        
        dept_frame.update_idletasks()
        dept_canvas.configure(scrollregion=dept_canvas.bbox("all"))
        
        # 下属单位 - 使用Canvas实现滚动
        unit_card = self.create_card(right_frame, "下属单位（20个）")
        unit_card.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 创建Canvas和滚动条
        unit_canvas = tk.Canvas(unit_card, bg=self.COLORS['bg_white'], highlightthickness=0)
        unit_scrollbar = ttk.Scrollbar(unit_card, orient="vertical", command=unit_canvas.yview)
        unit_canvas.configure(yscrollcommand=unit_scrollbar.set)
        
        unit_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        unit_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        unit_frame = tk.Frame(unit_canvas, bg=self.COLORS['bg_white'])
        unit_canvas.create_window((0, 0), window=unit_frame, anchor="nw", width=380)
        
        units = [
            ("天津市公路处", "负责公路建设、养护和管理"),
            ("天津市高速公路管理处", "负责高速公路运营管理"),
            ("天津市道路桥梁管理处", "负责城市道路桥梁管理"),
            ("天津市市政工程经济技术定额研究站（天津市公路工程定额管理站）", "负责工程定额研究和造价管理"),
            ("天津市市政工程配套办公室", "负责市政工程配套设施建设"),
            ("天津市市政工程研究院（天津市公路工程研究院）", "负责工程技术研究和检测"),
            ("天津市市政工程设计研究院", "负责工程设计和咨询"),
            ("天津市市政工程学校", "负责专业技术人才培养"),
            ("天津市市政公路管理局干部中等专业学校（中国共产党天津市市政公路管理局委员会党校）", "负责干部培训和党校教育"),
            ("天津市市政公路管理局技工学校", "负责技工培训和技能鉴定"),
            ("天津市市政工程建设公司（天津市市政公路利用世界银行贷款办公室）", "负责市政工程施工建设"),
            ("天津市贷款道路建设车辆通行费征收办公室", "负责通行费征收管理"),
            ("天津市贷款道路建设车辆通行费稽查管理处", "负责通行费稽查管理"),
            ("天津市公路养路费征稽处", "负责养路费征稽工作"),
            ("天津市公路养护工程处", "负责公路养护工程施工"),
            ("天津市乡村公路管理办公室", "负责乡村公路建设管理"),
            ("天津市市政公路工程质量监督站（天津市公路工程质量安全监督站）", "负责工程质量监督检测"),
            ("天津市地铁管理处", "负责地铁建设协调管理"),
            ("天津市市政公路信息中心", "负责信息化建设和信息管理"),
            ("天津市市政公路行业管理办公室", "负责行业管理和协调服务"),
        ]
        
        for unit_name, desc in units:
            unit_btn = tk.Button(unit_frame, text=f"{unit_name}",
                                font=("Microsoft YaHei", 10),
                                bg=self.COLORS['bg_light'], fg=self.COLORS['text_dark'],
                                relief=tk.FLAT, anchor="w",
                                command=lambda n=unit_name, d=desc: self.show_unit_detail(n, d))
            unit_btn.pack(fill=tk.X, pady=2)
        
        unit_frame.update_idletasks()
        unit_canvas.configure(scrollregion=unit_canvas.bbox("all"))

    def show_dept_detail(self, name, desc):
        """显示处室详情"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"{name} - 详细介绍")
        detail_window.geometry("500x400")
        
        # 标题
        tk.Label(detail_window, text=name, font=("Microsoft YaHei", 16, "bold"),
                fg=self.COLORS['primary']).pack(pady=20)
        
        # 职能描述
        tk.Label(detail_window, text=f"主要职能：{desc}",
                font=("Microsoft YaHei", 11), wraplength=450).pack(pady=10)
        
        # 详细介绍
        detail_text = f"""
{name}是天津市市政工程局的重要组成部门。

主要职责：
• {desc}
• 贯彻执行国家和本市有关政策法规
• 制定本部门工作计划和实施方案
• 协调配合其他处室开展工作
• 完成局领导交办的其他任务

联系方式：
地址：天津市XX区XX路XX号
电话：022-XXXXXXXX
        """
        
        text_widget = tk.Text(detail_window, font=("Microsoft YaHei", 11),
                             wrap=tk.WORD, padx=20, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text_widget.insert(tk.END, detail_text)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(detail_window, text="关闭", command=detail_window.destroy,
                 bg=self.COLORS['primary'], fg="white").pack(pady=10)

    def show_unit_detail(self, name, desc):
        """显示下属单位详情"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"{name} - 详细介绍")
        detail_window.geometry("500x400")
        
        # 标题
        tk.Label(detail_window, text=name, font=("Microsoft YaHei", 16, "bold"),
                fg=self.COLORS['primary']).pack(pady=20)
        
        # 职能描述
        tk.Label(detail_window, text=f"主要职能：{desc}",
                font=("Microsoft YaHei", 11), wraplength=450).pack(pady=10)
        
        # 详细介绍
        detail_text = f"""
{name}是天津市市政工程局下属事业单位。

单位简介：
• {desc}
• 接受市市政工程局的业务指导和监督管理
• 负责本单位职责范围内的具体工作
• 完成上级交办的其他任务

业务范围：
• 承担相关市政工程建设和管理工作
• 提供专业技术支持和服务
• 参与行业技术研究和标准制定

联系方式：
地址：天津市XX区XX路XX号
电话：022-XXXXXXXX
        """
        
        text_widget = tk.Text(detail_window, font=("Microsoft YaHei", 11),
                             wrap=tk.WORD, padx=20, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text_widget.insert(tk.END, detail_text)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(detail_window, text="关闭", command=detail_window.destroy,
                 bg=self.COLORS['primary'], fg="white").pack(pady=10)

    def show_assets(self):
        """显示资产管理"""
        self.clear_right_frame()
        
        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="资产管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)
        
        # 工具栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Button(toolbar, text="添加资产", command=self.add_asset,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="编辑资产", command=self.edit_asset,
                 bg=self.COLORS['secondary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="删除资产", command=self.delete_asset,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="刷新", command=self.refresh_assets,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        
        # 搜索栏
        search_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        search_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="查询", command=self.search_assets).pack(side=tk.LEFT, padx=5)
        
        # 资产列表
        columns = ("ID", "名称", "类别", "型号", "金额", "状态", "保管人", "归属")
        self.asset_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.asset_tree.heading(col, text=col)
            self.asset_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.asset_tree.yview)
        self.asset_tree.configure(yscrollcommand=scrollbar.set)
        
        self.asset_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        self.refresh_assets()

    def refresh_assets(self):
        """刷新资产列表"""
        for item in self.asset_tree.get_children():
            self.asset_tree.delete(item)
        
        assets = Asset.get_all_assets()
        for asset in assets:
            self.asset_tree.insert("", tk.END, values=(
                asset['id'], asset['name'], asset['category'], asset['model'],
                asset['price'], asset['status'], asset['caretaker'], asset.get('org_name', '')
            ))

    def search_assets(self):
        """搜索资产"""
        keyword = self.search_entry.get().strip()
        for item in self.asset_tree.get_children():
            self.asset_tree.delete(item)
        assets = Asset.get_all_assets({'keyword': keyword} if keyword else None)
        for asset in assets:
            self.asset_tree.insert("", tk.END, values=(
                asset['id'], asset['name'], asset['category'], asset['model'],
                asset['price'], asset['status'], asset['caretaker'], asset.get('org_name', '')
            ))

    def add_asset(self):
        """添加资产"""
        self.show_asset_dialog()

    def edit_asset(self):
        """编辑资产"""
        selection = self.asset_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的资产")
            return
        item = self.asset_tree.item(selection[0])
        asset_id = item['values'][0]
        asset = Asset.get_by_id(asset_id)
        if asset:
            self.show_asset_dialog(asset)

    def delete_asset(self):
        """删除资产"""
        selection = self.asset_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的资产")
            return
        if messagebox.askyesno("确认", "确定要删除选中的资产吗?"):
            item = self.asset_tree.item(selection[0])
            asset_id = item['values'][0]
            Asset.delete_asset(asset_id)
            self.refresh_assets()
            messagebox.showinfo("成功", "删除成功")

    def show_asset_dialog(self, asset=None):
        """显示资产编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑资产" if asset else "添加资产")
        dialog.geometry("500x600")

        # 获取组织列表
        from models.organization import Organization
        from config import ASSET_CATEGORIES

        orgs = Organization.get_all_organizations()
        org_list = [(0, "请选择归属单位")] + [(o['id'], o['name']) for o in orgs]
        org_values = [f"{o[0]} - {o[1]}" for o in org_list]

        # 资产类别列表
        category_list = ["请选择类别"] + list(ASSET_CATEGORIES.values())

        # 表单字段
        fields = [
            ("名称", "name"),
            ("类别", "category"),
            ("型号", "model"),
            ("序列号", "serial_number"),
            ("金额", "price"),
            ("位置", "location"),
            ("保管人", "caretaker"),
            ("归属", "organization_id"),
        ]

        entries = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(dialog, text=f"{label}:").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            if field == "category":
                # 类别使用下拉框
                cat_var = tk.StringVar()
                cat_combo = ttk.Combobox(dialog, textvariable=cat_var, width=28, values=category_list)
                cat_combo.grid(row=i, column=1, padx=10, pady=5)
                cat_combo.current(0)
                entries[field] = cat_var
            elif field == "organization_id":
                # 归属单位使用下拉框
                org_var = tk.StringVar()
                org_combo = ttk.Combobox(dialog, textvariable=org_var, width=28, values=org_values)
                org_combo.grid(row=i, column=1, padx=10, pady=5)
                org_combo.current(0)
                entries[field] = org_var
            else:
                entry = tk.Entry(dialog, width=30)
                entry.grid(row=i, column=1, padx=10, pady=5)
                if asset:
                    entry.insert(0, str(asset.get(field, "")))
                entries[field] = entry

        # 如果是编辑模式，预设已有值
        if asset:
            # 设置类别
            cat_val = asset.get('category', '')
            if cat_val:
                for idx, cat in enumerate(ASSET_CATEGORIES.values()):
                    if cat == cat_val:
                        entries['category'].current(idx + 1)
                        break
            # 设置归属单位
            org_id = asset.get('organization_id', 0)
            if org_id and org_id > 0:
                for idx, (oid, oname) in enumerate(org_list):
                    if oid == org_id:
                        entries['organization_id'].current(idx)
                        break

        def save():
            data = {}
            for k, v in entries.items():
                if k == "category":
                    # 从下拉框值中获取类别
                    val = v.get()
                    if val and val != "请选择类别":
                        # 反向查找key
                        for key, label in ASSET_CATEGORIES.items():
                            if label == val:
                                data[k] = label
                                break
                    else:
                        data[k] = ""
                elif k == "organization_id":
                    # 从下拉框值中提取ID
                    val = v.get()
                    if val and " - " in val:
                        org_id = int(val.split(" - ")[0])
                        data[k] = org_id if org_id > 0 else 0
                    else:
                        data[k] = 0
                else:
                    data[k] = v.get() if isinstance(v, tk.Entry) else v.get()
            if asset:
                Asset.update_asset(asset['id'], **data, status='normal', is_public=0)
            else:
                Asset.create_asset(**data, purchase_date='2024-01-01', status='normal', is_public=0)
            self.refresh_assets()
            dialog.destroy()
            messagebox.showinfo("成功", "保存成功")

        tk.Button(dialog, text="保存", command=save).grid(row=len(fields), column=1, pady=20)

    def show_applications(self):
        """显示申请审批"""
        self.clear_right_frame()
        
        tk.Label(self.right_frame, text="申请审批", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)
        
        # 申请列表
        columns = ("ID", "资产", "申请人", "申请单位", "申请原因", "申请时间", "状态")
        self.apply_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.apply_tree.heading(col, text=col)
            self.apply_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.apply_tree.yview)
        self.apply_tree.configure(yscrollcommand=scrollbar.set)
        
        self.apply_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # 按钮
        btn_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text="批准", command=self.approve_apply,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="拒绝", command=self.reject_apply,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_applies,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        
        self.refresh_applies()

    def refresh_applies(self):
        """刷新申请列表"""
        for item in self.apply_tree.get_children():
            self.apply_tree.delete(item)
        # 从数据库获取申请数据
        from db.connection import db
        sql = """SELECT aa.*, a.name as asset_name, u.full_name as applicant_name, o.name as org_name 
                 FROM asset_applications aa 
                 LEFT JOIN assets a ON aa.asset_id = a.id 
                 LEFT JOIN users u ON aa.applicant_id = u.id 
                 LEFT JOIN organizations o ON aa.applicant_org_id = o.id 
                 ORDER BY aa.id DESC"""
        applications = db.execute_query(sql)
        for app in applications:
            self.apply_tree.insert("", tk.END, values=(
                app['id'], app.get('asset_name', ''), app.get('applicant_name', ''),
                app.get('org_name', ''), app['reason'], app['apply_date'], app['status']
            ))

    def approve_apply(self):
        """批准申请"""
        selection = self.apply_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要批准的申请")
            return
        item = self.apply_tree.item(selection[0])
        app_id = item['values'][0]
        from db.connection import db
        db.execute_update("UPDATE asset_applications SET status='approved', approver_id=%s, approve_date=NOW() WHERE id=%s",
                         (self.user['id'], app_id))
        self.refresh_applies()
        messagebox.showinfo("成功", "已批准")

    def reject_apply(self):
        """拒绝申请"""
        selection = self.apply_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要拒绝的申请")
            return
        item = self.apply_tree.item(selection[0])
        app_id = item['values'][0]
        from db.connection import db
        db.execute_update("UPDATE asset_applications SET status='rejected', approver_id=%s, approve_date=NOW() WHERE id=%s",
                         (self.user['id'], app_id))
        self.refresh_applies()
        messagebox.showinfo("成功", "已拒绝")

    def show_statistics(self):
        """显示资产统计"""
        self.clear_right_frame()
        
        tk.Label(self.right_frame, text="资产统计", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)
        
        # 统计文本框
        self.stat_text = tk.Text(self.right_frame, font=("Consolas", 12), wrap=tk.WORD)
        self.stat_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.load_statistics()

    def load_statistics(self):
        """加载统计信息"""
        stats = Asset.get_statistics()
        text = f"""
资产统计报表
================================

资产总数: {stats['total']}
资产总金额: {stats['total_price']:.2f} 元

按类别统计:
"""
        for cat, count in stats.get('by_category', {}).items():
            text += f"  {cat}: {count}\n"

        text += "\n按状态统计:\n"
        for status, count in stats.get('by_status', {}).items():
            text += f"  {status}: {count}\n"

        text += "\n按处室分布:\n"
        for org, count in stats.get('by_org', {}).items():
            text += f"  {org}: {count}\n"

        self.stat_text.delete(1.0, tk.END)
        self.stat_text.insert(tk.END, text)

    def show_users(self):
        """显示用户管理"""
        self.clear_right_frame()
        
        tk.Label(self.right_frame, text="用户管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(pady=20)
        
        # 工具栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(toolbar, text="添加用户", command=self.add_user,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="编辑用户", command=self.edit_user,
                 bg=self.COLORS['secondary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="删除用户", command=self.delete_user,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="刷新", command=self.refresh_users,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)
        
        # 用户列表
        columns = ("ID", "用户名", "姓名", "角色", "组织", "职位")
        self.user_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=25)
        
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        self.refresh_users()

    def refresh_users(self):
        """刷新用户列表"""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        users = User.get_all_users()
        for user in users:
            self.user_tree.insert("", tk.END, values=(
                user['id'], user['username'], user['full_name'],
                user['role'], user.get('org_name', ''), user.get('position', '')
            ))

    def add_user(self):
        """添加用户"""
        self.show_user_dialog()

    def edit_user(self):
        """编辑用户"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的用户")
            return
        item = self.user_tree.item(selection[0])
        user_id = item['values'][0]
        user = User.get_by_id(user_id)
        if user:
            self.show_user_dialog(user)

    def delete_user(self):
        """删除用户"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的用户")
            return
        if messagebox.askyesno("确认", "确定要删除选中的用户吗?"):
            item = self.user_tree.item(selection[0])
            user_id = item['values'][0]
            User.delete_user(user_id)
            self.refresh_users()
            messagebox.showinfo("成功", "删除成功")

    def show_user_dialog(self, user=None):
        """显示用户编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑用户" if user else "添加用户")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="用户名:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        username_entry = tk.Entry(dialog, width=25)
        username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="姓名:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        fullname_entry = tk.Entry(dialog, width=25)
        fullname_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="角色:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        role_var = tk.StringVar(value="normal_user")
        role_combo = ttk.Combobox(dialog, textvariable=role_var, width=23)
        role_combo['values'] = ('system_admin', 'asset_manager', 'office_staff', 'tech_staff', 'finance_staff', 'unit_user', 'normal_user', 'leader')
        role_combo.grid(row=2, column=1, padx=10, pady=5)
        
        if user:
            username_entry.insert(0, user['username'])
            fullname_entry.insert(0, user['full_name'])
            role_var.set(user['role'])
            username_entry.config(state='readonly')
        
        def save():
            if user:
                User.update_user(user['id'], fullname_entry.get(), '', role_var.get())
            else:
                User.create_user(username_entry.get(), '123456', role_var.get(), 0, fullname_entry.get())
            self.refresh_users()
            dialog.destroy()
            messagebox.showinfo("成功", "保存成功")
        
        tk.Button(dialog, text="保存", command=save).grid(row=3, column=1, pady=20)

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
        
        # 修改密码申请卡片
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
        
        # 说明标签
        note_text = "说明：密码修改申请将提交至劳动人事处审批，审批通过后密码才会生效。"
        tk.Label(pwd_frame, text=note_text, font=("Microsoft YaHei", 9), fg="gray",
                wraplength=400, justify=tk.LEFT).grid(row=3, column=0, columnspan=2, pady=10)
        
        def submit_pwd_application():
            """提交密码修改申请"""
            old_password = old_pwd.get()
            new_password = new_pwd.get()
            confirm_password = confirm_pwd.get()
            
            # 验证输入
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
            
            # 提交申请到劳动人事处
            try:
                from db.connection import db
                sql = """INSERT INTO password_change_applications
                         (user_id, username, old_password, new_password, status, apply_date)
                         VALUES (%s, %s, %s, %s, 'pending', NOW())"""
                new_hash = hashlib.sha256(new_password.encode()).hexdigest()
                db.execute_update(sql, (self.user['id'], self.user['username'], old_hash, new_hash))
                
                messagebox.showinfo("成功", "密码修改申请已提交至劳动人事处，请等待审批。")
                old_pwd.delete(0, tk.END)
                new_pwd.delete(0, tk.END)
                confirm_pwd.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("错误", f"提交申请失败: {e}")
        
        tk.Button(pwd_frame, text="提交申请", font=("Microsoft YaHei", 11),
                 bg=self.COLORS['primary'], fg="white",
                 command=submit_pwd_application).grid(row=4, column=1, pady=10)
        
        # 申请记录卡片
        record_card = self.create_card(self.right_frame, "我的密码修改申请记录")
        record_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建表格显示申请记录
        columns = ("申请时间", "状态", "审批时间", "审批意见")
        self.pwd_record_tree = ttk.Treeview(record_card, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.pwd_record_tree.heading(col, text=col)
            self.pwd_record_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(record_card, orient=tk.VERTICAL, command=self.pwd_record_tree.yview)
        self.pwd_record_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pwd_record_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        self.refresh_pwd_records()
    
    def refresh_pwd_records(self):
        """刷新密码修改申请记录"""
        if hasattr(self, 'pwd_record_tree'):
            for item in self.pwd_record_tree.get_children():
                self.pwd_record_tree.delete(item)
            
            try:
                from db.connection import db
                sql = """SELECT apply_date, status, approve_date, approve_comment 
                         FROM password_change_applications 
                         WHERE user_id = %s ORDER BY apply_date DESC"""
                records = db.execute_query(sql, (self.user['id'],))
                
                status_map = {'pending': '待审批', 'approved': '已通过', 'rejected': '已拒绝'}
                for record in records:
                    status = status_map.get(record['status'], record['status'])
                    approve_date = record['approve_date'] if record['approve_date'] else '-'
                    comment = record['approve_comment'] if record['approve_comment'] else '-'
                    self.pwd_record_tree.insert("", tk.END, values=(
                        record['apply_date'], status, approve_date, comment
                    ))
            except Exception as e:
                print(f"加载密码修改记录失败: {e}")
