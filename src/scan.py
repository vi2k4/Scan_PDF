import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
import edit

# === 1) Load model predict đã train xong ===
model = tf.keras.models.load_model("src/crnn_predict_1.keras", compile=False)

# === 2) Bộ ký tự & map ===
characters = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪĐÊỀẾỆỂỄÔỒỐỘỔỖƠỜỚỢỞỠƯỪỨỰỬỮÝỲỴỶỸ"
    "abcdefghijklmnopqrstuvwxyzàáạảãăằắặẳẵâầấậẩẫđêềếệểễôồốộổỗơờớợởỡưừứựửữýỳỵỷỹ"
    "0123456789,.-/ "
)
char_to_num = {c: i for i, c in enumerate(characters)}
num_to_char = {i: c for c, i in char_to_num.items()}

# === 3) Hàm phân tách dòng cải tiến ===
def segment_lines(img_gray,
                  thresh_method="otsu",
                  min_line_height=20,
                  min_gap=15):
    """
    - Dùng horizontal projection profile để tìm khoảng trống giữa các dòng.
    - Lọc bỏ các vùng quá nhỏ theo min_line_height.
    """
    h, w = img_gray.shape

    # 1) threshold (invert: text=255)
    if thresh_method == "otsu":
        _, bw = cv2.threshold(img_gray, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        bw = cv2.adaptiveThreshold(img_gray, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV,
                                   25, 15)

    # 2) horizontal projection: đếm pixel text trên mỗi hàng
    proj = bw.sum(axis=1)  # length = h

    # 3) tìm các vùng có proj > 0 => trong dòng, ngắt tại những gap dài >= min_gap
    lines = []
    in_line = False
    start = 0
    gap = 0
    for y in range(h):
        if proj[y] > 0:
            if not in_line:
                # bắt đầu một line mới
                in_line = True
                start = y
            gap = 0
        else:
            if in_line:
                gap += 1
                # nếu gap đủ lớn, kết thúc line
                if gap >= min_gap:
                    end = y - gap
                    if (end - start) >= min_line_height:
                        lines.append((start, end))
                    in_line = False
    # nếu file kết thúc vẫn đang trong line
    if in_line and (h - start) >= min_line_height:
        lines.append((start, h - 1))

    return lines

# === 4) Tiền xử lý ảnh và decode CTC ===
def preprocess_for_model(img_gray, img_w=400, img_h=67):
    img = cv2.resize(img_gray, (img_w, img_h))
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=-1)

def decode_seq(seq):
    return "".join(num_to_char[i] for i in seq if i in num_to_char)

# === 5) OCR trên toàn ảnh ===
def ocr_on_image(img_path):
    gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise FileNotFoundError(f"Không mở được ảnh: {img_path}")

    # 3.1 tách dòng bằng projection
    line_bounds = segment_lines(gray,
                                thresh_method="otsu",
                                min_line_height=20,
                                min_gap=15)

    results = []
    for idx, (y0, y1) in enumerate(line_bounds):
        line_img = gray[y0:y1, :]
        # 3.2 tiền xử lý và predict
        proc = preprocess_for_model(line_img)
        batch = np.expand_dims(proc, axis=0)          # (1,H,W,1)
        pred  = model.predict(batch)                  # (1,100, num_classes)
        seq_len = np.array([pred.shape[1]], dtype=np.int32)

        # 3.3 CTC decode
        decoded, _ = K.ctc_decode(
            pred,
            seq_len,
            greedy=False,
            beam_width=30,   # tăng beam-width để cải thiện
            top_paths=1
        )
        seq = decoded[0].numpy()[0]
        text = decode_seq(seq)

        results.append((y0, y1, text))
        print(text)

    return text

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
        ocr_on_image("captured_image_flash.jpg")
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
                         command=lambda: ocr_on_image(file_path))
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
