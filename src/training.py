import os
import re
import cv2
import numpy as np
import string
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Conv2D, BatchNormalization, Activation, MaxPooling2D,
    Reshape, Bidirectional, LSTM, Dense, Lambda, Dropout
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    ReduceLROnPlateau, EarlyStopping, ModelCheckpoint
)

# ========== 1. Cấu hình đường dẫn & tham số ==========
labels_folder = r"C:/Study/Deep Learning/OCR/training_data/training_data/annotations"
images_root   = r"C:/Study/Deep Learning/OCR/training_data/training_data/images"

img_h      = 67
img_w      = 400
batch_size = 16
time_steps = 100
epochs     = 300
initial_lr = 1e-4

# ========== 2. Đọc nhãn ==========
label_dict = {}
for fn in os.listdir(labels_folder):
    if not fn.lower().endswith(".txt"):
        continue
    with open(os.path.join(labels_folder, fn), "r", encoding="utf-8") as f:
        for line in f:
            parts = line.replace(",", " ", 1).split(" ", 1)
            if len(parts) < 2:
                continue
            img_name, txt = parts[0].strip(), parts[1].strip()
            full_img_path = os.path.join(
                images_root,
                img_name.replace("\\", "/").split(".jpg")[0] + ".jpg"
            )
            label_dict[full_img_path] = txt
print("Đã đọc nhãn cho", len(label_dict), "ảnh.")

# ========== 3. Bộ ký tự & hàm mã hóa ==========
characters  = (
   "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪĐÊỀẾỆỂỄÔỒỐỘỔỖƠỜỚỢỞỠƯỪỨỰỬỮÝỲỴỶỸ"
    "abcdefghijklmnopqrstuvwxyzàáạảãăằắặẳẵâầấậẩẫđêềếệểễôồốộổỗơờớợởỡưừứựửữýỳỵỷỹ"
    "0123456789,.-/ "
)
char_to_num = {c: i for i, c in enumerate(characters)}
num_to_char = {i: c for c, i in char_to_num.items()}

def preprocess_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Không mở được ảnh: {path}")
    img = cv2.resize(img, (img_w, img_h))
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=-1)

def encode_label(s):
    return [char_to_num[c] for c in s if c in char_to_num]

# ========== 4. Tạo tf.data.Dataset ==========
def gen():
    for path, txt in label_dict.items():
        img = preprocess_image(path)
        lab = np.array(encode_label(txt), dtype=np.int32)
        il  = np.array([time_steps], dtype=np.float32)
        ll  = np.array([len(lab)], dtype=np.float32)
        yield {
            "image_input":  img,
            "the_labels":   lab,
            "input_length": il,
            "label_length": ll
        }, np.zeros((1,), dtype="float32")

ds = tf.data.Dataset.from_generator(
    gen,
    output_signature=(
        {
            "image_input":  tf.TensorSpec((img_h, img_w, 1), tf.float32),
            "the_labels":   tf.TensorSpec((None,),       tf.int32),
            "input_length": tf.TensorSpec((1,),          tf.float32),
            "label_length": tf.TensorSpec((1,),          tf.float32),
        },
        tf.TensorSpec((1,), tf.float32),
    )
)

# ========== 5. Lọc & augment ==========
ds = ds.filter(lambda inp, _: tf.shape(inp["the_labels"])[0] > 0)
ds = ds.filter(lambda inp, _: tf.shape(inp["the_labels"])[0] <= time_steps)
def augment(inp, y):
    img = inp["image_input"]
    img = tf.image.random_brightness(img, max_delta=0.1)
    img = tf.image.random_contrast(img, 0.9, 1.1)
    inp["image_input"] = img
    return inp, y
ds = ds.map(augment, num_parallel_calls=tf.data.AUTOTUNE)
ds = ds.repeat()
ds = ds.padded_batch(batch_size).prefetch(tf.data.AUTOTUNE)

# ========== 6. Xây CRNN (predict) ==========
input_img = Input((img_h, img_w, 1), name="image_input")
x = Conv2D(64,(3,3),padding="same")(input_img)
x = BatchNormalization()(x); x = Activation("relu")(x)
x = MaxPooling2D((2,2))(x)

x = Conv2D(128,(3,3),padding="same")(x)
x = BatchNormalization()(x); x = Activation("relu")(x)
x = MaxPooling2D((2,2))(x)

x = Conv2D(256,(3,3),padding="same")(x)
x = BatchNormalization()(x); x = Activation("relu")(x)
x = MaxPooling2D((2,1),padding="same")(x)

feat_h = img_h // 8
x = Reshape((time_steps, feat_h * 256))(x)
x = Bidirectional(LSTM(128, return_sequences=True, dropout=0.2))(x)
x = Bidirectional(LSTM(128, return_sequences=True, dropout=0.2))(x)
x = Dropout(0.5)(x)

y_pred = Dense(len(char_to_num) + 1, activation="softmax", name="y_pred")(x)
crnn_model = Model(input_img, y_pred, name="crnn_predict")
crnn_model.summary()

# ========== 7. Thêm CTC loss ==========
labels_in = Input(name="the_labels",   shape=(None,), dtype="int32")
in_len    = Input(name="input_length", shape=(1,),    dtype="float32")
lab_len   = Input(name="label_length", shape=(1,),    dtype="float32")

def ctc_loss_fn(args):
    y_p, lbl, il, ll = args
    return K.ctc_batch_cost(lbl, y_p, il, ll)

loss_out = Lambda(ctc_loss_fn, name="ctc_loss")(
    [y_pred, labels_in, in_len, lab_len]
)
crnn_train_model = Model(
    inputs=[input_img, labels_in, in_len, lab_len],
    outputs=loss_out,
    name="crnn_train"
)
opt = Adam(learning_rate=initial_lr)
crnn_train_model.compile(
    optimizer=opt,
    loss={"ctc_loss": lambda y_true, y_pred: y_pred}
)

# ========== 8. Callbacks ==========
callbacks = [
    ReduceLROnPlateau(monitor="loss", factor=0.5, patience=3, min_lr=1e-6),
    EarlyStopping(monitor="loss", patience=10, restore_best_weights=True),
    ModelCheckpoint("best_crnn_2.keras", monitor="loss", save_best_only=True)
]

# ========== 9. Huấn luyện ==========
steps_per_epoch = len(label_dict) // batch_size
crnn_train_model.fit(
    ds,
    epochs=epochs,
    steps_per_epoch=steps_per_epoch,
    callbacks=callbacks
)

# ========== 10. Lưu model dự đoán ==========
crnn_model.save("crnn_predict_2.keras")

# ========== 11. Inference trên batch mẫu ==========
batch_paths = list(label_dict)[:batch_size]
batch = np.stack([preprocess_image(p) for p in batch_paths], axis=0)
pred = crnn_model.predict(batch)  # NumPy array

# sequence_length vector 1-D
seq_len = np.array([pred.shape[1]] * pred.shape[0], dtype=np.int32)

# beam-search decode
decoded, _ = K.ctc_decode(
    pred,
    seq_len,
    greedy=False,
    beam_width=100,
    top_paths=1
)
decoded = decoded[0].numpy()

def decode_seq(seq):
    return "".join(num_to_char[i] for i in seq if i in num_to_char)

print("\n=== Ví dụ kết quả ===")
for i, path in enumerate(batch_paths):
    print("GT:  ", label_dict[path])
    print("Pred:", decode_seq(decoded[i]))
    print("-----")
