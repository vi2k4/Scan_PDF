import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import Menu
import scan
import subprocess
import setting
import user_controller
import edit
import user_data
import tiket
import ticket_repliers
import qlfile  # Import qlfile module
from db import user_model
import statistic
# Lấy user_id từ sys.argv
if len(sys.argv) > 1:
    user_id = sys.argv[1]
else:
    user_id = None

# Debug user_id
print(f"DEBUG: user_id từ sys.argv = {user_id}, type = {type(user_id)}")

# Đặt user_id vào user_data để đồng bộ
user_data.current_user_id = user_id

root = tk.Tk()
root.title("Custom UI")

# Định vị cửa sổ
window_width = 900
window_height = 700
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Top Frame (Menu)
top_frame = tk.Frame(root, height=40, bg="gray")
top_frame.pack(side=tk.TOP, fill=tk.X)

module_text = tk.StringVar()
module_text.set("Trang chủ")

# Label hiển thị tên module
nameModule_lbl = tk.Label(top_frame, textvariable=module_text, font=("Arial", 16), bg="gray", fg="white")
nameModule_lbl.pack(side=tk.LEFT, padx=20, pady=5)

# Menu button nằm bên phải
menu_button = tk.Button(top_frame, text="☰", font=("Arial", 14))
menu_button.pack(side=tk.RIGHT, padx=10, pady=5)

def change_module_name(name):
    module_text.set(name)

def backToLogin():
    root.destroy()
    subprocess.Popen(["python", "src/index.py"])  # Mở file index.py

# Debug vai trò người dùng
print(f"DEBUG: Vai trò người dùng: {user_model.get_role_user_by_id(user_id)}")

# Main Menu
menu = Menu(root, tearoff=0)
menu.add_command(label="Scan", command=lambda: [change_module_name("SCAN"), scan.load_scan(root, top_frame)])
menu.add_command(label="Chỉnh sửa", command=lambda: [change_module_name("CHỈNH SỬA"), edit.load_edit(root, top_frame, "")])
menu.add_command(label="File", command=lambda: [
    change_module_name("FILE"),
    print(f"DEBUG: Gọi qlfile.load_file với user_id = {user_id}"),
    qlfile.load_file(root, top_frame, user_id)
])
menu.add_command(label="Thống kê", command=lambda: [change_module_name("THỐNG KÊ"), statistic.load_statistic(root, top_frame)])
if user_model.get_role_user_by_id(user_id) != "admin":
    menu.add_command(label="Hỗ Trợ", command=lambda: [change_module_name("HỖ TRỢ"), tiket.load_user_support(root, top_frame, user_id)])
if user_model.get_role_user_by_id(user_id) == "admin":
    menu.add_command(label="Quản lý hỗ trợ", command=lambda: [change_module_name("QUẢN LÝ HỖ TRỢ"), ticket_repliers.load_admin_support(root, top_frame)])
    menu.add_command(label="Quản lý tài khoản", command=lambda: [change_module_name("QUẢN LÝ TÀI KHOẢN"), user_controller.load_user_management(root, top_frame)])
menu.add_command(label="Cài đặt", command=lambda: [change_module_name("CÀI ĐẶT"), setting.load_settings(root, top_frame, user_id)])
menu.add_command(label="Đăng xuất", command=lambda: backToLogin())

# Bind menu button
def show_menu(event=None):
    x, y = menu_button.winfo_rootx(), menu_button.winfo_rooty() + menu_button.winfo_height()
    menu.post(x, y)

menu_button.config(command=show_menu)
root.bind("<Button-3>", show_menu)

root.mainloop()