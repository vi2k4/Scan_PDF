import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import db
from db import tiketController

def center_window(win, width=900, height=600):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def load_user_support(root, top_frame, user_id):
    for widget in root.winfo_children():
        if widget not in [top_frame]:
            widget.pack_forget()

    frame = tk.Frame(root)
    frame.pack(pady=10, padx=20)

    # Gửi yêu cầu hỗ trợ
    tk.Label(frame, text="Gửi yêu cầu hỗ trợ", font=("Arial", 14)).pack()

    # Tiêu đề
    row1 = tk.Frame(frame)
    row1.pack(pady=5, anchor="w")
    tk.Label(row1, text="Tiêu đề:", width=10, anchor="w", font=("Arial", 12)).pack(side="left")
    title_entry = tk.Entry(row1, width=80)
    title_entry.pack(side="left")

    # Nội dung
    row2 = tk.Frame(frame)
    row2.pack(pady=5, anchor="w")
    tk.Label(row2, text="Nội dung:", width=10, anchor="nw", font=("Arial", 12)).pack(side="left")
    content_entry = tk.Text(row2, width=80, height=6)
    content_entry.pack(side="left")

    status_lbl = tk.Label(frame, text="", fg="green")
    status_lbl.pack(pady=(5, 10))
    

    def send_request():
        title = title_entry.get().strip()
        message = content_entry.get("1.0", tk.END).strip()
        if not title or not message:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tiêu đề và nội dung.")
            return
        tiketController.create_tiket(user_id,title,message)
        title_entry.delete(0, tk.END)
        content_entry.delete("1.0", tk.END)
        status_lbl.config(text="✅ Đã gửi yêu cầu!")
        load_requests()

    tk.Button(frame, text="Gửi yêu cầu", font=("Arial", 12), command=send_request).pack()

    # Danh sách phản hồi
    tk.Label(frame, text="Danh sách yêu cầu đã gửi", font=("Arial", 14)).pack(pady=(20, 5))

    columns = ("id", "title", "status")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
    tree.heading("id", text="ID")
    tree.heading("title", text="Tiêu đề")
    tree.heading("status", text="Trạng thái")
    tree.column("id", width=50)
    tree.column("title", width=400)
    tree.column("status", width=150)
    # Scrollbar dọc
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")

    # Kết nối scrollbar với treeview
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack()

    requests = []

    def load_requests():
        nonlocal requests
        for row in tree.get_children():
            tree.delete(row)
        
        requests = tiketController.fetch_data_tiket_replies(user_id)
        for req in requests:
            tree.insert("", tk.END, values=(req[0], req[2], req[4]))

    def show_detail(event):
        selected = tree.selection()
        if not selected:
            return
        index = tree.index(selected[0])
        req = requests[index]
        

        popup = tk.Toplevel(root)
        popup.title("Chi tiết phản hồi")
        center_window(popup, 600, 400)

        tk.Label(popup, text=f"Tiêu đề: {req[2]}", font=("Arial", 12, "bold"), wraplength=580).pack(anchor="w", padx=10, pady=(10, 5))
        tk.Label(popup, text=f"Nội dung: {req[3]}", wraplength=580).pack(anchor="w", padx=10, pady=(0, 10))
        tk.Label(popup, text="Phản hồi từ Admin:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        tk.Label(popup, text=tiketController.ticket_reply(req[0]) or "Chưa có phản hồi", fg="blue", wraplength=580).pack(anchor="w", padx=10, pady=(0, 10))
        tk.Button(popup, text="Thoát", command=popup.destroy).pack(pady=10)

    tree.bind("<<TreeviewSelect>>", show_detail)

    load_requests()
 