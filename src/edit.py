import sys
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import os
from reportlab.pdfgen import canvas
import subprocess
from db.created_pdf import insert_document
from datetime import datetime
import scan

if len(sys.argv) > 1:
    user_id = int(sys.argv[1])
else:
    user_id = None

def load_edit(root, top_frame):
    for widget in root.winfo_children():
        if widget not in [top_frame]:
            widget.pack_forget()
            
    # Tạo Frame chính
    edit_frame = tk.Frame(root, bg="white")
    edit_frame.pack(fill=tk.BOTH, expand=True)

   # Thanh chức năng
    toolbar = tk.Frame(edit_frame, bg="#f0efed", height=30)
    toolbar.pack(fill=tk.X)

    new_scan = tk.Button(toolbar, text="Quét mới", bg="blue", fg="white", command=lambda:scan.load_scan(root,top_frame))
    new_scan.pack(fill=tk.Y, side=tk.LEFT)
    open_file = tk.Button(toolbar, text="Mở file", bg="blue", fg="white")
    open_file.pack(fill=tk.Y, side=tk.LEFT)
    save_file = tk.Button(toolbar, text="Lưu file", bg="blue", fg="white")
    save_file.pack(fill=tk.Y, side=tk.LEFT)
    pdf_export = tk.Button(toolbar, text="Xuất PDF", bg="blue", fg="white", command=lambda:export_text(text_area))
    pdf_export.pack(fill=tk.Y, side=tk.LEFT)
    preview_file = tk.Button(toolbar, text="Xem trước", bg="blue", fg="white")
    preview_file.pack(fill=tk.Y, side=tk.LEFT)

    # Phân trang
    pagebar = tk.Frame(edit_frame, bg="#070e75", width=120)
    pagebar.pack(fill=tk.Y, side=tk.LEFT)

    # Sidebar bên phải
    sidebar = tk.Frame(edit_frame, width=180, bg="#f0efed")
    sidebar.pack(fill=tk.Y, side=tk.RIGHT)

    # Công cụ chỉnh sửa
    edit_tool = tk.Frame(sidebar, bg="white")
    edit_tool.pack(fill=tk.Y, expand=False)
    edit_title = tk.Label(edit_tool, text="Công cụ chỉnh sửa", bg="white", font=("Arial", 16, "bold") )
    edit_title.pack(pady=5)

    # Tuỳ chọn kiểu
    typeface_frame = tk.Frame(edit_tool, bg="white")
    typeface_frame.pack(fill=tk.X)
    bold_button = tk.Button(typeface_frame, text= "B", bg="white", font=("Arial",14,"bold"), bd=0, highlightthickness=0)
    bold_button.pack(fill=tk.Y, side=tk.LEFT)

    # Tuỳ chỉnh font
    tk.Label(edit_tool, text="Phông chữ", bg="white").pack()
    font_var = tk.StringVar(value="Times New Roman")
    font_dropdown = ttk.Combobox(edit_tool, textvariable=font_var, values=["Arial", "Times New Roman", "Courier New"])
    font_dropdown.pack()
    font_dropdown.bind("<<ComboboxSelected>>", lambda event: text_area.config(font=(font_var.get(), int(size_var.get()))))

    # Tuỳ chỉnh kích thước
    tk.Label(edit_tool, text="Cỡ chữ", bg="white").pack()
    size_var = tk.IntVar(value=14)
    size_dropdown = ttk.Combobox(edit_tool, width=5, textvariable=size_var, values=[str(i) for i in range(8, 40)])
    size_dropdown.pack()
    size_dropdown.bind("<<ComboboxSelected>>", lambda event: text_area.config(font=(font_var.get(), int(size_var.get()))))

    # Chọn màu chữ
    tk.Label(edit_tool, text="Màu chữ", bg="white").pack()
    def choose_color():
        color_code = colorchooser.askcolor(title="Chọn màu chữ")[1]
        if color_code:
            color_button.config(bg=color_code, activebackground=color_code)
            text_area.config(fg=color_code)
    color_button = tk.Button(edit_tool, command=choose_color, width=3, bg="red")
    color_button.pack()

    # Chọn màu nền
    tk.Label(edit_tool, text="Màu nền", bg="white").pack()
    def choose_bg_color():
        color_bg = colorchooser.askcolor(title="Chọn màu nền")[1]
        if color_bg:
            color_button_bg.config(bg=color_bg, activebackground=color_bg)
            text_area.config(bg=color_bg)
    color_button_bg = tk.Button(edit_tool, command=choose_bg_color, width=3, bg="yellow")
    color_button_bg.pack()
    # Tìm kiếm
    tk.Label(sidebar, text="Tìm kiếm",font=("Arial", 16,"bold")).pack()
    search_entry = tk.Entry(sidebar)
    search_entry.pack()
    search_button = tk.Button(sidebar, text="Tìm", command=lambda: search_text(text_area, search_entry.get()))
    search_button.pack()

    # Nút quay lại menu
    back_button = tk.Button(sidebar, text="Quay lại", command=lambda: go_back(root, top_frame))
    back_button.pack(fill=tk.X,side=tk.BOTTOM, pady=10)

     #Tạo Notebọok 
    notebook = ttk.Notebook(edit_frame)
    notebook.pack(fill=tk.BOTH, expand=True)

    tab_edit = tk.Frame(notebook, bg="#f0f0f0")
    tab_scan = tk.Frame(notebook, bg="#f0f0f0")

    # Vùng nhập văn bản
    notebook.add(tab_edit, text="Văn bản đã nhận dạng")
    notebook.add(tab_scan, text="Hình ảnh gốc")
    text_area = tk.Text(tab_edit, wrap=tk.WORD, font=("Times New Roman", 14), borderwidth=0, relief="flat")
    text_area.pack(fill=tk.BOTH, expand=True)


