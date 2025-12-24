"""
Service for working with ML model for soil classification
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import json
import numpy as np
from PIL import Image
from pathlib import Path
import tensorflow as tf
from typing import Optional

from app.schemas.soil import SoilPrediction


class SoilMLService:
    """Service for soil classification using trained ML model"""

    def __init__(self):
        self.model: Optional[tf.keras.Model] = None
        self.class_mapping: Optional[dict] = None
        self.model_path = Path("app/ml_model")
        self.img_height = 224
        self.img_width = 224

    def load_model(self):
        """Load the trained model and class mapping"""
        if self.model is None:
            model_file = self.model_path / "best_model.keras"
            if not model_file.exists():
                model_file = self.model_path / "soil_classifier.keras"

            self.model = tf.keras.models.load_model(str(model_file))

            # Load class mapping
            with open(self.model_path / "class_mapping.json", "r", encoding="utf-8") as f:
                self.class_mapping = json.load(f)

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model prediction

        Args:
            image_path: Path to the image file

        Returns:
            Preprocessed image array
        """
        # Load image
        img = Image.open(image_path)

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Resize
        img = img.resize((self.img_width, self.img_height))

        # Convert to array and normalize
        img_array = np.array(img)
        img_array = img_array / 255.0

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def predict(self, image_path: str) -> SoilPrediction:
        """
        Predict soil type from image

        Args:
            image_path: Path to the soil image

        Returns:
            SoilPrediction with soil type and recommendations
        """
        # Load model if not loaded
        if self.model is None:
            self.load_model()

        # Preprocess image
        img_array = self.preprocess_image(image_path)

        # Make prediction
        predictions = self.model.predict(img_array, verbose=0)

        # Get predicted class and confidence
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])

        # Get class name
        class_names = self.class_mapping["class_names"]
        predicted_soil_type = class_names[predicted_class_idx]

        # Get soil information
        soil_info = self.class_mapping["soil_info"][predicted_soil_type]

        return SoilPrediction(
            soil_type=predicted_soil_type,
            confidence=confidence,
            description=soil_info["description"],
            characteristics=soil_info["characteristics"],
            recommended_crops=soil_info["crops"],
            recommendations=soil_info["recommendations"]
        )


# Singleton instance
_ml_service_instance: Optional[SoilMLService] = None


def get_ml_service() -> SoilMLService:
    """Get singleton instance of ML service"""
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = SoilMLService()
    return _ml_service_instance
