import tkinter as tk
import cv2
from PIL import Image, ImageTk

cap = None  # Biến toàn cục để quản lý camera

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

def capture_image():
    if cap is None:
        return
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("captured_image.jpg", frame)
        print("Ảnh đã được chụp và lưu")

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
                            cursor="hand2", height=2, command=capture_image)
    capture_btn.pack(side=tk.LEFT, expand=True, pady=5)

    # Bottom Frame (Icons)
    bottom_frame = tk.Frame(root, bg="lightblue", height=50)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    photo_icon = tk.Label(bottom_frame, text="🖼", font=("Arial", 20), bg="lightblue")
    photo_icon.pack(side=tk.LEFT, padx=20, pady=5)

    camera_icon = tk.Label(bottom_frame, text="📷", font=("Arial", 20), bg="lightblue")
    camera_icon.pack(side=tk.LEFT, expand=True, padx=20, pady=5)
    camera_icon.bind("<Button-1>", lambda event: open_camera(camera_label, center_frame))

    lightning_icon = tk.Label(bottom_frame, text="⚡", font=("Arial", 20), bg="lightblue")
    lightning_icon.pack(side=tk.RIGHT, padx=20, pady=5)
