# -*- coding: utf-8 -*-
"""
办公室窗口 - 公文管理、消息通知
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_window import MainWindow
from services.document_service import DocumentService
from services.message_service import MessageService
from models.organization import Organization
from db.connection import db


class OfficeWindow(MainWindow):
    """办公室窗口"""

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
            ("公文管理", self.show_documents),
            ("消息通知", self.show_messages),
            ("业务请示", self.show_requests),
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

    def show_documents(self):
        """显示公文管理"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="公文管理", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 工具栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)

        tk.Button(toolbar, text="新建公文", command=self.create_document,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="编辑", command=self.edit_document,
                 bg=self.COLORS['secondary'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="删除", command=self.delete_document,
                 bg=self.COLORS['accent'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="发布", command=self.publish_document,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="刷新", command=self.refresh_documents,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        # 公文列表
        columns = ("ID", "标题", "类型", "发送单位", "状态", "创建时间")
        self.doc_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.doc_tree.heading(col, text=col)
            self.doc_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=scrollbar.set)

        self.doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.refresh_documents()

    def refresh_documents(self):
        """刷新公文列表"""
        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)

        docs = DocumentService.get_all_documents()
        type_map = {'notice': '通知', 'report': '报告', 'request': '请示'}

        for doc in docs:
            type_name = type_map.get(doc.get('doc_type', 'notice'), doc.get('doc_type', ''))
            status_map = {'draft': '草稿', 'pending': '待审核', 'published': '已发布', 'replied': '已回复'}
            status_name = status_map.get(doc.get('status', 'draft'), doc.get('status', ''))

            self.doc_tree.insert("", tk.END, values=(
                doc['id'], doc['title'], type_name,
                doc.get('org_name', ''), status_name, doc.get('create_date', '')
            ))

    def create_document(self):
        """创建公文"""
        self.show_document_dialog()

    def edit_document(self):
        """编辑公文"""
        selection = self.doc_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的公文")
            return
        item = self.doc_tree.item(selection[0])
        doc_id = item['values'][0]
        doc = DocumentService.get_document_by_id(doc_id)
        if doc:
            self.show_document_dialog(doc)

    def delete_document(self):
        """删除公文"""
        selection = self.doc_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的公文")
            return
        if messagebox.askyesno("确认", "确定要删除选中的公文吗?"):
            item = self.doc_tree.item(selection[0])
            doc_id = item['values'][0]
            DocumentService.delete_document(doc_id)
            self.refresh_documents()
            messagebox.showinfo("成功", "删除成功")

    def publish_document(self):
        """发布公文"""
        selection = self.doc_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要发布的公文")
            return
        item = self.doc_tree.item(selection[0])
        doc_id = item['values'][0]
        status = item['values'][4]
        if status == '已发布':
            messagebox.showwarning("提示", "该公文已经发布")
            return
        DocumentService.publish_document(doc_id)
        self.refresh_documents()
        messagebox.showinfo("成功", "发布成功")

    def show_document_dialog(self, doc=None):
        """显示公文编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑公文" if doc else "新建公文")
        dialog.geometry("600x500")

        # 表单字段
        fields = [
            ("标题", "title"),
            ("类型", "doc_type"),
        ]

        entries = {}
        tk.Label(dialog, text="标题:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        title_entry = tk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="类型:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        doc_type_var = tk.StringVar(value="notice")
        doc_type_combo = ttk.Combobox(dialog, textvariable=doc_type_var, width=38)
        doc_type_combo['values'] = ('notice', 'report', 'request')
        doc_type_combo.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(dialog, text="内容:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        content_text = tk.Text(dialog, width=40, height=15)
        content_text.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(dialog, text="发布范围:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        scope_text = tk.Entry(dialog, width=40)
        scope_text.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(dialog, text="局名义:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        is_official_var = tk.IntVar(value=0)
        tk.Checkbutton(dialog, text="是", variable=is_official_var).grid(row=4, column=1, sticky="w", padx=10)

        # 附件
        tk.Label(dialog, text="附件:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        attachment_var = tk.StringVar()
        tk.Entry(dialog, textvariable=attachment_var, width=30, state='readonly').grid(row=5, column=1, padx=10, pady=10, sticky="w")

        def select_file():
            from tkinter import filedialog
            filename = filedialog.askopenfilename(title="选择附件", filetypes=[("所有文件", "*.*"), ("文档", "*.doc *.docx *.pdf"), ("图片", "*.jpg *.png")])
            if filename:
                attachment_var.set(filename)

        tk.Button(dialog, text="选择文件", command=select_file).grid(row=5, column=1, padx=150, pady=10, sticky="w")

        if doc:
            title_entry.insert(0, doc.get('title', ''))
            doc_type_var.set(doc.get('doc_type', 'notice'))
            content_text.insert(1.0, doc.get('content', ''))
            scope_text.insert(0, doc.get('receiver_org_ids', ''))
            is_official_var.set(doc.get('is_official', 0))
            attachment_var.set(doc.get('attachment', ''))

        def save():
            data = {
                'title': title_entry.get(),
                'doc_type': doc_type_var.get(),
                'content': content_text.get(1.0, tk.END).strip(),
                'receiver_org_ids': scope_text.get(),
                'is_official': is_official_var.get(),
                'attachment': attachment_var.get()
            }
            if not data['title']:
                messagebox.showwarning("提示", "请输入标题")
                return

            if doc:
                DocumentService.update_document(doc['id'], data)
            else:
                DocumentService.create_document(data, self.user['id'], self.user['organization_id'])

            self.refresh_documents()
            dialog.destroy()
            messagebox.showinfo("成功", "保存成功")

        tk.Button(dialog, text="保存", command=save, bg=self.COLORS['primary'], fg="white").grid(row=5, column=1, pady=20)

    def show_messages(self):
        """显示消息通知"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="消息通知", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 工具栏
        toolbar = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        toolbar.pack(fill=tk.X, padx=20, pady=5)

        tk.Button(toolbar, text="发送通知", command=self.send_message,
                 bg=self.COLORS['success'], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="刷新", command=self.refresh_messages,
                 bg=self.COLORS['primary'], fg="white").pack(side=tk.LEFT, padx=5)

        # 消息列表
        columns = ("ID", "标题", "类型", "发送人", "发送时间")
        self.msg_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.msg_tree.heading(col, text=col)
            self.msg_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.msg_tree.yview)
        self.msg_tree.configure(yscrollcommand=scrollbar.set)

        self.msg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        self.refresh_messages()

    def refresh_messages(self):
        """刷新消息列表"""
        for item in self.msg_tree.get_children():
            self.msg_tree.delete(item)

        # 获取所有消息
        from db.connection import db
        sql = """SELECT m.*, u.full_name as sender_name
                 FROM messages m
                 LEFT JOIN users u ON m.sender_id = u.id
                 ORDER BY m.create_date DESC"""
        msgs = db.execute_query(sql)

        type_map = {'official': '局名义通知', 'business': '业务通知', 'request': '业务请示'}

        for msg in msgs:
            type_name = type_map.get(msg.get('message_type', 'business'), msg.get('message_type', ''))
            self.msg_tree.insert("", tk.END, values=(
                msg['id'], msg['title'], type_name,
                msg.get('sender_name', ''), msg.get('create_date', '')
            ))

    def send_message(self):
        """发送消息"""
        self.show_message_dialog()

    def show_message_dialog(self, msg=None):
        """显示消息编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("发送消息" if not msg else "编辑消息")
        dialog.geometry("500x400")

        tk.Label(dialog, text="标题:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        title_entry = tk.Entry(dialog, width=35)
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="类型:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        msg_type_var = tk.StringVar(value="business")
        msg_type_combo = ttk.Combobox(dialog, textvariable=msg_type_var, width=33)
        msg_type_combo['values'] = ('official', 'business', 'request')
        msg_type_combo.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(dialog, text="内容:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        content_text = tk.Text(dialog, width=35, height=12)
        content_text.grid(row=2, column=1, padx=10, pady=10)

        if msg:
            title_entry.insert(0, msg.get('title', ''))
            msg_type_var.set(msg.get('message_type', 'business'))
            content_text.insert(1.0, msg.get('content', ''))

        def send():
            if not title_entry.get():
                messagebox.showwarning("提示", "请输入标题")
                return

            from db.connection import db
            sql = """INSERT INTO messages (title, content, sender_id, sender_org_id, message_type, is_public, create_date)
                     VALUES (%s, %s, %s, %s, %s, 1, NOW())"""
            db.execute_update(sql, (
                title_entry.get(),
                content_text.get(1.0, tk.END).strip(),
                self.user['id'],
                self.user['organization_id'],
                msg_type_var.get()
            ))

            self.refresh_messages()
            dialog.destroy()
            messagebox.showinfo("成功", "发送成功")

        tk.Button(dialog, text="发送", command=send, bg=self.COLORS['primary'], fg="white").grid(row=3, column=1, pady=20)

    def show_requests(self):
        """显示业务请示"""
        self.clear_right_frame()

        # 标题
        title_frame = tk.Frame(self.right_frame, bg=self.COLORS['bg_white'])
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(title_frame, text="业务请示", font=("Microsoft YaHei", 18, "bold"),
                bg=self.COLORS['bg_white'], fg=self.COLORS['primary']).pack(side=tk.LEFT)

        # 请示列表（从消息表中获取业务请示类型）
        columns = ("ID", "标题", "发送单位", "发送时间", "状态")
        self.req_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=22)

        for col in columns:
            self.req_tree.heading(col, text=col)
            self.req_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.req_tree.yview)
        self.req_tree.configure(yscrollcommand=scrollbar.set)

        self.req_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 工具栏
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

        from db.connection import db
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

        from db.connection import db
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

            from db.connection import db
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

            # 验证原密码
            user = User.get_by_id(self.user['id'])
            old_hash = hashlib.sha256(old_password.encode()).hexdigest()
            if user['password'] != old_hash:
                messagebox.showerror("错误", "原密码错误")
                return

            # 提交申请
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