import os
import re
import paramiko
import paramiko.sftp_client
import customtkinter as ctk
from tkinter import messagebox, StringVar, ttk


import os
import sys

def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    path = os.path.join(base_path, relative_path)
    return path





class RemarkBox(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Remarkable 中文字体助手")
        self.geometry("460*300")
        self.resizable(False, False)  # 固定窗口大小

        self.fonts_folder = resource_path("fonts")  # 资源文件夹路径
        self.file_list = os.listdir(self.fonts_folder)

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)

        # 添加空白行以增加间距
        self.grid_rowconfigure(0, minsize=30)

        # File Selection
        self.file_label = ctk.CTkLabel(self, text="字体选择:")
        self.file_label.grid(row=1, column=0, padx=(20, 10), pady=(10, 5), sticky="e")

        self.file_var = StringVar(value=self.file_list[0])
        self.file_dropdown = ctk.CTkOptionMenu(
            self, variable=self.file_var, values=self.file_list, width=240
        )
        self.file_dropdown.grid(
            row=1, column=1, columnspan=2, padx=(10, 20), pady=(10, 5), sticky="w"
        )

        # IP Address
        self.ip_label = ctk.CTkLabel(self, text="IP Address:")
        self.ip_label.grid(row=2, column=0, padx=(20, 10), pady=5, sticky="e")
        self.ip_frame = ctk.CTkFrame(self, width=350)
        self.ip_frame.grid(
            row=2, column=1, columnspan=2, padx=(10, 20), pady=5, sticky="w"
        )

        self.ip_entry = ctk.CTkEntry(self.ip_frame, width=170)
        self.ip_entry.insert(0, "10.11.99.1")  # 默认IP地址
        self.ip_entry.grid(row=0, column=0, pady=5, sticky="w")
        self.ip_entry.bind("<KeyRelease>", self.validate_ip)

        self.ip_hint_label = ctk.CTkLabel(self.ip_frame, text="", text_color="red")
        self.ip_hint_label.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="w")

        # Username
        self.user_label = ctk.CTkLabel(self, text="用户名:")
        self.user_label.grid(row=3, column=0, padx=(20, 10), pady=5, sticky="e")
        self.user_entry = ctk.CTkEntry(self, width=240)
        self.user_entry.insert(0, "root")  # 默认用户名
        self.user_entry.grid(
            row=3, column=1, columnspan=2, padx=(10, 20), pady=5, sticky="w"
        )

        # Password
        self.pass_label = ctk.CTkLabel(self, text="密码:")
        self.pass_label.grid(row=4, column=0, padx=(20, 10), pady=5, sticky="e")
        self.pass_entry = ctk.CTkEntry(self, width=240)
        self.pass_entry.insert(0, "hAmU3XOlRY")
        self.pass_entry.grid(
            row=4, column=1, columnspan=2, padx=(10, 20), pady=5, sticky="w"
        )

        # Upload Button
        self.upload_btn = ctk.CTkButton(
            self, text="上传字体", command=self.upload_file
        )
        self.upload_btn.grid(row=5, column=0, columnspan=3, pady=(20, 5))

        # Progress Bar
        self.progress = ttk.Progressbar(
            self, orient="horizontal", mode="determinate", length=240
        )
        self.progress.grid(row=6, column=0, columnspan=3, padx=50, pady=(5, 20))

    def validate_ip(self, event=None):
        ip = self.ip_entry.get()
        if self.is_valid_ip(ip):
            self.ip_hint_label.configure(text="Valid IP", text_color="green")
        else:
            self.ip_hint_label.configure(text="Invalid IP", text_color="red")

    def is_valid_ip(self, ip):
        pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        if pattern.match(ip):
            return all(0 <= int(num) <= 255 for num in ip.split("."))
        return False

    def upload_file(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        ip = self.ip_entry.get()
        file_name = self.file_var.get()
        local_path = os.path.join(self.fonts_folder, file_name)
        remote_path = f"/usr/share/fonts/opentype/{file_name}"

        if not username or not password or not self.is_valid_ip(ip):
            messagebox.showwarning(
                "参数错误", "请提供正确的用户名密码和IP信息."
            )
            return

        self.progress["value"] = 0
        self.update_idletasks()

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接到远程主机
            ssh.connect(ip, username=username, password=password, timeout=5)
            # 创建SCP客户端
            scp = paramiko.SFTPClient.from_transport(ssh.get_transport())
            # 执行SCP上传
            scp.put(local_path, remote_path, callback=self.update_progress)

            messagebox.showinfo("成功", "字体已经成功上传,请重启你的Remarkable!!!")
            ssh.close()
        except Exception as e:
            messagebox.showerror("错误", f"字体上传失败: {e}")

    def update_progress(self, transferred, total):
        percent = (transferred / total) * 100
        self.progress["value"] = percent
        self.update_idletasks()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # 设置主题风格
    # ctk.set_default_color_theme("blue")  # 设置颜色主题
    app = RemarkBox()
    app.mainloop()
