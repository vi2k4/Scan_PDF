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
    
def load_admin_support(root, top_frame):
    for widget in root.winfo_children():
        if widget not in [top_frame]:
            widget.pack_forget()

    frame = tk.Frame(root)
    frame.pack(pady=10, padx=20)

    tk.Label(frame, text="Quản lý yêu cầu hỗ trợ", font=("Arial", 16, "bold")).pack(pady=10)

    columns = ("id", "user_id", "title", "status")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    tree.heading("id", text="ID")
    tree.heading("user_id", text="User ID")
    tree.heading("title", text="Tiêu đề")
    tree.heading("status", text="Trạng thái")

    tree.column("id", width=50)
    tree.column("user_id", width=80)
    tree.column("title", width=600)
    tree.column("status", width=150)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")

    # Kết nối scrollbar với treeview
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(pady=5)

    requests = []

    def load_requests():
        nonlocal requests
        for row in tree.get_children():
            tree.delete(row)
        
        requests = tiketController.fetch_data_tiket()
        for req in requests:
            tree.insert("", tk.END, values=(req[0], req[1], req[2], req[4]))  # id, user_id, title, status
    def delete_ticket(ticket_id):
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa ticket: {ticket_id}?")
        if not confirm:
            return
        result = tiketController.delete_ticket(ticket_id)
        if result is True:
            messagebox.showinfo("Thành công", f"Đã xóa ticket {ticket_id}!")
            load_requests()
        else:
            messagebox.showerror("Lỗi", "Không thể xoá ticket!")
        

    def show_reply_popup(event):
        selected = tree.selection()
        if not selected:
            return
        index = tree.index(selected[0])
        req = requests[index]

        popup = tk.Toplevel(root)
        popup.title("Phản hồi yêu cầu")
        center_window(popup, 600, 500)

        tk.Label(popup, text=f"Tiêu đề: {req[2]}", font=("Arial", 12, "bold"), wraplength=580).pack(anchor="w", padx=10, pady=(10, 5))
        tk.Label(popup, text=f"Nội dung: {req[3]}", wraplength=580).pack(anchor="w", padx=10, pady=(0, 10))

        tk.Label(popup, text="Phản hồi:", font=("Arial", 12)).pack(anchor="w", padx=10)
        reply_text = tk.Text(popup, width=70, height=6)
        reply = tiketController.ticket_reply(req[0])
        if isinstance(reply, list):
            reply = reply[0] if reply else ""
        reply_text.insert(tk.END, reply)
        reply_text.pack(padx=10, pady=(0, 10))
        

        def send_reply():
            response = reply_text.get("1.0", tk.END).strip()
            if not response:
                messagebox.showwarning("Thiếu nội dung", "Vui lòng nhập nội dung phản hồi.")
                return
            if (req[4] == "Đã phản hồi"):
                success = tiketController.update_ticket_reply(req[0],req[1] ,response)
            else:
                success = tiketController.create_tiket_replies(req[0],req[1] ,response)
            if success:
                messagebox.showinfo("Thành công", "Đã gửi phản hồi.")
                popup.destroy()
                load_requests()
            else:
                messagebox.showerror("Lỗi", "Không thể gửi phản hồi.")

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Gửi phản hồi", command=send_reply).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Xóa ticket này",  command=lambda: delete_ticket(req[0])).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Thoát", command=popup.destroy).pack(side="left", padx=10)

    tree.bind("<<TreeviewSelect>>", show_reply_popup)

    load_requests()
