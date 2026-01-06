"""
API FastAPI pour la classification d'images avec modèle TensorFlow.
Architecture extensible pour supporter plusieurs classes dynamiquement.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from typing import List, Dict
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cat & Dog Classifier API",
    description="API de classification d'images utilisant MobileNetV2",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du modèle
MODEL_PATH = "cat_dog_model.keras"
IMG_SIZE = 224

# Mapping des classes (extensible)
# Format: {index: nom_classe}
# Pour ajouter des classes, il faudra réentraîner le modèle
CLASS_NAMES = {
    0: "cat",
    1: "dog"
}

# Chargement du modèle au démarrage
model = None

@app.on_event("startup")
async def load_model():
    """Charge le modèle TensorFlow au démarrage de l'application."""
    global model
    try:
        logger.info(f"Chargement du modèle depuis {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Modèle chargé avec succès!")
        logger.info(f"Classes supportées: {CLASS_NAMES}")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle: {e}")
        raise


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Prétraite l'image pour la prédiction.

    Args:
        image_bytes: Bytes de l'image uploadée

    Returns:
        Image prétraitée sous forme de numpy array
    """
    try:
        # Ouvrir l'image avec PIL
        image = Image.open(io.BytesIO(image_bytes))

        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Redimensionner à la taille attendue par le modèle
        image = image.resize((IMG_SIZE, IMG_SIZE))

        # Convertir en array numpy
        img_array = np.array(image)

        # Ajouter la dimension batch
        img_array = np.expand_dims(img_array, axis=0)

        # Normalisation MobileNetV2
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

        return img_array
    except Exception as e:
        logger.error(f"Erreur lors du prétraitement de l'image: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur de traitement de l'image: {str(e)}")


def interpret_prediction(prediction: np.ndarray) -> Dict:
    """
    Interprète la prédiction du modèle de manière extensible.

    Args:
        prediction: Array de prédictions du modèle

    Returns:
        Dictionnaire avec la classe prédite et les scores pour toutes les classes
    """
    # Pour un modèle binaire (sigmoid), on obtient une seule valeur
    if prediction.shape[-1] == 1:
        prob_class_1 = float(prediction[0][0])
        prob_class_0 = 1.0 - prob_class_1

        scores = {
            CLASS_NAMES[0]: prob_class_0,
            CLASS_NAMES[1]: prob_class_1
        }

        predicted_class_idx = 1 if prob_class_1 > 0.5 else 0

    # Pour un modèle multi-classe (softmax), on obtient plusieurs valeurs
    else:
        scores = {
            CLASS_NAMES[i]: float(prediction[0][i])
            for i in range(len(CLASS_NAMES))
        }
        predicted_class_idx = int(np.argmax(prediction[0]))

    predicted_class = CLASS_NAMES[predicted_class_idx]
    confidence = scores[predicted_class]

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "all_scores": scores
    }


@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API."""
    return {
        "message": "Cat & Dog Classifier API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "classes": "/classes",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API et du modèle."""
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")

    return {
        "status": "healthy",
        "model_loaded": True,
        "supported_classes": list(CLASS_NAMES.values())
    }


@app.get("/classes")
async def get_classes():
    """Retourne la liste des classes supportées par le modèle."""
    return {
        "classes": CLASS_NAMES,
        "count": len(CLASS_NAMES)
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Effectue une prédiction sur l'image uploadée.

    Args:
        file: Fichier image uploadé

    Returns:
        Prédiction avec classe, confiance et scores détaillés
    """
    # Vérifier que le modèle est chargé
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")

    # Vérifier le type de fichier
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image (jpg, png, etc.)"
        )

    try:
        # Lire le contenu du fichier
        contents = await file.read()
        logger.info(f"Image reçue: {file.filename}, taille: {len(contents)} bytes")

        # Prétraiter l'image
        processed_image = preprocess_image(contents)

        # Effectuer la prédiction
        prediction = model.predict(processed_image, verbose=0)

        # Interpréter les résultats
        result = interpret_prediction(prediction)

        logger.info(f"Prédiction: {result['predicted_class']} (confiance: {result['confidence']:.2%})")

        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "prediction": result
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
