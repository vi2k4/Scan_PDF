import os
import shutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import webbrowser
def load_file(root, top_frame):
    print("DEBUG: Tải giao diện Quản lý File")

    if not top_frame:
        print("LỖI: top_frame = None, không thể hiển thị Quản lý File")
        return

    # Ẩn tất cả các widget ngoài top_frame
    for widget in root.winfo_children():
        if widget != top_frame:  # Giữ lại top_frame
            widget.pack_forget()  # Sử dụng pack_forget thay vì destroy để tránh tạo lại không cần thiết

    # Tạo lại giao diện Quản lý File
    file_manager_frame = tk.Frame(root, padx=0, pady=0)
    file_manager_frame.pack(fill=tk.BOTH, expand=True, pady=0)  # Đảm bảo không có khoảng cách (pady=0)

    # Đảm bảo rằng top_frame không thay đổi kích thước tự động và không có khoảng cách
    top_frame.pack_propagate(False)  # Ngừng tự động thay đổi kích thước của top_frame
    top_frame.pack(side="top", fill="x", padx=0, pady=0)  # Đảm bảo không có khoảng cách thừa

    # Khởi tạo FileManager với root thay vì file_manager_frame
    file_manager = FileManager(root)  # Truyền root vào thay vì frame
    file_manager.load_files()  # Nếu cần, bạn có thể gọi lại các phương thức để load lại file

class FileManager:
    def __init__(self, root):
        self.root = root
        # self.root.title("Quản lý PDF")
        self.current_mode = "pdf"
        self.selected_file = None
        self.selected_widgets = {}

        self.build_ui()
        self.update_header_style()
        self.load_files()
   

    def build_ui(self):
        # Header
        self.header = tk.Frame(self.root, bg="#f5f5f5", height=60)
        self.header.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)  # Kiểm tra lại padding của header
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

        # Scroll area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)  # Kiểm tra padding cho main_frame

        self.canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = tk.Scrollbar(main_frame, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)  # Kiểm tra lại padding cho canvas
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
        folder = os.path.abspath(self.current_mode)
        os.makedirs(folder, exist_ok=True)
        files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
        grouped = {}

        for file in files:
            full_path = os.path.join(folder, file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(full_path))
            key = mod_time.strftime("%m/%Y")
            grouped.setdefault(key, []).append((file, mod_time))

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for month_year, file_list in grouped.items():
            section = tk.Label(self.scrollable_frame, text=month_year, font=("Arial", 14, "bold"), bg="white")
            section.pack(anchor='w', padx=15, pady=(10, 0))
            for name, date in file_list:
                self.create_file_entry(folder, name, date)

    def create_file_entry(self, folder, name, date):
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

        lbl_name = tk.Label(content_frame, text=name, font=("Arial", 18, "bold"),
                            bg=bg_normal, anchor="w", cursor="hand2")
        lbl_name.pack(side=tk.LEFT, fill=tk.X, expand=True)

        lbl_date = tk.Label(content_frame, text=date.strftime("%d/%m/%Y"),
                            font=("Arial", 14), bg=bg_normal, anchor="w", width=15)
        lbl_date.pack(side=tk.RIGHT)

        action_frame = tk.Frame(frame, bg=bg_normal)
        action_frame.pack(side=tk.RIGHT, padx=10)

        if self.current_mode == "pdf":
            pin_btn = tk.Label(action_frame, text="☆", font=("Arial", 25), bg=bg_normal, cursor="hand2")
            pin_btn.pack(side=tk.LEFT)
            pin_btn.bind("<Button-1>", lambda e: self.copy_to_pin_folder(name))
        else:
            unpin_btn = tk.Label(action_frame, text="🗙", font=("Arial", 20), bg=bg_normal, cursor="hand2")
            unpin_btn.pack(side=tk.LEFT)
            unpin_btn.bind("<Button-1>", lambda e: self.unpin_file(name))

        edit_btn = tk.Label(action_frame, text="🖉", font=("Arial", 20), bg=bg_normal, cursor="hand2")
        edit_btn.pack(side=tk.LEFT)
        edit_btn.bind("<Button-1>", lambda e: messagebox.showinfo("Chỉnh sửa", f"Chỉnh sửa {name}"))

        widgets = [frame, icon_frame, content_frame, action_frame, icon_lbl, lbl_name, lbl_date, edit_btn]

        for w in widgets:
            w.bind("<Button-1>", lambda e, path=os.path.join(folder, name): self.select_file(path, frame, icon_lbl, lbl_name, lbl_date, content_frame, action_frame))
            w.bind("<Double-1>", lambda e, path=os.path.join(folder, name): self.open_file(path))

    def select_file(self, path, frame, *widgets):
        self.reset_selection()
        self.selected_file = path
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
        webbrowser.open(path)

    def copy_to_pin_folder(self, name):
        shutil.copy(os.path.join(self.current_mode, name), "pdf_ghim")
        self.load_files()

    def unpin_file(self, name):
        os.remove(os.path.join("pdf_ghim", name))
        self.load_files()

    def delete_file(self):
        if self.selected_file and os.path.exists(self.selected_file):
            os.remove(self.selected_file)
            self.load_files()

    def delete_all_files(self):
        folder = os.path.abspath(self.current_mode)
        for filename in os.listdir(folder):
            os.remove(os.path.join(folder, filename))
        self.load_files()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x700")
    root.config(padx=0, pady=0)  # Loại bỏ padding ngoài gốc
    app = FileManager(root)
    root.mainloop()
