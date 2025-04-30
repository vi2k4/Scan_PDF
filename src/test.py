import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K

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

    return results

# === 6) Chạy thử với ảnh mẫu ===
if __name__ == "__main__":
    img_path = r"C:\Study\Deep Learning\OCR\training_data\training_data\images\9\0.jpg"
    lines_ocr = ocr_on_image(img_path)

    print(f"Kết quả OCR cho ảnh: {img_path}")
    for (y0, y1, text) in lines_ocr:
        print(f"[y={y0}:{y1}]  {text}")
