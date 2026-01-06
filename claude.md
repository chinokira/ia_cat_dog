# Projet: Classification Chat vs Chien avec IA

## Vue d'ensemble
Projet d'intelligence artificielle pour classifier des images de chats et de chiens utilisant TensorFlow et MobileNetV2.

## Structure du projet

```
cat_and_dog_ia/
├── data/
│   └── train/              # Dataset d'entraînement (cats/ et dogs/)
├── main.py                 # Script d'entraînement du modèle
├── app_chat_chien.py       # Interface graphique Tkinter pour prédiction
├── cat_dog_model.keras     # Modèle entraîné (24.6 MB)
├── requirements.txt        # Dépendances Python
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration Docker
├── .dockerignore           # Fichiers exclus de Docker
├── claude.md               # Documentation du projet
└── README.md               # Documentation utilisateur complète
```

## Composants principaux

### 1. main.py - Entraînement du modèle
**Architecture:**
- Modèle de base: MobileNetV2 (pré-entraîné sur ImageNet)
- Transfer learning en 2 phases:
  1. Entraînement de la tête (5 epochs)
  2. Fine-tuning des dernières couches (8 epochs, à partir couche 100)

**Configuration:**
- Taille d'image: 224x224 pixels
- Batch size: 64
- Split: 80% train / 10% validation / 10% test
- Augmentation de données: flip horizontal, rotation (0.08), zoom (0.15)

**Fonctionnalités clés:**
- Validation et nettoyage automatique du dataset (suppression images corrompues/vides)
- Early stopping (patience=3)
- ModelCheckpoint (sauvegarde meilleur modèle)
- Évaluation avec métriques: loss, accuracy, AUC
- Matrice de confusion avec visualisation

**Optimisateurs:**
- Phase 1: Adam (lr=1e-3)
- Phase 2 (fine-tuning): Adam (lr=1e-5)

### 2. app_chat_chien.py - Interface de prédiction
**Interface graphique (Tkinter):**
- Fenêtre 760x560 pixels
- Prévisualisation d'image (430x370)
- Sélection de modèle .keras
- Configuration mapping classes (0=cats, 1=dogs)

**Modes de pré-traitement:**
1. **Auto (recommandé)**: Compare prédiction brute vs MobileNetV2 preprocess, prend la plus confiante
2. **RAW**: Pixels bruts 0-255
3. **MobileNetV2 preprocess**: Normalisation spécifique MobileNet

**Affichage:**
- Résultat de prédiction
- Probabilité classe 1 avec seuil (0.5)
- Debug: affiche p(class1) pour RAW et MOBILENET

**Fonctionnalités:**
- Bouton "Inverser 0/1" pour swap classes
- Support formats: jpg, jpeg, png, bmp, gif
- Barre de statut pour feedback utilisateur

## Workflow typique

### Mode local:

1. **Entraînement:**
   ```bash
   python main.py
   ```
   - Nettoie le dataset
   - Entraîne le modèle
   - Sauvegarde `cat_dog_model.keras`
   - Affiche matrice de confusion

2. **Prédiction:**
   ```bash
   python app_chat_chien.py
   ```
   - Charger le modèle .keras
   - Sélectionner une image
   - Cliquer "Prédire"
   - Visualiser résultat + debug info

### Mode Docker:

1. **Build de l'image:**
   ```bash
   docker-compose build
   ```

2. **Entraînement:**
   ```bash
   docker-compose --profile train up
   ```
   - Utilise le volume ./data pour le dataset
   - Sauvegarde le modèle dans ./cat_dog_model.keras

3. **Application GUI (Linux):**
   ```bash
   xhost +local:docker
   docker-compose --profile app up
   ```
   - Nécessite X11 forwarding
   - Sur Windows: utiliser VcXsrv ou WSL2 avec X server

## État actuel du projet

### Git status:
- Branche: `main`
- Fichiers stagés:
  - Configuration PyCharm (.idea/*)
  - claude.md (ce fichier)
- Commits récents:
  - `025584dd` - init
  - `900fefb4` - first commit

### Fichiers principaux:
- ✅ main.py (211 lignes) - Script d'entraînement complet
- ✅ app_chat_chien.py (225 lignes) - Interface GUI avec mode auto anti-bug
- ✅ cat_dog_model.keras (24.6 MB) - Modèle entraîné
- ✅ data/train/ - Dataset organisé
- ✅ requirements.txt - Dépendances Python (tensorflow, numpy, matplotlib, Pillow)
- ✅ Dockerfile - Configuration Docker (Python 3.10-slim + tkinter)
- ✅ docker-compose.yml - Orchestration avec profiles (train, app)
- ✅ .dockerignore - Exclusions Docker (.git, .venv, .idea, etc.)
- ✅ README.md - Documentation complète pour utilisateurs

## Améliorations possibles

1. **Modèle:**
   - Tester d'autres architectures (EfficientNet, ResNet)
   - Augmenter epochs si dataset plus grand
   - Ajuster learning rates

2. **Interface:**
   - Batch prediction (plusieurs images)
   - Historique prédictions
   - Export résultats CSV

3. **Dataset:**
   - Augmenter taille dataset
   - Validation croisée k-fold
   - Classes supplémentaires

4. **Déploiement:**
   - API REST (Flask/FastAPI)
   - ✅ Conteneurisation Docker (complété)
   - Version web (Streamlit)
   - Déploiement cloud (AWS, GCP, Azure)

## Notes techniques

- TensorFlow utilisé (pas PyTorch)
- Classification binaire (sigmoid output)
- Label mode: binary (0 ou 1)
- Système de debug intégré dans l'app pour diagnostiquer problèmes de preprocessing
- Mode AUTO résout problèmes d'incohérence entre preprocessing brut et MobileNet

## Containerisation Docker

### Configuration:
- **Image de base**: python:3.10-slim
- **Dépendances système**: python3-tk, libgl1-mesa-glx, libglib2.0-0
- **Port exposé**: 8080 (pour future API)
- **Volumes**:
  - ./data:/app/data (dataset)
  - ./cat_dog_model.keras:/app/cat_dog_model.keras (modèle)

### Profiles Docker Compose:
1. **train**: Entraînement du modèle
   ```bash
   docker-compose --profile train up
   ```

2. **app**: Interface graphique (nécessite X11)
   ```bash
   xhost +local:docker
   docker-compose --profile app up
   ```

### Notes Docker:
- L'interface GUI nécessite X11 forwarding sur Linux
- Sur Windows: utiliser VcXsrv ou WSL2 avec serveur X
- Le modèle et le dataset persistent via volumes montés
- Build optimisé avec .dockerignore (exclut .git, .venv, .idea)

## Dépendances principales
- tensorflow>=2.14.0
- numpy>=1.24.0
- matplotlib>=3.7.0
- Pillow>=10.0.0
- tkinter (standard library)

---
**Dernière mise à jour:** 2026-01-06
