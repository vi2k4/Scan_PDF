import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np

cap = None  
global selected_image_label  

# Hàm mở camera
def open_camera(camera_label, center_frame):
    global cap
    if cap is not None:
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera")
        cap = None
        return

    def update_frame():
        if cap is None:
            return

        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((center_frame.winfo_width(), center_frame.winfo_height() - 50)) 
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.config(image=imgtk)
            camera_label.after(10, update_frame)
        else:
            close_camera(camera_label)

    update_frame()

def close_camera(camera_label):
    global cap
    if cap is not None:
        cap.release()
        cap = None
    camera_label.config(image="", text="Camera đã tắt", fg="red")


def flash_screen():
    flash = tk.Toplevel()
    flash.geometry("1920x1080")  # Kích thước toàn màn hình
    flash.configure(bg="white")
    flash.attributes("-fullscreen", True)  # Ẩn thanh tiêu đề
    flash.after(200, flash.destroy)  # Hiển thị 200ms rồi đóng



def capture_image():
    global cap
    if cap is None:
        return
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("captured_image_flash.jpg", frame)
        print("Ảnh đã được chụp với hiệu ứng flash!")




def open_image():
    file_path = filedialog.askopenfilename(
        title="Chọn hình ảnh",
        filetypes=[("Image Files", "*.jpg;*.png")]
    )
    if file_path:
        print("Đã chọn ảnh:", file_path)
        show_selected_image(file_path)




def load_scan(root, top_frame):
    for widget in root.winfo_children():
        if widget not in [top_frame]:  # Giữ lại top_frame
            widget.pack_forget()  # Chỉ ẩn thay vì xóa

    # Center Frame (Camera)
    center_frame = tk.Frame(root, bg="white", height=600)
    center_frame.pack_propagate(False)
    center_frame.pack(side=tk.TOP, fill=tk.X)

    camera_label = tk.Label(center_frame, bg="black", width=900, height=550)
    camera_label.pack()

    # Frame chứa nút
    button_frame = tk.Frame(center_frame, bg="white")
    button_frame.pack(fill=tk.X)

    stop_camera_btn = tk.Button(button_frame, text="⛔ Kết thúc Camera", font=("Arial", 12, "bold"),
                                bg="#FF4C4C", fg="white", relief="raised", bd=3, padx=15, pady=5,
                                activebackground="#D32F2F", activeforeground="white",
                                cursor="hand2", height=2, command=lambda: close_camera(camera_label))
    stop_camera_btn.pack(side=tk.LEFT, padx=10, pady=5)

    capture_btn = tk.Button(button_frame, text="📸 Chụp Ảnh", font=("Arial", 12, "bold"),
                            bg="#4CAF50", fg="white", relief="raised", bd=3, padx=15, pady=5,
                            activebackground="#388E3C", activeforeground="white",
                            cursor="hand2", height=2,command= lambda: [flash_screen() , capture_image()])
    capture_btn.pack(side=tk.LEFT, expand=True, pady=5)

    # Bottom Frame (Icons)
    bottom_frame = tk.Frame(root, bg="lightblue", height=50)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)


    camera_icon = tk.Label(bottom_frame, text="📷", font=("Arial", 20), bg="lightblue")
    camera_icon.pack(side=tk.LEFT, expand=True, padx=20, pady=5)
    camera_icon.bind("<Button-1>", lambda event: open_camera(camera_label, center_frame))


    # Nút mở file explorer
    explorer_icon = tk.Label(bottom_frame, text="📂", font=("Arial", 20), bg="lightblue")
    explorer_icon.pack(side=tk.RIGHT, padx=20, pady=5)
    explorer_icon.bind("<Button-1>", lambda event: open_image())

    # Hiển thị ảnh đã chọn
    selected_image_label = tk.Label(center_frame, bg="white")
    selected_image_label.pack(pady=10)


def show_selected_image(file_path):
    img = Image.open(file_path)
    img = img.resize((300, 300))  # Thay đổi kích thước để hiển thị trên giao diện
    img = ImageTk.PhotoImage(img)

    selected_image_label.config(image=img)
    selected_image_label.image = img  # Lưu tham chiếu để tránh bị xóa


