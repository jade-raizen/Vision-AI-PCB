import os
import cv2
from ultralytics import YOLO
from pathlib import Path
from yolo11_openvino import YOLO11OpenVINO
from sahi_inference import SAHIInference
from app_logger import logger

# --- CONFIGURATION ---
MODEL_PATH = r"e:\New_vision_AI\yolo11_pcb_final.pt"
YOLO11_MODEL = "yolo11n.pt"
USE_SAHI = True  # Enable for high-res/small object detection

INPUT_DIR = Path(r"e:\New_vision_AI\inference_input")
OUTPUT_DIR = Path(r"e:\New_vision_AI\inference_results")

import argparse

def run_inference(source=None, model=None):
    # Determine source (argument or default)
    src = Path(source) if source else INPUT_DIR
    mdl = model if model else MODEL_PATH
    
    # Check if we should use YOLO11 with OpenVINO (Fallback or High-Res)
    use_ov = False
    
    if not os.path.exists(mdl):
        logger.warning(f"Model {mdl} not found. Switching to YOLO11 + OpenVINO.")
        use_ov = True
    
    # Determine image files
    if src.is_file():
        image_files = [src]
    else:
        image_files = list(src.glob("*.jpg")) + list(src.glob("*.png"))
        
    if not image_files:
        print(f"No images found in {src}.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if use_ov:
        logger.info(f"Loading YOLO11 OpenVINO model: {YOLO11_MODEL}")
        engine = YOLO11OpenVINO(YOLO11_MODEL)
        engine.load_model()
        results = engine.predict(source=str(src), project=str(OUTPUT_DIR), name="results_ov")
    elif USE_SAHI:
        print(f"Using SAHI Inference with model: {mdl}")
        sahi = SAHIInference(mdl)
        for img_path in image_files:
            print(f"Slicing and detecting: {img_path.name}")
            detections = sahi.predict(img_path)
            print(f"Found {len(detections)} components.")
    else:
        print(f"Loading standard YOLO model: {mdl}")
        yolo = YOLO(mdl)
        results = yolo.predict(source=str(src), save=True, project=str(OUTPUT_DIR), name="results")
    
    print(f"Inference complete. Results saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VisionIA - PCB Detection CLI")
    parser.add_argument("--source", help="Path to image or directory")
    parser.add_argument("--model", help="Path to .pt model file")
    args = parser.parse_args()
    
    run_inference(source=args.source, model=args.model)
