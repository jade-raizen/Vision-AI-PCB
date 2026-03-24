import os
import cv2
from ultralytics import YOLO
from pathlib import Path

# --- CONFIGURATION ---
MODEL_PATH = r"e:\New_vision_AI\yolov8_pcb_final.pt"
# Fallback to base model if final isn't trained yet
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "yolov8n.pt"

INPUT_DIR = Path(r"e:\New_vision_AI\inference_input")
OUTPUT_DIR = Path(r"e:\New_vision_AI\inference_results")

def run_inference():
    print(f"Loading model: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    image_files = list(INPUT_DIR.glob("*.jpg")) + list(INPUT_DIR.glob("*.png"))
    if not image_files:
        print(f"No images found in {INPUT_DIR}. Please add some images to analyze.")
        return

    print(f"Processing {len(image_files)} images...")
    results = model.predict(source=str(INPUT_DIR), save=True, project=str(OUTPUT_DIR), name="results")
    
    print(f"Inference complete. Results saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    run_inference()
