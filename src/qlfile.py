import os
import shutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from functools import partial
from PIL import Image, ImageTk
import webbrowser
import scan

class FileManager:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Quản lý PDF")
        self.current_mode = "pdf"
        self.selected_file = None
        self.selected_frame = None
        self.selected_content_frame = None
        self.selected_action_frame = None
        self.selected_icon_label = None
        self.selected_name_label = None
        self.selected_time_label = None

        self.build_ui()
        self.update_header_style()
        self.load_files()

        # Chờ cửa sổ root hoàn tất trước khi tạo ảnh
        self.root.after(10, self.load_icons)  # Đảm bảo ảnh được tạo sau khi root đã sẵn sàng

    def load_icons(self):
        try:
            img_path = os.path.abspath("img/Camera.png")
            img = Image.open(img_path).resize((100, 100))
        except FileNotFoundError:
            img = Image.new("RGB", (50, 50), (200, 200, 200))  # Tạo ảnh màu xám nếu không tìm thấy

        icon = ImageTk.PhotoImage(img)
        btn_icon = tk.Button(self.root, image=icon, bd=0)
        btn_icon.image = icon
        btn_icon.place(relx=0.98, rely=0.95, anchor="se")
        btn_icon.bind("<Button-1>", lambda event: scan.load_scan(root, top_frame))

    def load_scan(self):
        # Thêm logic cho load scan ở đây nếu cần
        print("Camera scan initiated...")

    def build_ui(self):
        # Header
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

        # Nút Xóa
        self.delete_btn = tk.Button(self.header, text="Xóa", font=("Arial", 12, "bold"),
                                    bg="red", fg="white", command=self.delete_file)
        self.delete_btn.pack(side=tk.RIGHT, padx=10)

        self.delete_all_btn = tk.Button(self.header, text="Xóa tất cả", font=("Arial", 12, "bold"),
                                        bg="red", fg="white", command=self.delete_all_files)
        self.delete_all_btn.pack(side=tk.RIGHT)

        # Scroll area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = tk.Scrollbar(main_frame, command=self.canvas.yview)
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

        # Icon
        icon_frame = tk.Frame(frame, bg=bg_normal, width=50)
        icon_frame.pack(side=tk.LEFT, padx=10)

        try:
            icon_img = Image.open("img/pdf.png").resize((40, 40))  # Mở và resize ảnh PDF
            pdf_icon = ImageTk.PhotoImage(icon_img)  # Chuyển đổi ảnh thành dạng có thể sử dụng trong Tkinter
        except:
            pdf_icon = None  # Nếu không có ảnh thì gán là None

        if pdf_icon:
            icon_lbl = tk.Label(icon_frame, image=pdf_icon, bg=bg_normal)
            icon_lbl.image = pdf_icon  # Lưu giữ tham chiếu đến ảnh để tránh bị mất
            icon_lbl.pack()
        else:
            icon_lbl = tk.Label(icon_frame, text="PDF", bg=bg_normal)
            icon_lbl.pack()

        # Content
        content_frame = tk.Frame(frame, bg=bg_normal)
        content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        lbl_name = tk.Label(content_frame, text=name, font=("Arial", 18, "bold"),
                            bg=bg_normal, anchor="w", cursor="hand2")
        lbl_name.pack(side=tk.LEFT, fill=tk.X, expand=True)

        lbl_date = tk.Label(content_frame, text=date.strftime("%d/%m/%Y"),
                            font=("Arial", 14), bg=bg_normal, anchor="w", width=15)
        lbl_date.pack(side=tk.RIGHT)

        # Actions
        action_frame = tk.Frame(frame, bg=bg_normal)
        action_frame.pack(side=tk.RIGHT, padx=10)

        if self.current_mode == "pdf":
            pin_btn = tk.Label(action_frame, text="☆", font=("Arial", 25), bg=bg_normal, cursor="hand2")
            pin_btn.pack(side=tk.LEFT)
            pin_btn.bind("<Button-1>", lambda event, name=name: self.copy_to_pin_folder(name, event))
        elif self.current_mode == "pdf_ghim":
            unpin_btn = tk.Label(action_frame, text="🗙", font=("Arial", 20), bg=bg_normal, cursor="hand2")
            unpin_btn.pack(side=tk.LEFT)
            unpin_btn.bind("<Button-1>", lambda e: self.unpin_file(name))

        edit_btn = tk.Label(action_frame, text="🖉", font=("Arial", 20), bg=bg_normal, cursor="hand2")
        edit_btn.pack(side=tk.LEFT)
        edit_btn.bind("<Button-1>", lambda e: messagebox.showinfo("Chỉnh sửa", f"Chỉnh sửa {name}"))

        # Tất cả widget liên quan đều bind chọn file + mở file
        widgets = [frame, icon_frame, content_frame, action_frame,
                icon_lbl, lbl_name, lbl_date, edit_btn]

        for w in widgets:
            w.bind("<Button-1>", lambda e, f=frame, cf=content_frame, af=action_frame, 
                il=icon_lbl, n=lbl_name, t=lbl_date: self.select_file(os.path.join(folder, name), f, cf, af, il, n, t))
            w.bind("<Double-1>", lambda e, path=os.path.join(folder, name): self.open_file(path))

    def select_file(self, path, frame, cf, af, icon_lbl, name_lbl, time_lbl):
        # Kiểm tra nếu frame cũ còn tồn tại thì reset màu
        try:
            if self.selected_frame and self.selected_frame.winfo_exists():
                self.selected_frame.config(bg="#4CE5F2")
            if self.selected_content_frame and self.selected_content_frame.winfo_exists():
                self.selected_content_frame.config(bg="#4CE5F2")
            if self.selected_action_frame and self.selected_action_frame.winfo_exists():
                self.selected_action_frame.config(bg="#4CE5F2")
            if self.selected_icon_label and self.selected_icon_label.winfo_exists():
                self.selected_icon_label.config(bg="#4CE5F2")
            if self.selected_name_label and self.selected_name_label.winfo_exists():
                self.selected_name_label.config(bg="#4CE5F2")
            if self.selected_time_label and self.selected_time_label.winfo_exists():
                self.selected_time_label.config(bg="#4CE5F2")
        except:
            pass

        # Lưu frame hiện tại để xử lý tiếp
        self.selected_frame = frame
        self.selected_content_frame = cf
        self.selected_action_frame = af
        self.selected_icon_label = icon_lbl
        self.selected_name_label = name_lbl
        self.selected_time_label = time_lbl

        # Đổi màu để hiển thị chọn
        self.selected_frame.config(bg="#4CC2F1")
        self.selected_content_frame.config(bg="#4CC2F1")
        self.selected_action_frame.config(bg="#4CC2F1")
        self.selected_icon_label.config(bg="#4CC2F1")
        self.selected_name_label.config(bg="#4CC2F1")
        self.selected_time_label.config(bg="#4CC2F1")

    def open_file(self, path):
        webbrowser.open(path)  # Mở file PDF

    def copy_to_pin_folder(self, name, event):
        source_folder = os.path.abspath(self.current_mode)
        destination_folder = os.path.abspath("pdf_ghim")
        shutil.copy(os.path.join(source_folder, name), destination_folder)
        self.load_files()

    def unpin_file(self, name):
        file_path = os.path.abspath(f"pdf_ghim/{name}")
        os.remove(file_path)
        self.load_files()

    def delete_file(self):
        if self.selected_file:
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
    app = FileManager(root)
    root.mainloop()
