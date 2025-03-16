import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

<<<<<<< HEAD
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
=======
# Thêm thư mục gốc (PYTHON) vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.connect import create_connection  # Import từ file connect.py
>>>>>>> 03a7e3b43494ab16ca94f6504a58aa1603b81b81

# Căn giữa cửa sổ
def center_window(win, width=400, height=300):
    win.update_idletasks()
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

# Lấy thông tin tài khoản
def get_user_info(user_id):
    print(f"DEBUG: Đang lấy thông tin user với user_id = {user_id}")
    conn = create_connection()
    
    if not conn:
        print("LỖI: Không thể kết nối database!")
        return None

    try:
        cursor = conn.cursor()
        sql = "SELECT username, email, role, is_active, created_at FROM users WHERE user_id = %s"
        print(f"DEBUG: Thực thi SQL: {sql} với user_id = {user_id}")
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        print(f"DEBUG: Kết quả truy vấn: {result}")
        return result
    except Exception as e:
        print(f"LỖI DATABASE: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
        print("Đã đóng kết nối.")

# Hiển thị thông tin tài khoản
def show_user_info(root, user_id, top_frame):
    if user_id is None:
        print("LỖI: user_id bị None, không thể lấy thông tin!")
        return

    user_id = str(user_id)  # Đảm bảo user_id luôn là chuỗi
    print(f"DEBUG: Đang hiển thị thông tin user với user_id = {user_id}")

    for widget in root.winfo_children():
        if widget not in top_frame.winfo_children():
            widget.pack_forget()

    user_info = get_user_info(user_id)
    if not user_info:
        print("LỖI: Không lấy được thông tin user!")
        return

    print(f"DEBUG: Dữ liệu user nhận được: {user_info}")

    # Tạo giao diện hiển thị thông tin user
    info_frame = tk.Frame(root, padx=20, pady=20)
    info_frame.pack(expand=True)

    tk.Label(info_frame, text="Thông Tin Tài Khoản", font=("Arial", 20, "bold")).pack(pady=(0, 10))
    tk.Label(info_frame, text=f"👤 Username: {user_info[0]}", font=("Arial", 14)).pack(pady=5, anchor="w")
    tk.Label(info_frame, text=f"📧 Email: {user_info[1]}", font=("Arial", 14)).pack(pady=5, anchor="w")
    tk.Label(info_frame, text=f"🔑 Role: {user_info[2]}", font=("Arial", 14)).pack(pady=5, anchor="w")
    tk.Label(info_frame, text=f"✅ Trạng thái: {'Active' if user_info[3] else 'Inactive'}", font=("Arial", 14)).pack(pady=5, anchor="w")
    tk.Label(info_frame, text=f"📅 Ngày tạo: {user_info[4]}", font=("Arial", 14)).pack(pady=5, anchor="w")

    tk.Button(info_frame, text="🔙 Quay lại", font=("Arial", 14), command=lambda: load_settings(root, top_frame, user_id)).pack(pady=15)

    print("DEBUG: Giao diện thông tin tài khoản đã được tạo thành công!")

# Đổi mật khẩu
def change_password(root, user_id):
    def submit():
        old_pass = entry_old.get().strip()
        new_pass = entry_new.get().strip()
        confirm_pass = entry_confirm.get().strip()

        if not all([old_pass, new_pass, confirm_pass]):
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=popup)
            return
        
        if new_pass != confirm_pass:
            messagebox.showerror("Lỗi", "Mật khẩu mới không khớp!", parent=popup)
            return
        
        conn = create_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("Lỗi", "Tài khoản không tồn tại!", parent=popup)
                return
            
            if old_pass != result[0]:
                messagebox.showerror("Lỗi", "Mật khẩu cũ không đúng!", parent=popup)
                return
            
            cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_pass, user_id))
            conn.commit()
            
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=popup)
            popup.destroy()
        except Exception as e:
            print(f"Lỗi database: {e}")
        finally:
            cursor.close()
            conn.close()
            print("Đã đóng kết nối.")
    
    popup = tk.Toplevel(root)
    popup.title("Đổi mật khẩu")
    center_window(popup)
    
    tk.Label(popup, text="Mật khẩu cũ:").pack()
    entry_old = tk.Entry(popup, show="*")
    entry_old.pack()
    
    tk.Label(popup, text="Mật khẩu mới:").pack()
    entry_new = tk.Entry(popup, show="*")
    entry_new.pack()
    
    tk.Label(popup, text="Xác nhận mật khẩu mới:").pack()
    entry_confirm = tk.Entry(popup, show="*")
    entry_confirm.pack()
    
    tk.Button(popup, text="Xác nhận", command=submit).pack()

# Giao diện cài đặt
def load_settings(root, top_frame, user_id):
    print(f"DEBUG: Tải giao diện Cài đặt cho user_id = {user_id}")

    if not top_frame:
        print("LỖI: top_frame = None, không thể hiển thị cài đặt")
        return

    for widget in root.winfo_children():
        if widget is not top_frame:
            widget.pack_forget()

    setting_frame = tk.Frame(root, padx=20, pady=20)
    setting_frame.pack(fill=tk.BOTH, expand=True)

    def add_section(title, options):
        tk.Label(setting_frame, text=title, font=("Arial", 18, "bold")).pack(anchor="w", pady=(10, 5))
        for text, command in options:
            tk.Button(setting_frame, text=text, font=("Arial", 14), fg="black", bd=1, command=command).pack(anchor="w", pady=5)

    add_section("Tài khoản", [
        ("Thông tin tài khoản", lambda: show_user_info(root, user_id, top_frame)),
        ("Đổi mật khẩu", lambda: change_password(root, user_id)),
    ])

# Biểu tượng camera
    try:
        img_path = os.path.abspath("img/Camera.png")
        img = Image.open(img_path).resize((100, 100))
    except FileNotFoundError:
        img = Image.new("RGB", (100, 100), (200, 200, 200))  

    icon = ImageTk.PhotoImage(img)
    btn_icon = tk.Button(root, image=icon, bd=0)
    btn_icon.image = icon
    btn_icon.place(relx=0.98, rely=0.95, anchor="se")

if __name__ == "__main__":
    user_id = 11
    root = tk.Tk()
    root.title("Cài đặt")
    root.geometry("900x700")

    top_frame = tk.Frame(root, height=40, bg="gray")
    top_frame.pack(side=tk.TOP, fill=tk.X)

    load_settings(root, top_frame, user_id)
    root.mainloop()
