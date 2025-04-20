import os
import shutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import webbrowser
import mysql.connector
import sys
import user_data

# ---------- THIẾT LẬP THÔNG SỐ ĐĂNG NHẬP ----------
if len(sys.argv) > 1:
    user_id = int(sys.argv[1])
else:
    user_id = None

# ---------- KẾT NỐI DATABASE ----------
def get_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="my_scanner_db"
        )
        print("DEBUG: Kết nối cơ sở dữ liệu thành công")
        return db
    except Exception as e:
        print(f"ERROR: Không thể kết nối cơ sở dữ liệu: {e}")
        messagebox.showerror("Lỗi kết nối", f"Không thể kết nối cơ sở dữ liệu: {e}")
        return None

def load_file(root, top_frame, user_id):
    print(f"DEBUG: Tải giao diện Quản lý file cho user_id = {user_data.get_current_user()}")

    if not top_frame:
        print("LỖI: top_frame = None, không thể hiển thị giao diện file")
        return

    for widget in root.winfo_children():
        if widget not in [top_frame]:  # Giữ lại top_frame
            widget.pack_forget()       # Ẩn thay vì xóa để dễ hiển thị lại

    file_manager = FileManager(root)  # Chỉ truyền root vào
    file_manager.load_files()



class FileManager:
    def __init__(self, root):
        self.root = root
        self.current_mode = "pdf"
        self.selected_file_id = None
        self.selected_widgets = {}
        self.build_ui()  # Gọi phương thức build_ui() để tạo giao diện
        self.update_header_style()

    def build_ui(self):
        self.header = tk.Frame(self.root, bg="#f5f5f5", height=60)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)

        self.lbl_file = tk.Label(self.header, text="File", font=("Arial", 20, "bold"),
                                 bg="#f5f5f5", cursor="hand2")
        self.lbl_file.pack(side=tk.LEFT, padx=(20, 10))
        self.lbl_file.bind("<Button-1>", lambda e: self.switch_mode("pdf"))

        tk.Frame(self.header, bg="#ccc", width=2, height=30).pack(side=tk.LEFT, pady=15)

        self.lbl_pin = tk.Label(self.header, text="Ghim", font=("Arial", 20, "bold"),
                                bg="#f5f5f5", cursor="hand2")
        self.lbl_pin.pack(side=tk.LEFT, padx=(10, 40))
        self.lbl_pin.bind("<Button-1>", lambda e: self.switch_mode("pdf_ghim"))

        self.underline = tk.Frame(self.header, bg="#00BFFF", height=3, width=100)
        self.underline.place(x=0, rely=1.0, anchor='sw')

        self.delete_btn = tk.Button(self.header, text="Xóa", font=("Arial", 12, "bold"),
                                    bg="red", fg="white", command=self.delete_file)
        self.delete_btn.pack(side=tk.RIGHT, padx=10)

        self.delete_all_btn = tk.Button(self.header, text="Xóa tất cả", font=("Arial", 12, "bold"),
                                        bg="red", fg="white", command=self.delete_all_files)
        self.delete_all_btn.pack(side=tk.RIGHT)

        # Tạo frame file mới tại đây thay vì truyền từ ngoài
        file_frame = tk.Frame(self.root, padx=20, pady=20)
        file_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(file_frame, bg="white")
        scrollbar = tk.Scrollbar(file_frame, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


    def switch_mode(self, mode):
        if self.current_mode != mode:
            self.current_mode = mode
            self.update_header_style()
            self.load_files()

    def update_header_style(self):
        target = self.lbl_file if self.current_mode == "pdf" else self.lbl_pin
        self.root.after(10, lambda: self.underline.place_configure(
            x=target.winfo_x(), width=target.winfo_width()))

    def load_files(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor(dictionary=True)

            query = """
                SELECT * FROM documents
                WHERE user_id = %s AND status = %s
                ORDER BY created_at DESC
            """
            mode_status = "pinned" if self.current_mode == "pdf_ghim" else "normal"
            cursor.execute(query, (user_data.get_current_user(), mode_status))
            rows = cursor.fetchall()

            print(f"DEBUG: Dữ liệu tải về: {rows}")  # In ra dữ liệu để kiểm tra

            if not rows:
                print("DEBUG: Không có dữ liệu nào được tải về.")
                messagebox.showinfo("Thông báo", "Không có dữ liệu để hiển thị.")

            grouped = {}
            for row in rows:
                date_key = row["created_at"].strftime("%m/%Y")
                grouped.setdefault(date_key, []).append(row)

            for month_year, items in grouped.items():
                section = tk.Label(self.scrollable_frame, text=month_year, font=("Arial", 14, "bold"), bg="white")
                section.pack(anchor='w', padx=15, pady=(10, 0))
                for row in items:
                    self.create_file_entry(row)

            cursor.close()
            db.close()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
            print(f"ERROR: Không thể tải dữ liệu: {e}")

    def create_file_entry(self, doc):
        bg_normal = "#4CE5F2"
        bg_selected = "#4CC2F1"

        frame = tk.Frame(self.scrollable_frame, bg=bg_normal, height=60, width=850, bd=1, relief="solid")
        frame.pack(fill=tk.X, padx=20, pady=5)
        frame.pack_propagate(False)

        icon_frame = tk.Frame(frame, bg=bg_normal, width=50)
        icon_frame.pack(side=tk.LEFT, padx=10)

        try:
            icon_img = Image.open("img/pdf.png").resize((40, 40))
            pdf_icon = ImageTk.PhotoImage(icon_img)
        except:
            pdf_icon = None

        icon_lbl = tk.Label(icon_frame, image=pdf_icon if pdf_icon else None,
                            text="PDF" if not pdf_icon else "", bg=bg_normal)
        if pdf_icon: icon_lbl.image = pdf_icon
        icon_lbl.pack()

        content_frame = tk.Frame(frame, bg=bg_normal)
        content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        lbl_name = tk.Label(content_frame, text=doc["title"], font=("Arial", 18, "bold"),
                            bg=bg_normal, anchor="w", cursor="hand2")
        lbl_name.pack(side=tk.LEFT, fill=tk.X, expand=True)

        lbl_date = tk.Label(content_frame, text=doc["created_at"].strftime("%d/%m/%Y"),
                            font=("Arial", 14), bg=bg_normal, anchor="w", width=15)
        lbl_date.pack(side=tk.RIGHT)

        action_frame = tk.Frame(frame, bg=bg_normal)
        action_frame.pack(side=tk.RIGHT, padx=10)

        if self.current_mode == "pdf":
            pin_btn = tk.Label(action_frame, text="☆", font=("Arial", 25), bg=bg_normal, cursor="hand2")
            pin_btn.pack(side=tk.LEFT)
            pin_btn.bind("<Button-1>", lambda e: self.update_pin_status(doc["doc_id"], "pinned"))
        else:
            unpin_btn = tk.Label(action_frame, text="🗙", font=("Arial", 20), bg=bg_normal, cursor="hand2")
            unpin_btn.pack(side=tk.LEFT)
            unpin_btn.bind("<Button-1>", lambda e: self.update_pin_status(doc["doc_id"], "normal"))

        widgets = [frame, icon_frame, content_frame, action_frame, icon_lbl, lbl_name, lbl_date]

        for w in widgets:
            w.bind("<Button-1>", lambda e, doc_id=doc["doc_id"]: self.select_file(doc_id, frame, *widgets))
            w.bind("<Double-1>", lambda e, path=doc["converted_file_path"]: self.open_file(path))

    def select_file(self, doc_id, frame, *widgets):
        self.reset_selection()
        self.selected_file_id = doc_id
        self.selected_widgets = {
            "frame": frame,
            "widgets": widgets
        }
        frame.config(bg="#4CC2F1")
        for w in widgets:
            w.config(bg="#4CC2F1")

    def reset_selection(self):
        if self.selected_widgets:
            self.selected_widgets["frame"].config(bg="#4CE5F2")
            for w in self.selected_widgets["widgets"]:
                w.config(bg="#4CE5F2")
            self.selected_widgets.clear()

    def open_file(self, path):
        if os.path.exists(path):
            webbrowser.open(path)
        else:
            messagebox.showwarning("Không tìm thấy", "Không tìm thấy file tại đường dẫn: " + path)

    def update_pin_status(self, doc_id, new_status):
        try:
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor()
            cursor.execute("UPDATE documents SET status = %s WHERE doc_id = %s", (new_status, doc_id))
            db.commit()
            cursor.close()
            db.close()
            self.load_files()
            messagebox.showinfo("Thành công", f"Đã cập nhật trạng thái file {new_status}.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật trạng thái: {e}")

    def delete_file(self):
        if not self.selected_file_id:
            messagebox.showwarning("Chưa chọn file", "Hãy chọn một file để xóa.")
            return
        # Xử lý xóa file từ cơ sở dữ liệu và hệ thống file
        try:
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor()
            cursor.execute("DELETE FROM documents WHERE doc_id = %s", (self.selected_file_id,))
            db.commit()
            cursor.close()
            db.close()
            self.load_files()
            messagebox.showinfo("Thành công", "Đã xóa file.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa file: {e}")

    def delete_all_files(self):
        response = messagebox.askyesno("Xóa tất cả", "Bạn có chắc chắn muốn xóa tất cả các file không?")
        if response:
            try:
                db = get_connection()
                if db is None:
                    return
                cursor = db.cursor()
                cursor.execute("DELETE FROM documents WHERE user_id = %s", (user_data.get_current_user(),))
                db.commit()
                cursor.close()
                db.close()
                self.load_files()
                messagebox.showinfo("Thành công", "Đã xóa tất cả các file.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa các file: {e}")
if __name__ == "__main__":
    import tkinter as tk
    import user_data  # giả sử file này có sẵn hoặc bạn tạo với get_current_user() trả về user_id = 1

    def get_current_user():
        return 1  # mock user_id để test

    # Gán user_id từ hàm mock
    user_id = get_current_user()

    # Tạo cửa sổ chính
    root = tk.Tk()
    root.title("Quản lý PDF")
    root.geometry("900x700")

    # Tạo khung top như bạn mô tả
    top_frame = tk.Frame(root, height=40, bg="gray")
    top_frame.pack(side=tk.TOP, fill=tk.X)

    # Khởi tạo giao diện quản lý file PDF
    app = FileManager(root)
    # app.pack(fill="both", expand=True)

    # Gọi phương thức load files tương ứng
    app.load_files()

    root.mainloop()
