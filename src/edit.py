import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

def load_edit(root, top_frame,text):
    for widget in root.winfo_children():
        # giữ lại top_frame
        if widget is top_frame:
            continue
        # chỉ bỏ pack với widget được quản lý bằng pack()
        if widget.winfo_manager() == "pack":
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
    text_area.delete("1.0", "end")  # Xóa nội dung cũ (nếu cần)
    text_area.insert("1.0", text)   # Chèn nội dung mới từ biến `text`

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
    import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import os
from reportlab.pdfgen import canvas
import subprocess
from db.created_pdf import insert_document
from datetime import datetime
import scan
import tkinter.messagebox

if len(sys.argv) > 1:
    user_id = int(sys.argv[1])
else:
    user_id = None


def show_tab_text(get_current_text_widget):
    global img_label
    if "img_label" in globals() and img_label.winfo_ismapped():
        img_label.pack_forget()
    if not get_current_text_widget.winfo_ismapped():
        get_current_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def show_tab_scan(tab_scan, get_current_text_widget):
    global img_label, img
    image_path = "captured_image_flash.jpg"

    if not os.path.exists(image_path):
        print("Không tìm thấy hình ảnh gốc!")
        return

    if "img_label" in globals() and img_label.winfo_ismapped():
        return
    
    if get_current_text_widget.winfo_ismapped():
        get_current_text_widget.pack_forget()

    img_raw = Image.open(image_path)

    # Cập nhật giao diện để lấy đúng kích thước frame
    tab_scan.update()
    frame_width = tab_scan.winfo_width()
    frame_height = tab_scan.winfo_height()

    # Resize ảnh giữ tỉ lệ vừa khung
    img_raw.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img_raw)
    
    if "img_label" not in globals():
        img_label = tk.Label(tab_scan, image=img, bg="#f0f0f0")
        img_label.image = img
    else:
        img_label.config(image=img)
        img_label.image = img

    img_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def on_tab_changed(event, get_current_text_widget, tab_scan):
    tab_text = event.widget.tab(event.widget.select(), "text")
    if tab_text == "Văn bản đã nhận dạng":
        show_tab_text(get_current_text_widget())
    elif tab_text == "Hình ảnh gốc":
        show_tab_scan(tab_scan, get_current_text_widget())
        
def toggle_tag(widget, tag_name, font_tuple):
    try:
        current_tags = widget.tag_names("sel.first")
        if tag_name in current_tags:
            widget.tag_remove(tag_name, "sel.first", "sel.last")
        else:
            widget.tag_add(tag_name, "sel.first", "sel.last")
            widget.tag_config(tag_name, font=font_tuple)
    except tk.TclError:
        pass  # Không có vùng chọn


def search_text(get_current_text_widget, search_word):
    get_current_text_widget.tag_remove("search", "1.0", tk.END)
    if search_word:
        start_pos = "1.0"
        while True:
            start_pos = get_current_text_widget.search(search_word, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_word)}c"
            get_current_text_widget.tag_add("search", start_pos, end_pos)
            get_current_text_widget.tag_config("search", background="yellow")
            start_pos = end_pos
            
def replacement_text(text_widget, search_term, replacement):
    if not search_term:
        return
    start_pos = "1.0"
    while True:
        start_pos = text_widget.search(search_term, start_pos, stopindex=tk.END)
        if not start_pos:
            break
        end_pos = f"{start_pos}+{len(search_term)}c"
        text_widget.delete(start_pos, end_pos)
        text_widget.insert(start_pos, replacement)
        start_pos = end_pos
            
def open_text_file(get_current_text_widget):
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        widget = get_current_text_widget()
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
def save_text_file(get_current_text_widget):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            text = get_current_text_widget().get("1.0", tk.END)
            f.write(text.strip())

def preview_text(get_current_text_widget):
    from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y

    preview_win = Toplevel()
    preview_win.title("Xem trước nội dung")
    preview_win.geometry("600x400")

    preview_text_widget = Text(preview_win, wrap=tk.WORD)
    preview_text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    scroll = Scrollbar(preview_win, command=preview_text_widget.yview)
    scroll.pack(side=RIGHT, fill=Y)
    preview_text_widget.config(yscrollcommand=scroll.set)

    content = get_current_text_widget.get("1.0", tk.END)
    preview_text_widget.insert(tk.END, content)
    preview_text_widget.config(state=tk.DISABLED)

        
