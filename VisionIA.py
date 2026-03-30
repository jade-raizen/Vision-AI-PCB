import os
import fiftyone as fo
import fiftyone.zoo as foz
from ultralytics import YOLO
from app_logger import logger

# --- 1. CONFIGURATION DES CHEMINS ---
data_dir = r"e:\New_vision_AI\datasets\all_pcb_yolo"
yaml_path = r"e:\New_vision_AI\datasets\all_pcb_yolo\dataset.yaml"
dataset_name = "pcb-full-detection"
USE_YOLO11 = True  # Set to True to use YOLO11, False for YOLOv8
MODEL_VARIANT = "yolo11n.pt" # yolo11n, yolo11s, etc.

def main():
    # --- 2. CHARGEMENT DANS FIFTYONE ---
    if dataset_name in fo.list_datasets():
        fo.delete_dataset(dataset_name)

    logger.info(f"Importation du dataset YOLO depuis : {data_dir}")
    dataset = fo.Dataset.from_dir(
        dataset_dir=data_dir,
        dataset_type=fo.types.YOLOv5Dataset, # YOLOv8/v5 uses the same structure in FiftyOne
        name=dataset_name,
    )
    dataset.persistent = True
    
    # Lancement de l'interface pour vérifier les boîtes englobantes
    session = fo.launch_app(dataset)
    print("Interface FiftyOne lancée sur http://localhost:5151")

    # --- 3. ENTRAÎNEMENT DU MODÈLE (YOLO DETECTION) ---
    logger.info(f"Début de l'entraînement de détection avec {'YOLO11' if USE_YOLO11 else 'YOLOv8'}...")
    
    if USE_YOLO11:
        model = YOLO(MODEL_VARIANT)
        model_name = "yolo11_pcb"
        final_model_name = "yolo11_pcb_final.pt"
    else:
        model = YOLO('yolov8_pcb_final.pt') if os.path.exists('yolov8_pcb_final.pt') else YOLO('yolov8n.pt')
        model_name = "yolov8_pcb"
        final_model_name = "yolov8_pcb_final.pt"

    model.train(
        data=os.path.abspath(yaml_path), 
        epochs=10,          #50# Augmenté pour la détection qui est plus complexe
        imgsz=1080,          #640# Taille augmentée pour voir les petits composants
        plots=True,
        project="pcb_detection_runs",
        name=model_name
    )

    # Sauvegarde du modèle final
    model.save(final_model_name)
    print(f"Entraînement terminé ! Modèle de détection sauvegardé sous : {final_model_name}")

    # Garder l'interface FiftyOne ouverte
    session.wait()

if __name__ == "__main__":
    main()
