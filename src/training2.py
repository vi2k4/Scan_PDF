import os
import cv2
import numpy as np
import string
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Conv2D, BatchNormalization, Activation, MaxPooling2D,
    Reshape, Bidirectional, LSTM, Dense, Dropout
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    ReduceLROnPlateau, EarlyStopping, ModelCheckpoint
)

# ========= 1. Cấu hình đường dẫn & tham số =========
labels_folder = r"C:/Study/Deep Learning/OCR/training_data/training_data/annotations"
images_root   = r"C:/Study/Deep Learning/OCR/training_data/training_data/images"

img_h      = 67
img_w      = 400
batch_size = 16
time_steps = 100
epochs     = 200
initial_lr = 1e-4

# ========= 2. Đọc nhãn =========
label_dict = {}
for fn in os.listdir(labels_folder):
    if not fn.lower().endswith(".txt"):
        continue
    with open(os.path.join(labels_folder, fn), "r", encoding="utf-8") as f:
        for line in f:
            parts = line.replace(",", " ", 1).split(" ", 1)
            if len(parts) < 2: continue
            img_name, txt = parts[0].strip(), parts[1].strip()
            full_img_path = os.path.join(
                images_root,
                img_name.replace("\\", "/").split(".jpg")[0] + ".jpg"
            )
            label_dict[full_img_path] = txt
print("Đã đọc nhãn cho", len(label_dict), "ảnh.")

# ========= 3. Chuẩn bị bộ ký tự và encoder =========
characters = (
   "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪĐÊỀẾỆỂỄÔỒỐỘỔỖƠỜỚỢỞỠƯỪỨỰỬỮÝỲỴỶỸ"
   "abcdefghijklmnopqrstuvwxyzàáạảãăằắặẳẵâầấậẩẫđêềếệểễôồốộổỗơờớợởỡưừứựửữýỳỵỷỹ"
   "0123456789,.-/ "
)
char_to_num = {c:i for i,c in enumerate(characters)}
num_to_char = {i:c for c,i in char_to_num.items()}
num_classes = len(characters) + 1  # +1 cho blank

def preprocess_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Không mở được ảnh: {path}")
    img = cv2.resize(img, (img_w, img_h))
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=-1)

def encode_label(s):
    return [char_to_num[c] for c in s if c in char_to_num]

# ========= 4. Tạo tf.data.Dataset =========
def gen():
    for path, txt in label_dict.items():
        lab = encode_label(txt)
        if len(lab)==0 or len(lab) > time_steps:
            continue
        img = preprocess_image(path)
        il = time_steps
        ll = len(lab)
        yield (
            {
                "image_input": img,
                "the_labels":  np.array(lab, dtype=np.int32),
                "input_length": np.array(il, dtype=np.int32),
                "label_length": np.array(ll, dtype=np.int32)
            },
            np.zeros((1,), dtype="float32")
        )

ds = tf.data.Dataset.from_generator(
    gen,
    output_signature=(
        {
            "image_input":   tf.TensorSpec((img_h, img_w, 1), tf.float32),
            "the_labels":    tf.TensorSpec((None,),       tf.int32),
            "input_length":  tf.TensorSpec((),            tf.int32),
            "label_length":  tf.TensorSpec((),            tf.int32),
        },
        tf.TensorSpec((1,), tf.float32)
    )
)

# ========== 5. Lọc & augment ==========
# bỏ các nhãn trống / quá dài
ds = ds.filter(lambda inp, _: tf.shape(inp["the_labels"])[0] > 0)
ds = ds.filter(lambda inp, _: tf.shape(inp["the_labels"])[0] <= time_steps)

# hàm augment
def augment(inp, y):
    img = inp["image_input"]
    img = tf.image.random_brightness(img, max_delta=0.1)
    img = tf.image.random_contrast(img, lower=0.9, upper=1.1)
    inp["image_input"] = img
    return inp, y

# áp dụng augment, rồi padded_batch/phrefetch
ds = ds.map(augment, num_parallel_calls=tf.data.AUTOTUNE)
ds = ds.repeat()
ds = ds.padded_batch(batch_size).prefetch(tf.data.AUTOTUNE)


# ========= 5. Xây dựng CRNN (predict) =========
inp = Input((img_h, img_w, 1), name="image_input")
x = Conv2D(64,3,padding="same")(inp); x = BatchNormalization()(x); x = Activation("relu")(x)
x = MaxPooling2D(2,2)(x)
x = Conv2D(128,3,padding="same")(x); x = BatchNormalization()(x); x = Activation("relu")(x)
x = MaxPooling2D(2,2)(x)
x = Conv2D(256,3,padding="same")(x); x = BatchNormalization()(x); x = Activation("relu")(x)
x = MaxPooling2D((2,1),padding="same")(x)
feat_h = img_h // 8
x = Reshape((time_steps, feat_h*256))(x)
x = Bidirectional(LSTM(128, return_sequences=True, dropout=0.2))(x)
x = Bidirectional(LSTM(128, return_sequences=True, dropout=0.2))(x)
x = Dropout(0.5)(x)
y_pred = Dense(num_classes, activation="softmax", name="y_pred")(x)
crnn_predict = Model(inp, y_pred, name="crnn_predict")
crnn_predict.summary()

# ========= 6. Tạo lớp Model tùy chỉnh để tính CTC loss =========
class CRNNTrainer(Model):
    def __init__(self, crnn):
        super().__init__()
        self.crnn = crnn

    def compile(self, optimizer):
        super().compile()
        self.optimizer = optimizer

    def train_step(self, data):
        x, _ = data
        images      = x["image_input"]
        labels      = x["the_labels"]
        input_len   = x["input_length"]
        label_len   = x["label_length"]
        with tf.GradientTape() as tape:
            y_pred = self.crnn(images, training=True)
            # ctc_batch_cost trả về shape (batch,)
            ctc_loss = K.ctc_batch_cost(labels, y_pred, input_len, label_len)
            loss = tf.reduce_mean(ctc_loss)
        grads = tape.gradient(loss, self.crnn.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.crnn.trainable_variables))
        return {"loss": loss}

# ========= 7. Instantiate và compile =========
trainer = CRNNTrainer(crnn_predict)
trainer.compile(optimizer=Adam(initial_lr))

# ========= 8. Callbacks =========
callbacks = [
    ReduceLROnPlateau(monitor="loss", factor=0.5, patience=3, min_lr=1e-6),
    EarlyStopping(monitor="loss", patience=10, restore_best_weights=True),
    ModelCheckpoint("best_crnn.keras", monitor="loss", save_best_only=True)
]

# ========= 9. Huấn luyện =========
steps_per_epoch = sum(1 for _ in gen()) // batch_size
trainer.fit(ds, epochs=epochs, steps_per_epoch=steps_per_epoch, callbacks=callbacks)

# ========= 10. Lưu model dự đoán =========
crnn_predict.save("crnn_predict_final.keras")
