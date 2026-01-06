# 🚀 Guide de démarrage - Application Web

Guide rapide pour lancer l'application web de classification Chat vs Chien.

## 📋 Prérequis

- Docker et Docker Compose installés
- Port 3000 (frontend) et 8000 (backend) disponibles

## 🏃 Démarrage rapide avec Docker

### 1. Lancer l'application complète

```bash
docker-compose -f docker-compose.web.yml up --build
```

### 2. Accéder à l'application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentation API (Swagger)**: http://localhost:8000/docs

### 3. Arrêter l'application

```bash
docker-compose -f docker-compose.web.yml down
```

## 🛠️ Développement local (sans Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📡 Endpoints API disponibles

### GET /
Informations sur l'API

### GET /health
Vérification de l'état du serveur et du modèle

### GET /classes
Liste des classes supportées

### POST /predict
Prédiction sur une image
- **Input**: Fichier image (multipart/form-data)
- **Output**: JSON avec prédiction et scores

**Exemple avec curl:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

**Réponse:**
```json
{
  "success": true,
  "filename": "image.jpg",
  "prediction": {
    "predicted_class": "dog",
    "confidence": 0.95,
    "all_scores": {
      "cat": 0.05,
      "dog": 0.95
    }
  }
}
```

## 🎨 Architecture

```
┌─────────────┐      HTTP       ┌──────────────┐
│   Vue.js    │ ────────────▶   │   FastAPI    │
│  Frontend   │                 │   Backend    │
│ (port 3000) │ ◀────────────   │ (port 8000)  │
└─────────────┘     JSON        └──────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │ TensorFlow   │
                                │   Model      │
                                │ (.keras)     │
                                └──────────────┘
```

## 🔧 Configuration

### Variables d'environnement Backend

Aucune configuration requise par défaut.

### Variables d'environnement Frontend

Créer un fichier `.env` dans `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Le frontend ne peut pas se connecter au backend

1. Vérifier que le backend est démarré: `curl http://localhost:8000/health`
2. Vérifier la configuration CORS dans `backend/main.py`
3. Vérifier la variable `VITE_API_URL` dans `frontend/.env`

### Erreur "Modèle non chargé"

1. Vérifier que `cat_dog_model.keras` existe dans `backend/`
2. Vérifier les logs du backend: `docker-compose -f docker-compose.web.yml logs backend`

### Port déjà utilisé

Modifier les ports dans `docker-compose.web.yml`:

```yaml
backend:
  ports:
    - "8001:8000"  # Utiliser le port 8001 au lieu de 8000

frontend:
  ports:
    - "3001:3000"  # Utiliser le port 3001 au lieu de 3000
```

## 📝 Ajouter de nouvelles classes (futur)

Pour supporter plus de 2 classes:

1. **Réentraîner le modèle** avec les nouvelles classes
2. **Mettre à jour `CLASS_NAMES`** dans `backend/main.py`:
   ```python
   CLASS_NAMES = {
       0: "cat",
       1: "dog",
       2: "bird",  # Nouvelle classe
       3: "fish"   # Nouvelle classe
   }
   ```
3. **Mettre à jour le frontend** dans `PredictionResult.vue`:
   ```javascript
   const icons = {
       'cat': '🐱',
       'dog': '🐶',
       'bird': '🐦',  // Nouveau
       'fish': '🐟'   // Nouveau
   }
   ```

## 📚 Ressources

- Documentation FastAPI: https://fastapi.tiangolo.com
- Documentation Vue.js: https://vuejs.org
- Documentation TensorFlow: https://www.tensorflow.org

---
**Version:** 1.0.0
**Dernière mise à jour:** 2026-01-06
