# user_controller.py
import tkinter as tk
from tkinter import messagebox, ttk
from db import user_model
# from user_model import hash_password


def center_window(win, width=400, height=300):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def load_user_management(root, top_frame):

    for widget in root.winfo_children():
        if widget not in [top_frame]:
            widget.pack_forget()

    mgmt_frame = tk.Frame(root)
    mgmt_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

    tree_frame = tk.Frame(mgmt_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("id", "username", "email", "role", "date_create")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    tree.heading("id", text="ID")
    tree.heading("username", text="Username")
    tree.heading("email", text="Email")
    tree.heading("role", text="Role")
    tree.heading("date_create", text="Create at")

    tree.column("id", width=50, anchor="center")
    tree.column("username", width=150, anchor="w")
    tree.column("email", width=200, anchor="w")
    tree.column("role", width=60, anchor="center")
    tree.column("date_create", width=90, anchor="center")
    tree.pack(fill=tk.BOTH, expand=True)

    def clear_treeview():
        for item in tree.get_children():
            tree.delete(item)

    def refresh_user_list():
        """Hiển thị toàn bộ user trong bảng."""
        clear_treeview()
        rows = user_model.get_all_users()  # GỌI model
        if rows is None:
            messagebox.showerror("Lỗi", "Không thể kết nối database!")
            return
        if not rows:
            messagebox.showinfo("Thông báo", "Chưa có người dùng nào!")
            return

        # row = (user_id, username, password_hash, email, role, is_active, created_at, ...)
        for row in rows:
            user_id = row[0]
            username = row[1]
            email = row[3]
            role = row[4]
            created_at = row[6]
            tree.insert("", tk.END, values=(user_id, username, email, role, created_at))

    def search_user():
        """Tìm user theo username LIKE."""
        typed_username = search_entry.get().strip()
        if not typed_username:
            # Nếu trống thì load lại toàn bộ
            refresh_user_list()
            return

        clear_treeview()
        rows = user_model.search_users_by_username(typed_username)  # GỌI model
        if rows is None:
            messagebox.showerror("Lỗi", "Không thể kết nối database!")
            return
        if not rows:
            messagebox.showinfo("Thông báo", "Không tìm thấy user phù hợp!")
            return

        for row in rows:
            tree.insert("", tk.END, values=(row[0], row[1], row[3], row[4], row[6]))

    def on_tree_click(event):
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
        values = tree.item(item_id, "values")
        user_id, username, email = values[0], values[1], values[2]

        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="Sửa", command=lambda: edit_user_popup(user_id, username, email))
        menu.add_command(label="Xoá", command=lambda: delete_user(user_id))
        menu.post(event.x_root, event.y_root)

    tree.bind("<Button-1>", on_tree_click)

    def add_user_popup():
        popup = tk.Toplevel(root)
        popup.title("Thêm tài khoản")
        center_window(popup, 400, 300)
        popup.grab_set()

        tk.Label(popup, text="Username:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        username_entry = tk.Entry(popup, font=("Arial", 12))
        username_entry.pack(fill="x", padx=10)

        tk.Label(popup, text="Email:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        email_entry = tk.Entry(popup, font=("Arial", 12))
        email_entry.pack(fill="x", padx=10)

        tk.Label(popup, text="Mật khẩu:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        pass_entry = tk.Entry(popup, show="*", font=("Arial", 12))
        pass_entry.pack(fill="x", padx=10)

        def submit_add():
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            password = pass_entry.get().strip()

            if not username or not email or not password:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đủ thông tin!", parent=popup)
                return

            # Gọi model để thêm user
            result = user_model.insert_user(username, email, password, "USER", 1)
            if result is True:
                messagebox.showinfo("Thành công", f"Đã thêm tài khoản cho {username}!", parent=popup)
                popup.destroy()
                refresh_user_list()
            elif result == "EMAIL_EXISTS":
                messagebox.showerror("Lỗi", "Email đã được sử dụng!", parent=popup)
            else:
                messagebox.showerror("Lỗi", "Không thể thêm user (lỗi DB)!", parent=popup)

        tk.Button(popup, text="Thêm mới", font=("Arial", 12),
                  bg="green", fg="white", command=submit_add).pack(pady=10)

    def edit_user_popup(user_id, username, email):
        popup = tk.Toplevel(root)
        popup.title("Sửa tài khoản")
        center_window(popup, 400, 300)
        popup.grab_set()

        tk.Label(popup, text="Username:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        username_entry = tk.Entry(popup, font=("Arial", 12))
        username_entry.insert(0, username)
        username_entry.pack(fill="x", padx=10)

        tk.Label(popup, text="Email:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        email_entry = tk.Entry(popup, font=("Arial", 12))
        email_entry.insert(0, email)
        email_entry.pack(fill="x", padx=10)

        tk.Label(popup, text="Mật khẩu mới (nếu muốn đổi):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        pass_entry = tk.Entry(popup, show="*", font=("Arial", 12))
        pass_entry.pack(fill="x", padx=10)

        def submit_edit():
            new_username = username_entry.get().strip()
            new_email = email_entry.get().strip()
            new_password = pass_entry.get().strip()

            if not new_username or not new_email:
                messagebox.showwarning("Cảnh báo", "Username và Email không được để trống!", parent=popup)
                return

            result = user_model.update_user(
                user_id,
                new_username,
                new_email,
                new_password if new_password else None
            )
            if result is True:
                messagebox.showinfo("Thành công", f"Đã sửa tài khoản #{user_id}!", parent=popup)
                popup.destroy()
                refresh_user_list()
            elif result == "EMAIL_EXISTS":
                messagebox.showerror("Lỗi", "Email này đã được sử dụng!", parent=popup)
            else:
                messagebox.showerror("Lỗi", "Không thể update user!", parent=popup)

        tk.Button(popup, text="Lưu thay đổi", font=("Arial", 12),
                  bg="green", fg="white", command=submit_edit).pack(pady=10)

    def delete_user(user_id):
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa user ID {user_id}?")
        if not confirm:
            return
        result = user_model.delete_user(user_id)
        if result is True:
            messagebox.showinfo("Thành công", f"Đã xóa user ID {user_id}!")
            refresh_user_list()
        else:
            messagebox.showerror("Lỗi", "Không thể xoá user!")

    # Thanh nút dưới
    btn_frame = tk.Frame(mgmt_frame)
    btn_frame.pack(fill="x", pady=10)

    # Ô tìm kiếm
    tk.Label(btn_frame, text="Tìm username:", font=("Arial", 12)).pack(side="left", padx=5)
    search_entry = tk.Entry(btn_frame, font=("Arial", 12), width=15)
    search_entry.pack(side="left", padx=5)

    tk.Button(btn_frame, text="Tìm", font=("Arial", 12), bg="#008CBA", fg="white",
              command=search_user).pack(side="left", padx=5)

    tk.Button(btn_frame, text="Thêm tài khoản", font=("Arial", 12),
              bg="blue", fg="white", command=add_user_popup).pack(side="left", padx=5)

    tk.Button(btn_frame, text="Tải danh sách", font=("Arial", 12),
              bg="orange", fg="white", command=refresh_user_list).pack(side="left", padx=5)

    refresh_user_list()
