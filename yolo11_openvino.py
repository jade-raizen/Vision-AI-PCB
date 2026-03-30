import os
from ultralytics import YOLO
import cv2
from pathlib import Path

class YOLO11OpenVINO:
    def __init__(self, model_variant="yolo11n.pt", task="detect"):
        """
        Initialize YOLO11 with OpenVINO optimization.
        model_variant: yolo11n, yolo11s, yolo11m, yolo11l, yolo11x
        """
        self.model_variant = model_variant
        self.ov_model_path = Path(model_variant).with_suffix(".ov.xml") # OpenVINO exported path format
        self.model = None
        self.task = task
        
    def load_model(self):
        """Load YOLO11 model and export to OpenVINO if not already done."""
        print(f"--- Loading YOLO11 Variant: {self.model_variant} ---")
        self.model = YOLO(self.model_variant)
        
        # Check if OpenVINO model already exists (folder check because export creates a folder)
        ov_folder = Path(self.model_variant.replace(".pt", "_openvino_model"))
        
        if not ov_folder.exists():
            print("Optimizing model for OpenVINO (CPU)...")
            # Export to OpenVINO format
            self.model.export(format="openvino")
            print(f"Model exported to {ov_folder}")
        
        # Reload the optimized model
        print("Loading optimized OpenVINO model...")
        self.model = YOLO(str(ov_folder), task=self.task)
        
    def predict(self, source, imgsz=640, conf=0.25, save=True, project="inference_results", name="yolo11_ov"):
        """Perform inference using OpenVINO optimized model."""
        if self.model is None:
            self.load_model()
            
        print(f"Running inference on {source} with OpenVINO...")
        results = self.model.predict(
            source=source,
            imgsz=imgsz,
            conf=conf,
            save=save,
            project=project,
            name=name
        )
        return results

if __name__ == "__main__":
    # Example usage
    ov_engine = YOLO11OpenVINO("yolo11n.pt")
    
    # Test on a single image if exists
    test_image = r"e:\New_vision_AI\inference_input\test.jpg"
    if os.path.exists(test_image):
        ov_engine.predict(test_image)
    else:
        print("No test image found at e:\\New_vision_AI\\inference_input\\test.jpg")
        print("Run with: python yolo11_openvino.py --source <path>")
