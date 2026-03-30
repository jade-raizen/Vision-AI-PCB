import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI\datasets").resolve()
OUTPUT_DIR = Path(r"e:\New_vision_AI\datasets\all_pcb_yolo").resolve()

CLASS_MAP = {
    "open": 0, "short": 1, "mousebite": 2, "spur": 3, "copper": 4, "pin-hole": 5,
    "resistor": 6, "capacitor": 7, "inductor": 8, "diode": 9, "led": 10, "ic": 11,
    "transistor": 12, "connector": 13, "jumper": 14, "emi_filter": 15, "button": 16
}

def main():
    print("--- Unifying All PCB Datasets to YOLO (Robust V2) ---")
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    
    for d in ["images/train", "images/val", "labels/train", "labels/val"]:
        (OUTPUT_DIR / d).mkdir(parents=True, exist_ok=True)

    # 1. DeepPCB
    dp_root = BASE_DIR / "deep_pcb" / "PCBData"
    count = 0
    if dp_root.exists():
        for root, dirs, files in os.walk(dp_root):
            for file in files:
                if file.lower().endswith("_test.jpg"):
                    img_p = Path(root) / file
                    # Label is in a folder suffixed with _not (sibling to the image folder)
                    # or in the same folder.
                    # Image path: group00041/00041/00041000_test.jpg
                    # Label path: group00041/00041_not/00041000.txt
                    
                    parent = img_p.parent.name
                    grandparent = img_p.parent.parent
                    label_dir = grandparent / (parent + "_not")
                    label_name = file.replace("_test.jpg", ".txt")
                    label_p = label_dir / label_name
                    
                    if not label_p.exists():
                        # Fallback: same folder
                        label_p = img_p.with_suffix(".txt")
                    
                    if label_p.exists():
                        with open(label_p, 'r') as f:
                            lines = f.readlines()
                        yolo_lines = []
                        for line in lines:
                            parts = line.strip().replace(',', ' ').split()
                            if len(parts) >= 5:
                                try:
                                    x1, y1, x2, y2, t = map(float, parts[:5])
                                    bw, bh = abs(x2-x1)/640, abs(y2-y1)/640
                                    cx, cy = (x1+x2)/1280, (y1+y2)/1280
                                    yolo_lines.append(f"{int(t)-1} {cx} {cy} {bw} {bh}")
                                except: continue
                        
                        if yolo_lines:
                            split = "train" if hash(file) % 10 < 9 else "val"
                            shutil.copy(img_p, OUTPUT_DIR / "images" / split / file)
                            with open(OUTPUT_DIR / "labels" / split / file.replace(".jpg", ".txt"), "w") as f:
                                f.write("\n".join(yolo_lines))
                            count += 1
    
    print(f"DeepPCB: {count} images processed.")

    # 2. WACV
    count_wacv = 0
    wacv_dir = BASE_DIR / "pcb_wacv_2019_old"
    if wacv_dir.exists():
        img_dir = wacv_dir / "images"
        ann_dir = wacv_dir / "annotations"
        if img_dir.exists() and ann_dir.exists():
            for img_p in img_dir.glob("*.jpg"):
                ann_p = ann_dir / (img_p.stem + ".xml")
                if ann_p.exists():
                    try:
                        tree = ET.parse(ann_p)
                        root = tree.getroot()
                        size = root.find('size')
                        w, h = int(size.find('width').text), int(size.find('height').text)
                        labels = []
                        for obj in root.findall('object'):
                            name = obj.find('name').text.lower()
                            cls_id = CLASS_MAP.get(name, 6) # Map to component if unknown
                            xmlbox = obj.find('bndbox')
                            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), 
                                 float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                            bw, bh = (b[1]-b[0])/w, (b[3]-b[2])/h
                            cx, cy = (b[0]+b[1])/(2*w), (b[2]+b[3])/(2*h)
                            labels.append(f"{cls_id} {cx} {cy} {bw} {bh}")
                        
                        if labels:
                            split = "train" if hash(img_p.name) % 10 < 9 else "val"
                            shutil.copy(img_p, OUTPUT_DIR / "images" / split / img_p.name)
                            with open(OUTPUT_DIR / "labels" / split / (img_p.stem + ".txt"), "w") as f:
                                f.write("\n".join(labels))
                            count_wacv += 1
                    except: continue
    
    print(f"WACV: {count_wacv} images processed.")

    # Create YAML
    with open(OUTPUT_DIR / "dataset.yaml", "w") as f:
        f.write(f"path: {OUTPUT_DIR}\ntrain: images/train\nval: images/val\n\nnames:\n")
        rev_map = {v: k for k, v in CLASS_MAP.items()}
        for i in range(max(rev_map.keys()) + 1):
            f.write(f"  {i}: {rev_map.get(i, 'component')}\n")

if __name__ == "__main__":
    main()
