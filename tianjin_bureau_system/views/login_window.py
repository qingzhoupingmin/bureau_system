# -*- coding: utf-8 -*-
"""
登录窗口 - 美化版
"""
import tkinter as tk
from tkinter import ttk, messagebox
from services.auth_service import AuthService
from config import SYSTEM_NAME
from PIL import Image, ImageTk
import os


class LoginWindow:
    """登录窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{SYSTEM_NAME} - 登录")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f4f8')

        # 居中显示
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 450) // 2
        self.root.geometry(f"500x450+{x}+{y}")

        self.current_user = None
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 顶部蓝色标题栏
        header_frame = tk.Frame(self.root, bg='#1a5fb4', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # 单位Logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'logo.png')
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_frame, image=self.logo_photo, bg='#1a5fb4')
            logo_label.pack(side='left', padx=20, pady=10)
        except Exception as e:
            print(f"加载Logo失败: {e}")

        # 系统标题
        title_label = tk.Label(header_frame, text=SYSTEM_NAME, font=("Microsoft YaHei", 16, "bold"), 
                              bg='#1a5fb4', fg='white')
        title_label.pack(side='left', padx=10, pady=10)

        # 主内容区
        content_frame = tk.Frame(self.root, bg='#f0f4f8')
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)

        # 欢迎文字
        welcome_label = tk.Label(content_frame, text="欢迎使用", font=("Microsoft YaHei", 14), 
                                bg='#f0f4f8', fg='#333333')
        welcome_label.pack(pady=(0, 20))

        # 登录表单框架
        form_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # 用户名
        tk.Label(form_frame, text="用户名:", font=("Microsoft YaHei", 11), bg='white', fg='#555555').pack(anchor='w', padx=20, pady=(20, 5))
        self.username_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 11), width=30, relief='solid', bd=1)
        self.username_entry.pack(fill='x', padx=20, pady=5)

        # 密码
        tk.Label(form_frame, text="密码:", font=("Microsoft YaHei", 11), bg='white', fg='#555555').pack(anchor='w', padx=20, pady=(15, 5))
        self.password_entry = tk.Entry(form_frame, font=("Microsoft YaHei", 11), width=30, show="*", relief='solid', bd=1)
        self.password_entry.pack(fill='x', padx=20, pady=5)

        # 登录按钮
        login_btn = tk.Button(form_frame, text="登 录", font=("Microsoft YaHei", 12, "bold"), 
                             bg='#1a5fb4', fg='white', activebackground='#154a8c',
                             cursor='hand2', relief='flat', command=self.do_login)
        login_btn.pack(fill='x', padx=20, pady=25)

        # 绑定回车键
        self.password_entry.bind("Return", lambda e: self.do_login())

        # 底部版权
        footer_label = tk.Label(self.root, text="Copyright 2026 天津市市政工程局", 
                               font=("Microsoft YaHei", 9), bg='#f0f4f8', fg='#888888')
        footer_label.pack(side='bottom', pady=10)

    def do_login(self):
        """执行登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        user = AuthService.login(username, password)
        if user:
            self.current_user = user
            self.root.destroy()
        else:
            messagebox.showerror("错误", "用户名或密码错误")

    def show(self):
        """显示窗口并返回当前用户"""
        self.root.mainloop()
        return self.current_user