def search_text(text_area, search_word):
    text_area.tag_remove("search", "1.0", tk.END)
    if search_word:
        start_pos = "1.0"
        while True:
            start_pos = text_area.search(search_word, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_word)}c"
            text_area.tag_add("search", start_pos, end_pos)
            text_area.tag_config("search", background="yellow")
            start_pos = end_pos

def export_text(text_area):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not BASE_DIR:
        return
    pdf_root = os.path.join(BASE_DIR, "pdf")
    user_folder = os.path.join(pdf_root, f"user{user_id}")
    ghim_folder = os.path.join(user_folder, "ghim")
    os.makedirs(user_folder, exist_ok=True)
    os.makedirs(ghim_folder, exist_ok=True)
    
    file_path = filedialog.asksaveasfilename(initialdir=user_folder, defaultextension=".pdf", 
                                             filetypes=[("PDF file", "*.pdf"), ("All files", "*.*")])
    if file_path:
        try:
            c = canvas.Canvas(file_path)
            text = text_area.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Cảnh báo", "Nội dung trống, không thể lưu file.")
                return
            # Ghi nội dung vào PDF
            y_position = 750
            lines = text.split("\n")
            for line in lines:
                c.drawString(50, y_position, line)
                y_position -= 14  # Giảm y để ghi dòng tiếp theo
                if y_position < 50:  # Chuyển trang nếu hết chỗ
                    c.showPage()
                    y_position = 750
            c.save()

            print("PDF saved to: ", file_path)
            
            title = os.path.basename(file_path)
            # Truyền giá trị cho cả original_file_path và converted_file_path
            insert_document(user_id, title, file_path, file_path, "normal", datetime.now())
            messagebox.showinfo("Thành công", "File đã được lưu thành công!")

        except Exception as e:
            print(f"ERROR: Lỗi khi lưu file PDF: {e}")
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

def go_back(root, top_frame):
    for widget in root.winfo_children():
        if widget not in [top_frame]:
            widget.pack_forget()
    top_frame.pack(fill=tk.X)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chỉnh sửa PDF")
    root.geometry("900x700")

    top_frame = tk.Frame(root, height=40, bg="gray")
    top_frame.pack(side=tk.TOP, fill=tk.X)

    load_edit(root, top_frame)

    root.mainloop()
