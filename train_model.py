"""
Script to train CNN model for soil classification
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
import json

# Configuration
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32
EPOCHS = 30
DATASET_PATH = Path("Dataset")
MODEL_PATH = Path("app/ml_model")

# Soil types and their descriptions
SOIL_INFO = {
    "Alluvial soil": {
        "description": "Аллювиальная почва - формируется речными отложениями",
        "characteristics": "Плодородная, хорошо дренированная",
        "crops": "Рис, пшеница, сахарный тростник, хлопок",
        "recommendations": "Регулярное орошение, органические удобрения"
    },
    "Black Soil": {
        "description": "Черная почва (чернозем) - богата минералами",
        "characteristics": "Высокое содержание глины, отличная влагоудерживающая способность",
        "crops": "Хлопок, подсолнечник, табак, зерновые",
        "recommendations": "Добавить песок для улучшения дренажа, азотные удобрения"
    },
    "Clay soil": {
        "description": "Глинистая почва - тяжелая, плотная структура",
        "characteristics": "Медленный дренаж, хорошо удерживает питательные вещества",
        "crops": "Капуста, брокколи, бобовые",
        "recommendations": "Добавить компост и органику, улучшить дренаж"
    },
    "Red soil": {
        "description": "Красная почва - содержит оксиды железа",
        "characteristics": "Пористая, хороший дренаж, низкое плодородие",
        "crops": "Арахис, картофель, просо",
        "recommendations": "Органические удобрения, известкование для снижения кислотности"
    }
}


def create_model(num_classes):
    """Create CNN model for soil classification"""
    model = keras.Sequential([
        # Input layer
        layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3)),

        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        # Third convolutional block
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        # Fourth convolutional block
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.3),

        # Flatten and Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])

    return model


def main():
    print("=" * 50)
    print("SOIL CLASSIFICATION MODEL TRAINING")
    print("=" * 50)

    # Create model directory
    MODEL_PATH.mkdir(parents=True, exist_ok=True)

    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        zoom_range=0.2,
        shear_range=0.2,
        fill_mode='nearest'
    )

    # Only rescaling for test data
    test_datagen = ImageDataGenerator(rescale=1./255)

    # Load training data
    print("\nLoading training data...")
    train_generator = train_datagen.flow_from_directory(
        DATASET_PATH / 'Train',
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )

    # Load test data
    print("Loading test data...")
    test_generator = test_datagen.flow_from_directory(
        DATASET_PATH / 'test',
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    # Get class names
    class_names = list(train_generator.class_indices.keys())
    num_classes = len(class_names)

    print(f"\nClasses found: {class_names}")
    print(f"Number of classes: {num_classes}")
    print(f"Training samples: {train_generator.samples}")
    print(f"Test samples: {test_generator.samples}")

    # Save class names
    class_mapping = {
        'class_names': class_names,
        'class_indices': train_generator.class_indices,
        'soil_info': SOIL_INFO
    }

    with open(MODEL_PATH / 'class_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(class_mapping, f, ensure_ascii=False, indent=2)

    print("\nClass mapping saved!")

    # Create model
    print("\nCreating model...")
    model = create_model(num_classes)

    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    print(model.summary())

    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            MODEL_PATH / 'best_model.keras',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    # Train model
    print("\n" + "=" * 50)
    print("STARTING TRAINING")
    print("=" * 50 + "\n")

    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=test_generator,
        callbacks=callbacks,
        verbose=1
    )

    # Evaluate model
    print("\n" + "=" * 50)
    print("EVALUATING MODEL")
    print("=" * 50 + "\n")

    test_loss, test_accuracy = model.evaluate(test_generator, verbose=1)
    print(f"\nTest Accuracy: {test_accuracy * 100:.2f}%")
    print(f"Test Loss: {test_loss:.4f}")

    # Save final model
    print("\nSaving final model...")
    model.save(MODEL_PATH / 'soil_classifier.keras')

    # Save training history
    history_dict = {
        'accuracy': [float(x) for x in history.history['accuracy']],
        'val_accuracy': [float(x) for x in history.history['val_accuracy']],
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']],
        'final_test_accuracy': float(test_accuracy),
        'final_test_loss': float(test_loss)
    }

    with open(MODEL_PATH / 'training_history.json', 'w') as f:
        json.dump(history_dict, f, indent=2)

    print("\n" + "=" * 50)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"\nModel saved to: {MODEL_PATH / 'soil_classifier.keras'}")
    print(f"Best model saved to: {MODEL_PATH / 'best_model.keras'}")
    print(f"Class mapping saved to: {MODEL_PATH / 'class_mapping.json'}")
    print(f"Training history saved to: {MODEL_PATH / 'training_history.json'}")


if __name__ == "__main__":
    main()
