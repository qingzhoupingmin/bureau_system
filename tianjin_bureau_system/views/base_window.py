# -*- coding: utf-8 -*-
"""
通用主窗口基类 - 美化版
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import SYSTEM_NAME, DEPARTMENTS
from PIL import Image, ImageTk
import os


class MainWindow:
    """主窗口基类"""

    # 配色方案
    COLORS = {
        'primary': '#1a5490',      # 深蓝色 - 主色调
        'secondary': '#2980b9',    # 中蓝色
        'accent': '#e74c3c',       # 红色 - 强调色
        'success': '#27ae60',      # 绿色
        'warning': '#f39c12',      # 橙色
        'bg_light': '#ecf0f1',     # 浅灰背景
        'bg_white': '#ffffff',     # 白色
        'bg_primary': '#f5f6fa',   # 主背景色
        'bg_secondary': '#ffffff', # 次要背景色
        'text_dark': '#2c3e50',    # 深色文字
        'text_light': '#7f8c8d',   # 浅色文字
        'text_primary': '#2c3e50', # 主要文字颜色
        'text_secondary': '#7f8c8d', # 次要文字颜色
    }

    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"{SYSTEM_NAME} - {user['full_name']}")
        self.root.geometry("1400x800")
        self.root.configure(bg=self.COLORS['bg_white'])

        # 加载徽章图片
        self.logo_img = self.load_logo()

        self.current_user = user
        self.create_widgets()

    def load_logo(self):
        """加载单位Logo"""
        try:
            # 尝试加载logo.png，如果不存在则使用默认徽章
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'logo.png')
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            # 如果没有logo.png，尝试加载badge.png作为备选
            badge_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'badge.png')
            if os.path.exists(badge_path):
                img = Image.open(badge_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"加载Logo失败: {e}")
        return None

    def create_widgets(self):
        """创建主窗口组件"""
        # 顶部标题栏 - 渐变效果
        top_frame = tk.Frame(self.root, bg=self.COLORS['primary'], height=70)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)

        # 左侧 - 徽章和标题
        left_frame = tk.Frame(top_frame, bg=self.COLORS['primary'])
        left_frame.pack(side=tk.LEFT, padx=20)

        # 显示徽章
        if self.logo_img:
            logo_label = tk.Label(left_frame, image=self.logo_img, bg=self.COLORS['primary'])
            logo_label.pack(side=tk.LEFT, padx=(0, 15))

        title_label = tk.Label(left_frame, text=SYSTEM_NAME,
                              font=("Microsoft YaHei", 18, "bold"),
                              bg=self.COLORS['primary'], fg="white")
        title_label.pack(side=tk.LEFT)

        # 右侧 - 用户信息和退出
        right_frame = tk.Frame(top_frame, bg=self.COLORS['primary'])
        right_frame.pack(side=tk.RIGHT, padx=20)

        # 用户头像占位
        user_frame = tk.Frame(right_frame, bg=self.COLORS['primary'])
        user_frame.pack(side=tk.LEFT, padx=(0, 15))

        user_avatar = tk.Label(user_frame, text="👤", font=("Microsoft YaHei", 24),
                              bg=self.COLORS['primary'], fg="white")
        user_avatar.pack()

        # 用户信息
        info_frame = tk.Frame(right_frame, bg=self.COLORS['primary'])
        info_frame.pack(side=tk.LEFT, padx=(0, 20))

        user_name = tk.Label(info_frame, text=self.user['full_name'],
                            font=("Microsoft YaHei", 11, "bold"),
                            bg=self.COLORS['primary'], fg="white")
        user_name.pack(anchor="w")

        role_name = self.get_role_name()
        role_label = tk.Label(info_frame, text=role_name,
                             font=("Microsoft YaHei", 9),
                             bg=self.COLORS['primary'], fg="#bdc3c7")
        role_label.pack(anchor="w")

        # 退出按钮
        logout_btn = tk.Button(right_frame, text="退出登录",
                              command=self.logout,
                              bg=self.COLORS['accent'],
                              fg="white",
                              font=("Microsoft YaHei", 10),
                              relief=tk.FLAT,
                              padx=15, pady=5,
                              cursor="hand2")
        logout_btn.pack(side=tk.LEFT)

        # 主内容区
        self.main_frame = tk.Frame(self.root, bg=self.COLORS['bg_light'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建标签页
        self.create_notebook()

        # 状态栏
        status_frame = tk.Frame(self.root, bg=self.COLORS['bg_white'],
                               highlightbackground="#ddd",
                               highlightthickness=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 状态栏左侧 - 系统状态
        status_left = tk.Frame(status_frame, bg=self.COLORS['bg_white'])
        status_left.pack(side=tk.LEFT, padx=10, pady=5)

        status_icon = tk.Label(status_left, text="●", fg=self.COLORS['success'],
                              bg=self.COLORS['bg_white'], font=("Microsoft YaHei", 10))
        status_icon.pack(side=tk.LEFT, padx=(0, 5))

        self.status_label = tk.Label(status_left, text="系统运行正常",
                                    bg=self.COLORS['bg_white'],
                                    fg=self.COLORS['text_dark'],
                                    font=("Microsoft YaHei", 9))
        self.status_label.pack(side=tk.LEFT)

        # 状态栏右侧 - 时间
        status_right = tk.Frame(status_frame, bg=self.COLORS['bg_white'])
        status_right.pack(side=tk.RIGHT, padx=10, pady=5)

        import datetime
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        time_label = tk.Label(status_right, text=f"当前时间: {time_str}",
                             bg=self.COLORS['bg_white'],
                             fg=self.COLORS['text_light'],
                             font=("Microsoft YaHei", 9))
        time_label.pack(side=tk.LEFT)

    def create_notebook(self):
        """创建标签页 - 子类实现"""
        pass

    def create_styled_button(self, parent, text, command, color='primary', width=10):
        """创建样式化按钮"""
        colors = {
            'primary': self.COLORS['primary'],
            'success': self.COLORS['success'],
            'warning': self.COLORS['warning'],
            'accent': self.COLORS['accent'],
        }
        btn_color = colors.get(color, self.COLORS['primary'])

        btn = tk.Button(parent, text=text, command=command,
                       bg=btn_color, fg="white",
                       font=("Microsoft YaHei", 10),
                       relief=tk.FLAT,
                       width=width,
                       padx=10, pady=5,
                       cursor="hand2")
        return btn

    def create_card(self, parent, title):
        """创建卡片式容器"""
        card = tk.Frame(parent, bg=self.COLORS['bg_white'],
                       highlightbackground="#ddd",
                       highlightthickness=1)

        if title:
            title_frame = tk.Frame(card, bg=self.COLORS['bg_light'], height=35)
            title_frame.pack(fill=tk.X)
            title_frame.pack_propagate(False)

            title_label = tk.Label(title_frame, text=title,
                                  bg=self.COLORS['bg_light'],
                                  fg=self.COLORS['text_dark'],
                                  font=("Microsoft YaHei", 11, "bold"))
            title_label.pack(side=tk.LEFT, padx=15, pady=5)

        return card

    def get_role_name(self):
        """获取角色名称"""
        role_names = {
            'system_admin': '系统管理员',
            'leader': '局领导',
            'asset_manager': '资产管理处',
            'office_staff': '办公室',
            'tech_staff': '科技处',
            'finance_staff': '财务处',
            'unit_user': '下属单位',
            'normal_user': '普通用户'
        }
        return role_names.get(self.user['role'], '用户')

    def logout(self):
        """退出登录 - 返回登录界面"""
        if messagebox.askokcancel("退出", "确定要退出登录吗?"):
            from services.auth_service import AuthService
            AuthService.logout(self.user['id'])
            # 关闭当前窗口
            self.root.destroy()
            # 重新启动主程序（返回登录界面）
            import os
            import sys
            # 获取主程序路径
            main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'main.py')
            # 使用当前Python解释器重新运行
            os.execv(sys.executable, [sys.executable, main_path])

    def show(self):
        """显示窗口"""
        self.root.mainloop()

    def set_status(self, message):
        """设置状态栏信息"""
        self.status_label.config(text=message)

    def show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)

    def show_info(self, message):
        """显示提示信息"""
        messagebox.showinfo("提示", message)

    def show_warning(self, message):
        """显示警告信息"""
        messagebox.showwarning("警告", message)
