import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import hashlib
import mysql.connector
from mysql.connector import Error

# Kết nối MySQL
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",  # Thay bằng user của bạn
            password="",  # Thay bằng password của bạn
            database="my_scanner_db"
        )
    except Error as e:
        print(f"Lỗi kết nối MySQL: {e}")
        return None

# Hàm băm mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Căn giữa cửa sổ
def center_window(win, width=400, height=300):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

# Đổi mật khẩu
def change_password(root, email):
    if not email or not isinstance(email, str):
        messagebox.showerror("Lỗi", "Email không hợp lệ!", parent=root)
        return

    def submit():
        old_pass = entry_old.get()
        new_pass = entry_new.get()
        confirm_pass = entry_confirm.get()

        if not old_pass or not new_pass or not confirm_pass:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=popup)
            return

        if new_pass != confirm_pass:
            messagebox.showerror("Lỗi", "Mật khẩu mới không khớp!", parent=popup)
            return  

        conn = connect_db()
        if not conn:
            messagebox.showerror("Lỗi", "Không thể kết nối database!", parent=popup)
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            if not result or result[0] != hash_password(old_pass):
                messagebox.showerror("Lỗi", "Mật khẩu cũ không đúng!", parent=popup)
                return

            cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hash_password(new_pass), email))
            conn.commit()
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=popup)
            popup.destroy()
            root.attributes("-disabled", False)
        except Error as e:
            messagebox.showerror("Lỗi", f"Lỗi database: {e}", parent=popup)
        finally:
            cursor.close()
            conn.close()

    root.attributes("-disabled", True)
    popup = tk.Toplevel(root)
    popup.title("Đổi mật khẩu")
    center_window(popup)
    popup.protocol("WM_DELETE_WINDOW", lambda: [popup.destroy(), root.attributes("-disabled", False)])

    tk.Label(popup, text="Mật khẩu cũ:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
    entry_old = tk.Entry(popup, show="*", font=("Arial", 14))
    entry_old.pack(fill="x", padx=10)

    tk.Label(popup, text="Mật khẩu mới:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
    entry_new = tk.Entry(popup, show="*", font=("Arial", 14))
    entry_new.pack(fill="x", padx=10)

    tk.Label(popup, text="Xác nhận mật khẩu mới:", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
    entry_confirm = tk.Entry(popup, show="*", font=("Arial", 14))
    entry_confirm.pack(fill="x", padx=10)

    tk.Button(popup, text="Xác nhận", command=submit, font=("Arial", 14), bg="green", fg="white").pack(pady=10)

# Xóa tài khoản
def delete_account(root):
    root.attributes("-disabled", True)
    popup = tk.Toplevel(root)
    popup.title("Xóa tài khoản")
    center_window(popup, 350, 200)
    popup.protocol("WM_DELETE_WINDOW", lambda: [popup.destroy(), root.attributes("-disabled", False)])

    tk.Label(popup, text="Bạn có chắc muốn xóa tài khoản?", font=("Arial", 14)).pack(pady=20)
    
    btn_frame = tk.Frame(popup)
    btn_frame.pack()

    tk.Button(btn_frame, text="Hủy", command=lambda: [popup.destroy(), root.attributes("-disabled", False)], font=("Arial", 14), bg="gray", fg="white").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Xóa", command=lambda: [messagebox.showinfo("Thông báo", "Tài khoản đã bị xóa!"), popup.destroy(), root.attributes("-disabled", False)], font=("Arial", 14), bg="red", fg="white").pack(side="left", padx=10)

# Giao diện cài đặt
def load_settings(root, email="default_email@example.com"):
    for widget in root.winfo_children():
        widget.destroy()

    setting_frame = tk.Frame(root)
    setting_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

    def add_section(title, options):
        tk.Label(setting_frame, text=title, font=("Arial", 28, "bold")).pack(anchor="w", pady=(15, 5))
        for text, command in options:
            tk.Button(setting_frame, text=text, font=("Arial", 20), fg="gray", bd=0, command=command).pack(anchor="w")

    add_section("Tài khoản", [
        ("Đổi mật khẩu", lambda: change_password(root, email)),
        ("Xóa tài khoản", lambda: delete_account(root))
    ])

    # Biểu tượng camera
    try:
        img_path = os.path.abspath("img/Camera.png")
        img = Image.open(img_path).resize((100, 100))
    except FileNotFoundError:
        img = Image.new("RGB", (100, 100), (200, 200, 200))  # Ảnh nền xám

    icon = ImageTk.PhotoImage(img)
    btn_icon = tk.Button(root, image=icon, bd=0)
    btn_icon.image = icon
    btn_icon.place(relx=0.98, rely=0.95, anchor="se")

# Chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Cài đặt")
    root.geometry("900x700")
    load_settings(root, email="admin@example.com")
    root.mainloop()
