# Utiliser une image Python officielle avec support des librairies scientifiques
FROM python:3.10-slim

# Installer les dépendances système nécessaires pour OpenCV et tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers du projet
COPY main.py .
COPY app_chat_chien.py .
COPY cat_dog_model.keras .
COPY data/ ./data/

# Exposer le port si nécessaire (pour future API REST)
EXPOSE 8080

# Variable d'environnement pour désactiver le buffering Python
ENV PYTHONUNBUFFERED=1

# Commande par défaut (peut être surchargée)
CMD ["python", "app_chat_chien.py"]
