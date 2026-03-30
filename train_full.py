import os
from ultralytics import YOLO
from pathlib import Path
from app_logger import logger

# --- Configuration ---
YAML_PATH = r"e:\New_vision_AI\datasets\all_pcb_yolo\dataset.yaml"
# Using yolo11n.pt as the pre-trained base
MODEL_BASE = "yolo11n.pt" 
EPOCHS = 5
IMGSZ = 640 

import argparse

def train(epochs=EPOCHS, imgsz=IMGSZ, model_base=MODEL_BASE):
    logger.info(f"--- Démarrage de l'entraînement (CLI Mode) : {epochs} epochs, {imgsz}px ---")
    
    # Init YOLO model
    model = YOLO(model_base)
    
    # Train
    results = model.train(
        data=YAML_PATH,
        epochs=epochs,
        imgsz=imgsz,
        project="pcb_full_train",
        name="full_dataset_run",
        plots=True,
        workers=4, # Use 4 workers for 6 cores
        device="cpu"
    )
    
    logger.info("\n--- Entraînement fini ! ---")
    final_name = "yolo11_pcb_final.pt"
    model.save(final_name)
    logger.info(f"Modèle sauvegardé sous : {final_name}")

    # --- Tentative d'inférence ---
    print("\n--- Test d'inférence sur un échantillon ---")
    # Finding a sample in val/images
    val_images = list(Path(r"e:\New_vision_AI\datasets\yolo_dataset_final\images\val").glob("*.jpg"))
    if val_images:
        sample = val_images[0]
        print(f"Inférence sur : {sample}")
        pred = model.predict(source=str(sample), save=True, project="inference_tests", name="after_train")
        print(f"Résultats d'inférence sauvegardés dans 'inference_tests/after_train'")
    else:
        print("Aucun échantillon trouvé dans val/images pour le test.")

if __name__ == "__main__":
    train()
