import os
import xml.etree.ElementTree as ET
import shutil
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
SOURCE_DIR = BASE_DIR / "pcb_wacv_2019"
# We avoid nested 'pcb_wacv_2019' if it exists
if (SOURCE_DIR / "pcb_wacv_2019").exists():
    SOURCE_DIR = SOURCE_DIR / "pcb_wacv_2019"

OUTPUT_DIR = BASE_DIR / "yolo_dataset"
CLASS_MAPPING = {
    "resistor": 0,
    "capacitor": 1,
    "inductor": 2,
    "diode": 3,
    "led": 4,
    "ic": 5,
    "transistor": 6,
    "connector": 7,
    "jumper": 8,
    "emi_filter": 9,
    "button": 10,
    "clock": 11,
    "transformer": 12,
    "potentiometer": 13,
    "heatsink": 14,
    "fuse": 15,
    "ferrite_bead": 16,
    "buzzer": 17,
    "display": 18,
    "battery": 19
}

def convert_to_yolo(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    return (x * dw, y * dh, w * dw, h * dh)

def map_name_to_class(name):
    name = name.lower().replace('"', '')
    for key in CLASS_MAPPING:
        if key in name:
            return CLASS_MAPPING[key]
    return None

def process_dataset():
    # Setup folders
    for split in ["train", "val"]:
        (OUTPUT_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

    all_files = []
    for board_folder in SOURCE_DIR.iterdir():
        if not board_folder.is_dir():
            continue
        
        xml_files = list(board_folder.glob("*.xml"))
        for xml_path in xml_files:
            img_path = board_folder / (xml_path.stem + ".jpg")
            if not img_path.exists():
                img_path = board_folder / (xml_path.stem + ".png")
            
            if img_path.exists():
                all_files.append((xml_path, img_path))

    print(f"Found {len(all_files)} boards with annotations.")
    
    # Split 80/20
    split_idx = int(0.8 * len(all_files))
    train_files = all_files[:split_idx]
    val_files = all_files[split_idx:]

    def save_data(files, split):
        for xml_path, img_path in files:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            size = root.find("size")
            w = int(size.find("width").text)
            h = int(size.find("height").text)

            yolo_labels = []
            for obj in root.findall("object"):
                name = obj.find("name").text
                class_id = map_name_to_class(name)
                if class_id is None:
                    continue
                
                xmlbox = obj.find("bndbox")
                b = (float(xmlbox.find("xmin").text), float(xmlbox.find("xmax").text),
                     float(xmlbox.find("ymin").text), float(xmlbox.find("ymax").text))
                bb = convert_to_yolo((w, h), b)
                yolo_labels.append(f"{class_id} " + " ".join([f"{a:.6f}" for a in bb]))

            if yolo_labels:
                # Copy image
                target_img = OUTPUT_DIR / "images" / split / img_path.name
                shutil.copy(img_path, target_img)
                
                # Write labels
                target_label = OUTPUT_DIR / "labels" / split / (xml_path.stem + ".txt")
                with open(target_label, "w") as f:
                    f.write("\n".join(yolo_labels))

    save_data(train_files, "train")
    save_data(val_files, "val")
    print("Done! YOLO dataset created at:", OUTPUT_DIR)

if __name__ == "__main__":
    process_dataset()
