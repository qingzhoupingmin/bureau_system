# -*- coding: utf-8 -*-
"""
数据库初始化工具 - 双击运行
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class InitTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("数据库初始化工具")
        self.root.geometry("600x400")

        # 标题
        tk.Label(self.root, text="天津市市政工程局综合管理系统", font=("Microsoft YaHei", 14, "bold")).pack(pady=10)
        tk.Label(self.root, text="数据库初始化工具", font=("Microsoft YaHei", 12)).pack(pady=5)

        # 说明
        info_text = """请确保：
1. MySQL服务已启动
2. config.py中的数据库密码正确 (当前: Oppor831t)"""
        tk.Label(self.root, text=info_text, fg="blue").pack(pady=10)

        # 日志输出区域
        self.log_area = scrolledtext.ScrolledText(self.root, height=15, width=70)
        self.log_area.pack(padx=10, pady=10)

        # 按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="开始初始化", command=self.start_init, bg="#1a5fb4", fg="white",
                 font=("Microsoft YaHei", 11), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="退出", command=self.root.quit, font=("Microsoft YaHei", 11),
                 width=10).pack(side=tk.LEFT, padx=5)

    def log(self, msg):
        """输出日志"""
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.root.update()

    def start_init(self):
        """开始初始化"""
        threading.Thread(target=self.run_init, daemon=True).start()

    def run_init(self):
        """执行初始化"""
        try:
            self.log("="*50)
            self.log("开始初始化数据库...")
            self.log("")

            # 测试连接
            self.log("1. 测试数据库连接...")
            from config import DB_CONFIG
            import pymysql

            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                charset=DB_CONFIG['charset']
            )
            self.log(f"   连接成功! 数据库: {DB_CONFIG['database']}")
            conn.close()

            # 执行初始化
            self.log("")
            self.log("2. 执行初始化...")
            from db.init_db import init_all
            init_all()

            self.log("")
            self.log("="*50)
            self.log("初始化完成!")
            self.log("")
            self.log("默认账号:")
            self.log("  系统管理员: admin / admin123")
            self.log("  局领导: secretary / leader123")
            self.log("  办公室: office_1 / office123")
            self.log("  财务处: finance_1 / finance123")
            self.log("  资产管理处: asset_1 / asset123")

            messagebox.showinfo("成功", "数据库初始化完成！")

        except Exception as e:
            self.log(f"错误: {str(e)}")
            messagebox.showerror("错误", f"初始化失败:\n{str(e)}")

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = InitTool()
    app.run()
