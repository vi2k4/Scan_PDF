import os
import shutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import webbrowser
import mysql.connector
import user_data

# ---------- KẾT NỐI DATABASE ----------
def get_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Thay bằng mật khẩu MySQL nếu có
            database="my_scanner_db"
        )
        print("DEBUG: Kết nối cơ sở dữ liệu thành công")
        return db
    except Exception as e:
        print(f"ERROR: Không thể kết nối cơ sở dữ liệu: {e}")
        messagebox.showerror("Lỗi kết nối", f"Không thể kết nối cơ sở dữ liệu: {e}")
        return None

# ---------- TẢI DỮ LIỆU FILE ----------
def load_file(root, top_frame, user_id):
    print(f"DEBUG: user_id được truyền vào = {user_id}")
    print(f"DEBUG: user_data.get_current_user() = {user_data.get_current_user()}")
    
    # Sử dụng user_id được truyền vào nếu có, nếu không thì lấy từ user_data
    effective_user_id = user_id if user_id is not None else user_data.get_current_user()
    print(f"DEBUG: effective_user_id = {effective_user_id}")

    if not top_frame:
        print("LỖI: top_frame = None, không thể hiển thị giao diện file")
        return

    for widget in root.winfo_children():
        if widget not in [top_frame]:
            widget.pack_forget()

    query = """
        SELECT * FROM documents
        WHERE user_id = %s AND status = %s
        ORDER BY created_at DESC
    """
    mode_status = "normal"

    try:
        db = get_connection()
        if db is None:
            return

        cursor = db.cursor(dictionary=True)
        print(f"DEBUG: Truy vấn SQL: {query % (effective_user_id, mode_status)}")
        cursor.execute(query, (effective_user_id, mode_status))
        rows = cursor.fetchall()
        print(f"DEBUG: Số bản ghi: {len(rows)}")
        print(f"DEBUG: Dữ liệu lấy về: {rows}")

        # Luôn khởi tạo FileManager, ngay cả khi không có dữ liệu
        file_manager = FileManager(root)
        file_manager.load_files(rows)

        # Hiển thị thông báo nếu không có dữ liệu
        if not rows:
            print("DEBUG: Không có dữ liệu để hiển thị.")
            messagebox.showinfo("Thông báo", "Không có dữ liệu để hiển thị.")

        cursor.close()
        db.close()
    except Exception as e:
        print(f"ERROR: Lỗi khi tải dữ liệu: {e}")
        messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")