def export_text(get_current_text_widget):
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
            text = get_current_text_widget.get("1.0", tk.END).strip()
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

def load_edit(root, top_frame, text):
    for widget in root.winfo_children():
        if widget is top_frame:
            continue
        if widget.winfo_manager() == "pack":
            widget.pack_forget()

    edit_frame = tk.Frame(root, bg="white")
    edit_frame.pack(fill=tk.BOTH, expand=True)

    # Thanh công cụ
    toolbar = tk.Frame(edit_frame, bg="#e0e0e0", height=40)
    toolbar.pack(fill=tk.X)

    button_style = {"bg": "#4a90e2", "fg": "white", "padx": 10, "pady": 5, "bd": 0, "font": ("Arial", 10)}

    tk.Button(toolbar, text="Quét mới", command=lambda: scan.load_scan(root, top_frame), **button_style).pack(side=tk.LEFT, padx=2)
    tk.Button(toolbar, text="Mở file", command= lambda: open_text_file(get_current_text_widget()), **button_style).pack(side=tk.LEFT, padx=2)
    tk.Button(toolbar, text="Lưu file", command=lambda: save_text_file(get_current_text_widget()), **button_style).pack(side=tk.LEFT, padx=2)
    tk.Button(toolbar, text="Xuất PDF", command=lambda: export_text(get_current_text_widget()), **button_style).pack(side=tk.LEFT, padx=2)
    tk.Button(toolbar, text="Xem trước", command=lambda: preview_text(get_current_text_widget()), **button_style).pack(side=tk.LEFT, padx=2)

    # Sidebar trái
    pagebar = tk.Frame(edit_frame, bg="#1c1f4c", width=120)
    pagebar.pack(fill=tk.Y, side=tk.LEFT)

    # Sidebar phải
    sidebar = tk.Frame(edit_frame, width=200, bg="#f7f7f7")
    sidebar.pack(fill=tk.Y, side=tk.RIGHT)

    edit_tool = tk.Frame(sidebar, bg="white")
    edit_tool.pack(pady=10, fill=tk.X)

    tk.Label(edit_tool, text="Công cụ chỉnh sửa", bg="white", font=("Arial", 14, "bold")).pack(pady=(0, 10))

    typeface_frame = tk.Frame(edit_tool, bg="white")
    typeface_frame.pack(pady=5)

    tk.Button(typeface_frame, text="B", font=("Arial", 12, "bold"), bg="#4a90e2", fg="white",
              command=lambda: toggle_tag(get_current_text_widget(), "bold", ("Arial", 14, "bold"))).pack(side=tk.LEFT, padx=2)

    tk.Button(typeface_frame, text="I ", font=("Arial", 12, "italic"), bg="#4a90e2", fg="white",
              command=lambda: toggle_tag(get_current_text_widget(), "italic", ("Arial", 14, "italic"))).pack(side=tk.LEFT, padx=2)

    tk.Button(typeface_frame, text="U", font=("Arial", 12, "underline"), bg="#4a90e2", fg="white",
              command=lambda: toggle_tag(get_current_text_widget(), "underline", ("Arial", 14, "underline"))).pack(side=tk.LEFT, padx=2)

    # Font
    tk.Label(edit_tool, text="Phông chữ", bg="white").pack(pady=(10, 0))
    font_var = tk.StringVar(value="Times New Roman")
    font_dropdown = ttk.Combobox(edit_tool, textvariable=font_var, values=["Arial", "Times New Roman", "Courier New"])
    font_dropdown.pack()

    # Size
    tk.Label(edit_tool, text="Cỡ chữ", bg="white").pack(pady=(10, 0))
    size_var = tk.IntVar(value=14)
    size_dropdown = ttk.Combobox(edit_tool, width=5, textvariable=size_var, values=[str(i) for i in range(8, 40)])
    size_dropdown.pack()

    font_dropdown.bind("<<ComboboxSelected>>", lambda e: get_current_text_widget().config(font=(font_var.get(), size_var.get())))
    size_dropdown.bind("<<ComboboxSelected>>", lambda e: get_current_text_widget().config(font=(font_var.get(), size_var.get())))

    # Màu chữ
    tk.Label(edit_tool, text="Màu chữ", bg="white").pack(pady=(10, 0))
    color_button = tk.Button(edit_tool, bg="black", width=3, command=lambda: choose_color(color_button))
    color_button.pack()

    def choose_color(button):
        color_code = colorchooser.askcolor()[1]
        if color_code:
            button.config(bg=color_code)
            get_current_text_widget().config(fg=color_code)

    # Màu nền
    tk.Label(edit_tool, text="Màu nền", bg="white").pack(pady=(10, 0))
    color_button_bg = tk.Button(edit_tool, bg="white", width=3, command=lambda: choose_bg_color(color_button_bg))
    color_button_bg.pack()

    def choose_bg_color(button):
        color_code = colorchooser.askcolor()[1]
        if color_code:
            button.config(bg=color_code)
            get_current_text_widget().config(bg=color_code)

    # Tìm kiếm và thay thế
    tk.Label(sidebar, text="Tìm kiếm", font=("Arial", 12, "bold"), bg="#f7f7f7").pack(pady=(20, 0))
    search_entry = tk.Entry(sidebar)
    search_entry.pack(padx=10, pady=2)
    tk.Button(sidebar, text="Tìm", command=lambda: search_text(get_current_text_widget(), search_entry.get())).pack(pady=2)

    replacement_entry = tk.Entry(sidebar)
    replacement_entry.pack(padx=10, pady=2)
    tk.Button(sidebar, text="Thay thế", command=lambda: replacement_text(get_current_text_widget(), search_entry.get(), replacement_entry.get())).pack(pady=2)

    tk.Button(sidebar, text="Quay lại", command=lambda: go_back(root, top_frame), bg="#d9534f", fg="white").pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    # Notebook
    notebook = ttk.Notebook(edit_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    tab_edit = tk.Frame(notebook, bg="#f8f8f8")
    tab_scan = tk.Frame(notebook, bg="#f8f8f8")
    notebook.add(tab_edit, text="Văn bản đã nhận dạng")
    notebook.add(tab_scan, text="Hình ảnh gốc")

    # Trang văn bản
    page_display = tk.Frame(tab_edit, bg="#ddd")
    page_display.pack(fill=tk.BOTH, expand=True)
    pages = []
    current_page_index = [0]

    def get_current_text_widget():
        return pages[current_page_index[0]]['text']

    def add_page(content=""):
        if pages:
            pages[current_page_index[0]]['frame'].pack_forget()

        page_frame = tk.Frame(page_display, width=595, height=842, bg="white", bd=2, relief="ridge")
        page_frame.pack(pady=20)
        page_frame.pack_propagate(False)

        text_widget = tk.Text(page_frame, wrap=tk.WORD, font=("Times New Roman", 14), relief="flat")
        text_widget.insert("1.0", content)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        pages.append({"frame": page_frame, "text": text_widget})
        current_page_index[0] = len(pages) - 1
        update_pagebar()

    def delete_current_page():
        if len(pages) <= 1:
            messagebox.showinfo("Thông báo", "Không thể xóa vì chỉ còn 1 trang.")
            return
        pages[current_page_index[0]]['frame'].pack_forget()
        pages[current_page_index[0]]['frame'].destroy()
        del pages[current_page_index[0]]

        current_page_index[0] = min(current_page_index[0], len(pages) - 1)
        pages[current_page_index[0]]['frame'].pack(pady=20)
        update_pagebar()

    def update_pagebar():
        for widget in pagebar.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()
        for i in range(len(pages)):
            ttk.Button(pagebar, text=f"Trang {i + 1}", width=10, command=lambda i=i: show_page(i)).pack(pady=2)
        ttk.Button(pagebar, text="Xóa", width=10, command=delete_current_page).pack(pady=5, side=tk.BOTTOM)  
        ttk.Button(pagebar, text="Thêm", width=10, command=lambda: add_page()).pack(pady=5, side=tk.BOTTOM)

    def show_page(index):
        pages[current_page_index[0]]['frame'].pack_forget()
        pages[index]['frame'].pack(pady=20)
        current_page_index[0] = index

    add_page(text)
    notebook.bind("<<NotebookTabChanged>>", lambda e: on_tab_changed(e, get_current_text_widget, tab_scan))
