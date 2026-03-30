import os
import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path

class SAHIInference:
    def __init__(self, model_path, slice_height=640, slice_width=640, overlap_height_ratio=0.2, overlap_width_ratio=0.2):
        self.model = YOLO(model_path)
        self.slice_height = slice_height
        self.slice_width = slice_width
        self.overlap_height_ratio = overlap_height_ratio
        self.overlap_width_ratio = overlap_width_ratio

    def slice_image(self, image):
        """Slices the image into smaller overlapping patches."""
        h, w = image.shape[:2]
        slices = []
        
        stride_h = int(self.slice_height * (1 - self.overlap_height_ratio))
        stride_w = int(self.slice_width * (1 - self.overlap_width_ratio))
        
        for y in range(0, h, stride_h):
            for x in range(0, w, stride_w):
                y2 = min(y + self.slice_height, h)
                x2 = min(x + self.slice_width, w)
                y1 = max(0, y2 - self.slice_height)
                x1 = max(0, x2 - self.slice_width)
                
                slice_img = image[y1:y2, x1:x2]
                slices.append({
                    'image': slice_img,
                    'x': x1,
                    'y': y1
                })
        return slices

    def predict(self, image_path, conf=0.25):
        """Performs Slicing Aided Hyper Inference."""
        image = cv2.imread(str(image_path))
        if image is None:
            return []
            
        slices = self.slice_image(image)
        all_results = []
        
        print(f"Slicing into {len(slices)} patches...")
        for s in slices:
            results = self.model.predict(s['image'], conf=conf, verbose=False)
            for res in results:
                boxes = res.boxes.data.cpu().numpy() # [x1, y1, x2, y2, conf, cls]
                for box in boxes:
                    # Map back to original image coordinates
                    box[0] += s['x']
                    box[1] += s['y']
                    box[2] += s['x']
                    box[3] += s['y']
                    all_results.append(box)
                    
        return self.non_max_suppression(all_results)

    def non_max_suppression(self, boxes, iou_threshold=0.5):
        """Performs NMS on the aggregated results from all slices."""
        if not boxes:
            return []
            
        boxes = np.array(boxes)
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        scores = boxes[:, 4]
        
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]
        
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            
            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            
            inds = np.where(ovr <= iou_threshold)[0]
            order = order[inds + 1]
            
        return boxes[keep]

if __name__ == "__main__":
    # Example usage
    MODEL = r"e:\New_vision_AI\yolov8_pcb_final.pt"
    if not os.path.exists(MODEL):
        MODEL = "yolov8n.pt"
        
    sahi = SAHIInference(MODEL)
    test_img = r"e:\New_vision_AI\inference_input\test.jpg"
    if os.path.exists(test_img):
        detections = sahi.predict(test_img)
        print(f"Detected {len(detections)} components using SAHI.")
