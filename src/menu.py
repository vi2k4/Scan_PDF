import sys
import tkinter as tk
from tkinter import Menu
import scan 
import subprocess
import setting
import user_controller
import edit
import user_data

if len(sys.argv) > 1:
    user_id = sys.argv[1]
else:
    user_id = None
# print(user_data.get_current_user())
#
# print("Menu này : ")
# print(user_data.current_user_id)
# print(f"user_id từ menu: {user_data.current_user_id}")
# print(f"DEBUG: user_data.current_user_id = {user_data.current_user_id}, type = {type(user_data.current_user_id)}")
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
    subprocess.Popen(["python", "src/index.py"])  # Mở file scan.py

    # subprocess.Popen(["python", "src/index.py"])  # Mở file scan.py
   

# Main Menu
menu = Menu(root, tearoff=0)
menu.add_command(label="Scan", command=lambda: [change_module_name("SCAN"), scan.load_scan(root, top_frame)])
menu.add_command(label="Chỉnh sửa", command=lambda: [change_module_name("CHỈNH SỬA"), edit.load_edit(root, top_frame)])
menu.add_command(label="Ảnh gần đây", command=lambda: change_module_name("ẢNH GẦN ĐÂY"))
menu.add_command(label="File", command=lambda: change_module_name("FILE"))
if(user_id == "1"):
    menu.add_command(label="Quản lý tài khoản", command=lambda: [change_module_name("QUẢN LÝ TÀI KHOẢN"), user_controller.load_user_management(root, top_frame)])
# menu.add_command(label="Cài đặt", command=lambda: [change_module_name("CÀI ĐẶT"), setting.load_settings(root, top_frame)])
menu.add_command(label="Cài đặt", command=lambda: [change_module_name("CÀI ĐẶT"), setting.load_settings(root, top_frame, user_id)])
menu.add_command(label="Đăng xuất" , command=lambda: backToLogin())

# Bind menu button
def show_menu(event=None):
    x, y = menu_button.winfo_rootx(), menu_button.winfo_rooty() + menu_button.winfo_height()
    menu.post(x, y)

menu_button.config(command=show_menu)
root.bind("<Button-3>", show_menu)

root.mainloop()
