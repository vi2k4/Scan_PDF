import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def open_image():
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh",
        filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.bmp")]
    )
    if file_path:
        img = Image.open(file_path)
        img = img.resize((400, 400))  # Resize ảnh cho vừa giao diện
        img_tk = ImageTk.PhotoImage(img)

        image_label.config(image=img_tk)
        image_label.image = img_tk  # Giữ tham chiếu ảnh để không bị xoá

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Hiển thị ảnh")
root.geometry("500x500")
root.configure(bg="white")

# Nút chọn ảnh
open_btn = tk.Button(root, text="📂 Chọn ảnh", font=("Arial", 14), command=open_image)
open_btn.pack(pady=20)

# Label để hiển thị ảnh
image_label = tk.Label(root, bg="white")
image_label.pack(pady=10)

# Chạy vòng lặp giao diện
root.mainloop()
