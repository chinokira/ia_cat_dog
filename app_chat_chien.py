import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import tensorflow as tf

MODEL_PATH_DEFAULT = "8086fb8b-b880-4267-ae13-632b856da3b7.keras"
IMG_SIZE = (224, 224)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IA - Chat vs Chien")
        self.geometry("760x560")
        self.resizable(False, False)

        self.model = None
        self.model_path = tk.StringVar(value=MODEL_PATH_DEFAULT)

        # Mapping labels (peut être modifié)
        self.class0 = tk.StringVar(value="cats")
        self.class1 = tk.StringVar(value="dogs")

        self.image_path = None
        self.preview_imgtk = None

        # Nouveau: mode preprocess
        # auto = essaie brut + preprocess, prend le plus confiant
        self.preprocess_mode = tk.StringVar(value="auto")  # "auto" | "raw" | "mobilenet"

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, padx=10, pady=10)
        top.pack(fill="x")

        tk.Label(top, text="Modèle (.keras) :", width=14, anchor="w").pack(side="left")
        tk.Entry(top, textvariable=self.model_path, width=55).pack(side="left", padx=(0, 8))
        tk.Button(top, text="Choisir…", command=self.choose_model).pack(side="left")
        tk.Button(top, text="Charger", command=self.load_model).pack(side="left", padx=(8, 0))

        mapping = tk.LabelFrame(self, text="Mapping des classes", padx=10, pady=10)
        mapping.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(mapping, text="Sortie = 0  →").grid(row=0, column=0, sticky="w")
        tk.Entry(mapping, textvariable=self.class0, width=12).grid(row=0, column=1, sticky="w", padx=(6, 20))

        tk.Label(mapping, text="Sortie = 1  →").grid(row=0, column=2, sticky="w")
        tk.Entry(mapping, textvariable=self.class1, width=12).grid(row=0, column=3, sticky="w", padx=(6, 20))

        tk.Button(mapping, text="Inverser 0/1", command=self.swap_classes).grid(row=0, column=4, padx=(10, 0))

        # Nouveau: choix preprocess + mode auto
        pp = tk.LabelFrame(self, text="Pré-traitement (anti-bug)", padx=10, pady=10)
        pp.pack(fill="x", padx=10, pady=(0, 10))

        tk.Radiobutton(pp, text="Auto (recommandé)", variable=self.preprocess_mode, value="auto").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(pp, text="Brut (0–255)", variable=self.preprocess_mode, value="raw").grid(row=0, column=1, sticky="w", padx=(15,0))
        tk.Radiobutton(pp, text="MobileNetV2 preprocess", variable=self.preprocess_mode, value="mobilenet").grid(row=0, column=2, sticky="w", padx=(15,0))

        content = tk.Frame(self, padx=10, pady=10)
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, width=440, height=380, bd=1, relief="solid")
        left.pack(side="left", padx=(0, 10))
        left.pack_propagate(False)

        self.preview_label = tk.Label(left, text="Aucune image chargée", fg="gray")
        self.preview_label.pack(fill="both", expand=True)

        right = tk.Frame(content)
        right.pack(side="left", fill="both", expand=True)

        tk.Button(right, text="Choisir une image…", height=2, command=self.choose_image).pack(fill="x")
        tk.Button(right, text="Prédire", height=2, command=self.predict).pack(fill="x", pady=(8, 0))

        self.result_title = tk.Label(right, text="Résultat :", font=("Arial", 12, "bold"))
        self.result_title.pack(anchor="w", pady=(18, 6))

        self.result_label = tk.Label(right, text="—", font=("Arial", 20))
        self.result_label.pack(anchor="w")

        self.proba_label = tk.Label(right, text="", font=("Arial", 11), fg="gray")
        self.proba_label.pack(anchor="w", pady=(6, 0))

        # Nouveau: debug (pour voir raw vs preprocess)
        self.debug_label = tk.Label(right, text="", font=("Consolas", 10), fg="gray", justify="left")
        self.debug_label.pack(anchor="w", pady=(10, 0))

        self.status = tk.StringVar(value="Charge le modèle puis choisis une image.")
        tk.Label(self, textvariable=self.status, anchor="w", padx=10, pady=6, fg="gray").pack(fill="x")

    def swap_classes(self):
        c0, c1 = self.class0.get(), self.class1.get()
        self.class0.set(c1)
        self.class1.set(c0)

    def choose_model(self):
        path = filedialog.askopenfilename(
            title="Choisir le modèle .keras",
            filetypes=[("Keras model", "*.keras"), ("All files", "*.*")]
        )
        if path:
            self.model_path.set(path)

    def load_model(self):
        path = self.model_path.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Erreur", "Chemin du modèle invalide.")
            return

        try:
            self.status.set("Chargement du modèle…")
            self.update_idletasks()
            self.model = tf.keras.models.load_model(path)
            self.status.set(f"Modèle chargé: {os.path.basename(path)}")
            self.debug_label.config(text="")
        except Exception as e:
            self.model = None
            messagebox.showerror("Erreur chargement modèle", str(e))
            self.status.set("Échec du chargement du modèle.")

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return

        try:
            img = Image.open(path).convert("RGB")
            preview = img.copy()
            preview.thumbnail((430, 370))
            self.preview_imgtk = ImageTk.PhotoImage(preview)
            self.preview_label.config(image=self.preview_imgtk, text="")
            self.image_path = path

            self.result_label.config(text="—")
            self.proba_label.config(text="")
            self.debug_label.config(text="")
            self.status.set(f"Image chargée: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Erreur image", str(e))

    def _predict_sigmoid(self, arr_4d: np.ndarray) -> float:
        """Retourne proba classe 1 (sigmoid)"""
        out = self.model.predict(arr_4d, verbose=0)
        return float(np.array(out).reshape(-1)[0])

    def predict(self):
        if self.model is None:
            messagebox.showwarning("Modèle non chargé", "Clique sur 'Charger' pour charger le modèle.")
            return
        if not self.image_path:
            messagebox.showwarning("Aucune image", "Choisis une image d'abord.")
            return

        try:
            # Charge image -> array float32
            img = tf.keras.utils.load_img(self.image_path, target_size=IMG_SIZE)
            arr = tf.keras.utils.img_to_array(img).astype(np.float32)
            arr = np.expand_dims(arr, axis=0)  # (1, H, W, 3)

            c0 = self.class0.get().strip() or "class0"
            c1 = self.class1.get().strip() or "class1"
            classes = [c0, c1]

            mode = self.preprocess_mode.get()

            # A) prédiction brute
            p_raw = self._predict_sigmoid(arr)

            # B) prédiction preprocess mobilenet
            arr_m = tf.keras.applications.mobilenet_v2.preprocess_input(arr.copy())
            p_mob = self._predict_sigmoid(arr_m)

            # Choix
            if mode == "raw":
                p = p_raw
                chosen = "RAW"
            elif mode == "mobilenet":
                p = p_mob
                chosen = "MOBILENET"
            else:
                # AUTO: prend celle qui est la plus "certaine" (distance à 0.5 max)
                conf_raw = abs(p_raw - 0.5)
                conf_mob = abs(p_mob - 0.5)
                if conf_mob > conf_raw:
                    p = p_mob
                    chosen = "AUTO → MOBILENET"
                else:
                    p = p_raw
                    chosen = "AUTO → RAW"

            pred_idx = 1 if p >= 0.5 else 0
            self.result_label.config(text=f"{classes[pred_idx]}")
            self.proba_label.config(text=f"p({classes[1]}) = {p:.3f}   |   seuil=0.5   |   mode={chosen}")

            # Debug visible : te montre si un des deux modes part en vrille
            self.debug_label.config(
                text=(
                    f"Debug:\n"
                    f"- p_class1 RAW      = {p_raw:.4f}\n"
                    f"- p_class1 MOBILENET= {p_mob:.4f}\n"
                    f"  (auto choisit la plus confiante)"
                )
            )

            self.status.set("Prédiction terminée.")

        except Exception as e:
            messagebox.showerror("Erreur prédiction", str(e))
            self.status.set("Échec de la prédiction.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
