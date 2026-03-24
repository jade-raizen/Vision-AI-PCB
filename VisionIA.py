import os
import fiftyone as fo
import fiftyone.zoo as foz
from ultralytics import YOLO

# --- 1. CONFIGURATION DES CHEMINS ---
data_dir = r"e:\New_vision_AI\yolo_dataset"
yaml_path = r"e:\New_vision_AI\pcb_data.yaml"
dataset_name = "pcb-full-detection"

def main():
    # --- 2. CHARGEMENT DANS FIFTYONE ---
    if dataset_name in fo.list_datasets():
        fo.delete_dataset(dataset_name)

    print(f"Importation du dataset YOLO depuis : {data_dir}")
    dataset = fo.Dataset.from_dir(
        dataset_dir=data_dir,
        dataset_type=fo.types.YOLOv5Dataset, # YOLOv8/v5 uses the same structure in FiftyOne
        name=dataset_name,
    )
    dataset.persistent = True
    
    # Lancement de l'interface pour vérifier les boîtes englobantes
    session = fo.launch_app(dataset)
    print("Interface FiftyOne lancée sur http://localhost:5151")

    # --- 3. ENTRAÎNEMENT DU MODÈLE (YOLOv8 Detection) ---
    print("Début de l'entraînement de détection...")
    # 'yolov8n.pt' est le modèle de détection standard
    model = YOLO('yolov8n.pt') 

    model.train(
        data=os.path.abspath(yaml_path), 
        epochs=50,          # Augmenté pour la détection qui est plus complexe
        imgsz=640,          # Taille augmentée pour voir les petits composants
        plots=True,
        project="pcb_detection_runs",
        name="yolov8_pcb"
    )

    # Sauvegarde du modèle final
    model_path = "yolov8_pcb_final.pt"
    model.save(model_path)
    print(f"Entraînement terminé ! Modèle de détection sauvegardé sous : {model_path}")

    # Garder l'interface FiftyOne ouverte
    session.wait()

if __name__ == "__main__":
    main()
