import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# CONFIG
# =========================
DATA_DIR = "data/train"
IMG_SIZE = (224, 224)
BATCH_SIZE = 64
SEED = 123
EPOCHS_HEAD = 5
EPOCHS_FT = 8
MODEL_OUT = "cat_dog_model.keras"

# =========================
# HELPER: Clean dataset
# =========================
def validate_and_clean_dataset(data_dir):
    """Remove empty or corrupted image files."""
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    removed_count = 0
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = Path(root) / file
            
            # Skip non-image files
            if file_path.suffix.lower() not in valid_extensions:
                print(f"Skipping non-image file: {file_path}")
                continue
            
            # Check if file is empty or corrupted
            try:
                if file_path.stat().st_size == 0:
                    print(f"Removing empty file: {file_path}")
                    file_path.unlink()
                    removed_count += 1
                    continue
                
                # Try to load the image to verify it's valid
                img = tf.io.read_file(str(file_path))
                tf.image.decode_image(img, channels=3)
                
            except Exception as e:
                print(f"Removing corrupted file: {file_path} - Error: {e}")
                try:
                    file_path.unlink()
                    removed_count += 1
                except:
                    pass
    
    print(f"\n✓ Dataset validation complete. Removed {removed_count} problematic files.\n")

# Clean the dataset first
validate_and_clean_dataset(DATA_DIR)

# =========================
# DATASETS (train/val/test)
# =========================
# 80% train, 10% val, 10% test via 2 splits:
# 1) train (80%) + tmp (20%)
# 2) tmp => val (10%) + test (10%)

train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
)

tmp_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
)

class_names = train_ds.class_names
print("Classes:", class_names)

# Split tmp into val/test (half/half)
tmp_batches = tmp_ds.cardinality().numpy()
val_batches = tmp_batches // 2

val_ds = tmp_ds.take(val_batches)
test_ds = tmp_ds.skip(val_batches)

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.shuffle(2000, seed=SEED).prefetch(AUTOTUNE)
val_ds = val_ds.prefetch(AUTOTUNE)
test_ds = test_ds.prefetch(AUTOTUNE)

# =========================
# MODEL (MobileNetV2)
# =========================
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.08),
    tf.keras.layers.RandomZoom(0.15),
], name="aug")

base = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,
    weights="imagenet",
)
base.trainable = False

inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = data_augmentation(inputs)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = base(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.25)(x)
outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

model = tf.keras.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),
    loss="binary_crossentropy",
    metrics=[tf.keras.metrics.BinaryAccuracy(name="acc"), tf.keras.metrics.AUC(name="auc")],
)

model.summary()

# =========================
# TRAIN - HEAD
# =========================
callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint(MODEL_OUT, save_best_only=True),
]

hist1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_HEAD,
    callbacks=callbacks
)

# =========================
# FINE-TUNING
# =========================
base.trainable = True

# On "gèle" les premières couches et on fine-tune les dernières
fine_tune_at = 100
for layer in base.layers[:fine_tune_at]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss="binary_crossentropy",
    metrics=[tf.keras.metrics.BinaryAccuracy(name="acc"), tf.keras.metrics.AUC(name="auc")],
)

hist2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_FT,
    callbacks=callbacks
)

model.save(MODEL_OUT)
print(f"\n✓ Model saved to: {MODEL_OUT}")

# =========================
# EVALUATION (test)
# =========================
test_loss, test_acc, test_auc = model.evaluate(test_ds, verbose=1)
print(f"\nTEST  loss={test_loss:.4f}  acc={test_acc:.4f}  auc={test_auc:.4f}")

# =========================
# CONFUSION MATRIX
# =========================
y_true = []
y_pred = []

for x_batch, y_batch in test_ds:
    probs = model.predict(x_batch, verbose=0).reshape(-1)
    preds = (probs >= 0.5).astype(np.int32)
    y_pred.extend(preds.tolist())
    y_true.extend(y_batch.numpy().astype(np.int32).reshape(-1).tolist())

y_true = np.array(y_true)
y_pred = np.array(y_pred)

cm = tf.math.confusion_matrix(y_true, y_pred, num_classes=2).numpy()
print("\nConfusion matrix (rows=true, cols=pred):\n", cm)

plt.figure()
plt.imshow(cm)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.xticks([0, 1], [class_names[0], class_names[1]])
plt.yticks([0, 1], [class_names[0], class_names[1]])
for (i, j), v in np.ndenumerate(cm):
    plt.text(j, i, str(v), ha="center", va="center")
plt.show()
