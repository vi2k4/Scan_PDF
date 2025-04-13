import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np

cap = None  
selected_image_label = None  # Khai báo biến toàn cục

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

            # Resize ảnh theo kích thước của centerFrame
            img = img.resize((center_frame.winfo_width(), center_frame.winfo_height()), Image.Resampling.LANCZOS)

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
    flash.geometry("1920x1080")
    flash.configure(bg="white")
    flash.attributes("-fullscreen", True)
    flash.after(200, flash.destroy)


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
        filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.bmp")]
    )
    if file_path:
        print("Đã chọn ảnh:", file_path)
        show_selected_image(file_path)


def show_selected_image(file_path):
    img = Image.open(file_path)

    # Kích thước cố định của label
    target_width, target_height = 900, 550
    img_width, img_height = img.size

    # Tính tỷ lệ resize để không bóp ảnh
    ratio = min(target_width / img_width, target_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)

    # Resize ảnh theo tỷ lệ
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Tạo ảnh nền trắng đúng kích thước label
    background = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # Tính tọa độ để canh giữa ảnh resized trong nền
    offset_x = (target_width - new_width) // 2
    offset_y = (target_height - new_height) // 2
    background.paste(img, (offset_x, offset_y))

    # Tạo cửa sổ hiển thị ảnh
    img_window = tk.Toplevel()
    img_window.title("Ảnh đã chọn")
    img_window.configure(bg="white")

    img_tk = ImageTk.PhotoImage(background)
    label = tk.Label(img_window, image=img_tk, bg="white", width=target_width, height=target_height)
    label.image = img_tk
    label.pack(padx=10, pady=10)

    # Nút scan
    scan_btn = tk.Button(img_window, text="🔍 Scan", font=("Arial", 12, "bold"),
                         bg="#1976D2", fg="white", padx=20, pady=10,
                         command=lambda: print(">> Thực hiện scan ảnh..."))
    scan_btn.pack(pady=10)


def load_scan(root, top_frame):
    global selected_image_label

    for widget in root.winfo_children():
        if widget not in [top_frame]:
            widget.pack_forget()

    # Center Frame
    center_frame = tk.Frame(root, bg="white", height=600)
    center_frame.pack_propagate(False)
    center_frame.pack(side=tk.TOP, fill=tk.X)

    camera_label = tk.Label(center_frame, bg="black", width=900, height=550)
    camera_label.pack()

    # Nút chức năng
    button_frame = tk.Frame(center_frame, bg="white")
    button_frame.pack(fill=tk.X)

    stop_camera_btn = tk.Button(button_frame, text="⛔ Kết thúc Camera", font=("Arial", 12, "bold"),
                                bg="#FF4C4C", fg="white", relief="raised", bd=3, padx=15, pady=5,
                                activebackground="#D32F2F", activeforeground="white",
                                cursor="hand2", height=2,
                                command=lambda: close_camera(camera_label))
    stop_camera_btn.pack(side=tk.LEFT, padx=10, pady=5)

    capture_btn = tk.Button(button_frame, text="📸 Chụp Ảnh", font=("Arial", 12, "bold"),
                            bg="#4CAF50", fg="white", relief="raised", bd=3, padx=15, pady=5,
                            activebackground="#388E3C", activeforeground="white",
                            cursor="hand2", height=2,
                            command=lambda: [flash_screen(), capture_image()])
    capture_btn.pack(side=tk.LEFT, expand=True, pady=5)

    # Bottom Frame
    bottom_frame = tk.Frame(root, bg="lightblue", height=50)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    camera_icon = tk.Label(bottom_frame, text="📷", font=("Arial", 20), bg="lightblue")
    camera_icon.pack(side=tk.LEFT, expand=True, padx=20, pady=5)
    camera_icon.bind("<Button-1>", lambda event: open_camera(camera_label, center_frame))

    explorer_icon = tk.Label(bottom_frame, text="📂", font=("Arial", 20), bg="lightblue")
    explorer_icon.pack(side=tk.RIGHT, padx=20, pady=5)
    explorer_icon.bind("<Button-1>", lambda event: open_image())




# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Chụp và Chọn Ảnh")
#     root.geometry("1000x550")
#     root.configure(bg="white")

#     # Frame phía trên cùng (giữ nguyên)
#     top_frame = tk.Frame(root, bg="skyblue", height=50)
#     top_frame.pack(side=tk.TOP, fill=tk.X)
#     title_label = tk.Label(top_frame, text="📸 Ứng dụng Chụp & Chọn Ảnh", font=("Arial", 16, "bold"), bg="skyblue")
#     title_label.pack(pady=10)

#     # Gọi giao diện camera + chức năng
#     load_scan(root, top_frame)

#     root.mainloop()