# ---------- CLASS QUẢN LÝ FILE ----------
class FileManager:
    def __init__(self, root):
        self.root = root
        self.current_mode = "pdf"
        self.selected_file_id = None
        self.selected_widgets = {}
        self.build_ui()
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

    def refresh_files(self):
        """Tải lại danh sách file từ cơ sở dữ liệu dựa trên current_mode."""
        query = """
            SELECT * FROM documents
            WHERE user_id = %s AND status = %s
            ORDER BY created_at DESC
        """
        mode_status = "normal" if self.current_mode == "pdf" else "pinned"
        try:
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor(dictionary=True)
            cursor.execute(query, (user_data.get_current_user(), mode_status))
            rows = cursor.fetchall()
            print(f"DEBUG: Tải lại file - Số bản ghi: {len(rows)}")
            print(f"DEBUG: Dữ liệu tải lại: {rows}")
            self.load_files(rows)
            if not rows:
                print(f"DEBUG: Không có dữ liệu để hiển thị trong tab {'File' if self.current_mode == 'pdf' else 'Ghim'}.")
                messagebox.showinfo("Thông báo", "Không có dữ liệu để hiển thị.")
            cursor.close()
            db.close()
        except Exception as e:
            print(f"ERROR: Lỗi khi tải lại file: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải lại danh sách file: {e}")

    def switch_mode(self, mode):
        if self.current_mode != mode:
            self.current_mode = mode
            self.update_header_style()
            self.refresh_files()  # Tải lại file khi chuyển mode

    def update_header_style(self):
        target = self.lbl_file if self.current_mode == "pdf" else self.lbl_pin
        self.root.after(10, lambda: self.underline.place_configure(
            x=target.winfo_x(), width=target.winfo_width()))

    def load_files(self, rows=None):
        if rows is None:
            rows = []

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        print(f"DEBUG: Đang tải {len(rows)} file vào giao diện")
        for doc in rows:
            self.create_file_entry(doc)

    def create_file_entry(self, doc):
        bg_normal = "#4CE5F2"
        bg_selected = "#4CC2F1"

        frame = tk.Frame(self.scrollable_frame, bg=bg_normal, height=60, width=800, bd=1, relief="solid")
        frame.pack(fill=tk.X, padx=20, pady=5)
        frame.pack_propagate(False)

        icon_frame = tk.Frame(frame, bg=bg_normal, width=50)
        icon_frame.pack(side=tk.LEFT, padx=10)

        try:
            icon_img = Image.open("img/pdf.png").resize((40, 40))
            pdf_icon = ImageTk.PhotoImage(icon_img)
        except Exception as e:
            print(f"DEBUG: Lỗi tải icon: {e}")
            pdf_icon = None

        icon_lbl = tk.Label(icon_frame, image=pdf_icon if pdf_icon else None,
                            text="PDF" if not pdf_icon else "", bg=bg_normal)
        if pdf_icon:
            icon_lbl.image = pdf_icon
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

        print(f"DEBUG: Đã tạo widget cho file: {doc['title']}")

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
            cursor = db.cursor(dictionary=True)

            if new_status == "pinned":
                # Lấy thông tin file gốc
                cursor.execute("SELECT * FROM documents WHERE doc_id = %s AND status = 'normal'", (doc_id,))
                file_info = cursor.fetchone()
                if not file_info:
                    messagebox.showerror("Lỗi", "Không tìm thấy file để ghim.")
                    cursor.close()
                    db.close()
                    return

                # Tạo bản ghi mới với status = 'pinned'
                insert_query = """
                    INSERT INTO documents (user_id, title, original_file_path, converted_file_path, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    file_info["user_id"],
                    file_info["title"],
                    file_info["original_file_path"],
                    file_info["converted_file_path"],
                    "pinned",
                    file_info["created_at"]
                ))
                db.commit()
                print(f"DEBUG: Đã tạo bản ghi pinned cho file doc_id = {doc_id}, title = {file_info['title']}")

            elif new_status == "normal":
                # Xóa bản ghi pinned
                cursor.execute("DELETE FROM documents WHERE doc_id = %s AND status = 'pinned'", (doc_id,))
                db.commit()
                print(f"DEBUG: Đã xóa bản ghi pinned với doc_id = {doc_id}")

            cursor.close()
            db.close()
            self.refresh_files()  # Tải lại file sau khi ghim/bỏ ghim
            messagebox.showinfo("Thành công", f"Đã {'ghim' if new_status == 'pinned' else 'bỏ ghim'} file.")
        except Exception as e:
            print(f"ERROR: Lỗi khi cập nhật trạng thái ghim: {e}")
            messagebox.showerror("Lỗi", f"Không thể cập nhật trạng thái: {e}")

    def delete_file(self):
        if not self.selected_file_id:
            messagebox.showwarning("Chưa chọn file", "Hãy chọn một file để xóa.")
            return

        # Kiểm tra thông tin file trước khi xóa
        try:
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT title FROM documents WHERE doc_id = %s", (self.selected_file_id,))
            file_info = cursor.fetchone()
            cursor.close()
            db.close()

            if file_info:
                confirm = messagebox.askyesno(
                    "Xác nhận xóa",
                    f"Bạn có chắc muốn xóa file '{file_info['title']}' không?"
                )
                if not confirm:
                    print("DEBUG: Người dùng hủy xóa file")
                    return

            # Tiến hành xóa
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor()
            cursor.execute("DELETE FROM documents WHERE doc_id = %s", (self.selected_file_id,))
            db.commit()
            cursor.close()
            db.close()
            print(f"DEBUG: Đã xóa file với doc_id = {self.selected_file_id}")
            self.refresh_files()  # Tải lại file sau khi xóa
            messagebox.showinfo("Thành công", "Đã xóa file.")
        except Exception as e:
            print(f"ERROR: Lỗi khi xóa file: {e}")
            messagebox.showerror("Lỗi", f"Không thể xóa file: {e}")

    def delete_all_files(self):
        # Kiểm tra số lượng file trước khi xóa
        try:
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM documents WHERE user_id = %s AND status = %s",
                           (user_data.get_current_user(), "normal" if self.current_mode == "pdf" else "pinned"))
            count = cursor.fetchone()[0]
            cursor.close()
            db.close()

            if count == 0:
                messagebox.showinfo("Thông báo", "Không có file nào để xóa.")
                return

            confirm = messagebox.askyesno(
                "Xác nhận xóa tất cả",
                f"Bạn có chắc muốn xóa {count} file trong chế độ {'File' if self.current_mode == 'pdf' else 'Ghim'} không?"
            )
            if not confirm:
                print("DEBUG: Người dùng hủy xóa tất cả file")
                return

            # Tiến hành xóa tất cả
            db = get_connection()
            if db is None:
                return
            cursor = db.cursor()
            cursor.execute("DELETE FROM documents WHERE user_id = %s AND status = %s",
                           (user_data.get_current_user(), "normal" if self.current_mode == "pdf" else "pinned"))
            db.commit()
            cursor.close()
            db.close()
            print(f"DEBUG: Đã xóa {count} file")
            self.refresh_files()  # Tải lại file sau khi xóa
            messagebox.showinfo("Thành công", "Đã xóa tất cả các file.")
        except Exception as e:
            print(f"ERROR: Lỗi khi xóa tất cả file: {e}")
            messagebox.showerror("Lỗi", f"Không thể xóa tất cả file: {e}")

if __name__ == "__main__":
    # Mock user_data để test
    def get_current_user():
        return 1  # Giả lập user_id = 1

    # Gán user_id
    user_data.get_current_user = get_current_user
    user_id = get_current_user()

    # Tạo cửa sổ chính
    root = tk.Tk()
    root.title("Quản lý PDF")
    root.geometry("900x700")

    # Tạo top_frame
    top_frame = tk.Frame(root, height=40, bg="gray")
    top_frame.pack(side=tk.TOP, fill=tk.X)

    # Tải dữ liệu và hiển thị
    load_file(root, top_frame, user_id)

    root.mainloop()