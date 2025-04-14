import hashlib
import tkinter as tk
from tkinter import messagebox
from mysql.connector import Error


import mysql
from PIL import Image, ImageTk
import os
import sys
from cryptography.fernet import Fernet
from tkinter import messagebox
import scan


if len(sys.argv) > 1:
    user_id = int (sys.argv[1])
else:
    user_id = None

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
# Thêm thư mục gốc (PYTHON) vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.connect import create_connection  # Import từ file connect.py

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

def show_user_info(root, user_id):
    if user_id is None:
        print("LỖI: user_id bị None, không thể lấy thông tin!")
        return

    user_id = str(user_id)  # Đảm bảo user_id luôn là chuỗi
    print(f"DEBUG: Đang hiển thị thông tin user với user_id = {user_id}")

    user_info = get_user_info(user_id)
    if not user_info:
        print("LỖI: Không lấy được thông tin user!")
        return

    print(f"DEBUG: Dữ liệu user nhận được: {user_info}")

    # Tạo cửa sổ mới (Toplevel)
    info_window = tk.Toplevel(root)
    info_window.title("Thông Tin Tài Khoản")
    info_window.configure(bg="white")

    # Căn giữa cửa sổ
    window_width = 400
    window_height = 300
    screen_width = info_window.winfo_screenwidth()
    screen_height = info_window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    info_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Tiêu đề
    tk.Label(info_window, text="Thông Tin Tài Khoản", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    # Các thông tin tài khoản
    details = [
        (f"👤 Username: {user_info[0]}", "black"),
        (f"📧 Email: {user_info[1]}", "black"),
        (f"🔑 Role: {user_info[2]}", "black"),
        (f"✅ Trạng thái: {'Active' if user_info[3] else 'Inactive'}", "green" if user_info[3] else "red"),
        (f"📅 Ngày tạo: {user_info[4]}", "black"),
    ]

    for text, color in details:
        tk.Label(info_window, text=text, font=("Arial", 12), fg=color, bg="white", anchor="w").pack(pady=5, fill="x")

    # Nút đóng cửa sổ
    btn_close = tk.Button(info_window, text="Đóng", font=("Arial", 12, "bold"), bg="gray", fg="white",
                          padx=10, pady=5, command=info_window.destroy)
    btn_close.pack(pady=15)

    print("DEBUG: Giao diện thông tin tài khoản đã được tạo thành công!")



# Hàm mã hóa/giải mã mật khẩu
key = b"ljlJeB1u3Yyh8tYYYAObAevf5-nbv5qZz0_sPihFll8="

def encrypt_password(password: str) -> str:
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()

def decrypt_password(encrypted_password: str) -> str:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()

# Hàm đổi mật khẩu có mã hóa
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

            # Giải mã mật khẩu đã lưu và so sánh
            try:
                saved_password = decrypt_password(result[0])
            except Exception:
                messagebox.showerror("Lỗi", "Lỗi giải mã mật khẩu cũ!", parent=popup)
                return

            if old_pass != saved_password:
                messagebox.showerror("Lỗi", "Mật khẩu cũ không đúng!", parent=popup)
                return
            
            encrypted_new = encrypt_password(new_pass)
            cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (encrypted_new, user_id))
            conn.commit()
            
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=popup)
            popup.destroy()
        except Exception as e:
            print(f"Lỗi database: {e}")
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi cập nhật mật khẩu!", parent=popup)
        finally:
            cursor.close()
            conn.close()
            print("Đã đóng kết nối.")

    popup = tk.Toplevel(root)
    popup.title("Đổi mật khẩu")
    center_window(popup, 600, 350)
    popup.configure(bg="white")

    frame = tk.Frame(popup, padx=20, pady=20, bg="white")
    frame.pack(expand=True)

    tk.Label(frame, text="🔑 Đổi mật khẩu", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    tk.Label(frame, text="Mật khẩu cũ:", font=("Arial", 14), bg="white").pack(anchor="w")
    entry_old = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
    entry_old.pack(pady=5)

    tk.Label(frame, text="Mật khẩu mới:", font=("Arial", 14), bg="white").pack(anchor="w")
    entry_new = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
    entry_new.pack(pady=5)

    tk.Label(frame, text="Xác nhận mật khẩu mới:", font=("Arial", 14), bg="white").pack(anchor="w")
    entry_confirm = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
    entry_confirm.pack(pady=5)

    btn_submit = tk.Button(frame, text="Xác nhận", font=("Arial", 14, "bold"), bg="blue", fg="white", width=15, command=submit)
    btn_submit.pack(pady=10)


# Hàm xóa tài khoản
def delete_account(root, user_id):
    def confirm_delete():
        conn = create_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("Lỗi", "Tài khoản không tồn tại!", parent=popup)
                return

            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            messagebox.showinfo("Thành công", "Tài khoản đã bị xóa!", parent=popup)
            root.attributes("-disabled", False)  # Khôi phục quyền điều khiển cửa sổ chính
            popup.destroy()  # Đóng cửa sổ xác nhận xóa tài khoản
        except Exception as e:
            print(f"Lỗi database: {e}")
        finally:
            cursor.close()
            conn.close()

    # Tạo cửa sổ popup để xác nhận xóa tài khoản
    popup = tk.Toplevel(root)
    popup.title("Xóa tài khoản")
    center_window(popup, 600, 250)
    popup.configure(bg="white")

    frame = tk.Frame(popup, padx=20, pady=20, bg="white")
    frame.pack(expand=True)

    tk.Label(frame, text="⚠️ Xác nhận xóa tài khoản", font=("Arial", 18, "bold"), fg="red", bg="white").pack(pady=10)
    tk.Label(frame, text="Bạn có chắc chắn muốn xóa tài khoản này không?", font=("Arial", 14), bg="white").pack(pady=10)

    btn_frame = tk.Frame(frame, bg="white")
    btn_frame.pack(pady=10)

    # Nút hủy, không đóng cửa sổ chính
    btn_cancel = tk.Button(btn_frame, text="Hủy", font=("Arial", 14, "bold"), bg="gray", fg="white", width=10,
                           command=lambda: popup.destroy())  # Chỉ đóng cửa sổ con popup
    btn_cancel.pack(side="left", padx=10)

    # Nút xóa tài khoản
    btn_delete = tk.Button(btn_frame, text="Xóa", font=("Arial", 14, "bold"), bg="red", fg="white", width=10, command=confirm_delete)
    btn_delete.pack(side="left", padx=10)

    # Vô hiệu hóa cửa sổ chính để ngừng tương tác khi popup mở
    # root.attributes("-disabled", True)

    # Sự kiện đóng cửa sổ con (popup) khi người dùng nhấn nút "X"
    # popup.protocol("WM_DELETE_WINDOW", lambda: root.attributes("-disabled", False) or popup.destroy())

# Giao diện cài đặt
# Thêm nút xóa vào giao diện cài đặt
def load_settings(root, top_frame, user_id):
    print(f"DEBUG: Tải giao diện Cài đặt cho user_id = {user_id}")

    if not top_frame:
        print("LỖI: top_frame = None, không thể hiển thị cài đặt")
        return

    for widget in root.winfo_children():
        if widget not in [top_frame]:  # Giữ lại top_frame
            widget.pack_forget()  # Chỉ ẩn thay vì xóa

    setting_frame = tk.Frame(root, padx=20, pady=20)
    setting_frame.pack(fill=tk.BOTH, expand=True)

    def add_section(title, options):
        tk.Label(setting_frame, text=title, font=("Arial", 25, "bold")).pack(anchor="w", pady=(15, 5))
        for text, command in options:
            tk.Button(setting_frame, text=text, font=("Arial", 17), fg="gray", bd=0, command=command).pack(anchor="w")

    add_section("Tài khoản", [
        ("Thông tin tài khoản", lambda: show_user_info(root, user_id)),
        ("Đổi mật khẩu", lambda: change_password(root, user_id)),
        ("Xóa tài khoản", lambda: delete_account(root, user_id)),  # Nút xóa tài khoản
    ])
    add_section("Giới thiệu", [
        ("chính sách", None),
        ("Giấy phép",None),
        ("...", None), 
    ])
    add_section("Trung tâm trợ giúp", [
        ("Hỗ trợ", None),
        ("Địa chỉ: trụ sở SGU",None),
        ("Hotline: sđtxxx", None),  
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
    btn_icon.bind("<Button-1>", lambda event: scan.load_scan(root, top_frame))

if __name__ == "__main__":
    user_id = 12
    root = tk.Tk()
    root.title("Cài đặt")
    root.geometry("900x700")

    top_frame = tk.Frame(root, height=40, bg="gray")
    top_frame.pack(side=tk.TOP, fill=tk.X)

    load_settings(root, top_frame, user_id)
    root.mainloop()
