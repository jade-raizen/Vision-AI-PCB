# Architecture & R&D Documentation

## 1. Problem Statement

Manual PCB reverse engineering is time-consuming and error-prone. This project explores an automated approach using computer vision to:

1. **Detect** electronic components on a PCB photograph
2. **Classify** each component into one of 20 categories
3. **Locate** components with bounding box coordinates for potential schematic reconstruction

## 2. System Design

### 2.1 Detection Model

We use **YOLOv8** (You Only Look Once, version 8) from Ultralytics — a state-of-the-art single-shot object detector optimized for real-time inference.

**Why YOLOv8?**
- Single-pass architecture (detection + classification in one forward pass)
- Native support for small object detection (critical for SMD components)
- Extensive augmentation pipeline built-in
- Easy export to ONNX/TensorRT for edge deployment

### 2.2 Dataset Strategy

The core R&D challenge is **data acquisition**. Unlike common object categories (cars, people), electronic components have limited publicly available labeled datasets.

**Our multi-source approach:**

| Source | Type | Advantage |
|--------|------|-----------|
| WACV 2019 | Academic | High-quality XML annotations on real PCBs |
| ElectroCom61 | Community | 61 component classes, pre-labeled |
| Octopart | Scraped | Latest product images, real manufacturer photos |
| LCSC | Scraped | Chinese distributor, different component angles |
| Google Images | Scraped | Diverse backgrounds, varied quality |

### 2.3 Automated Data Pipeline

```
Component Catalog (MPN list)
         │
         ▼
  ┌──────────────┐
  │  Web Scraper  │  ← Anti-detection: stealth Selenium, delays, cookie handling
  │  (Octopart,   │
  │   LCSC, etc.) │
  └──────┬───────┘
         ▼
  scraped_components/
  ├── resistor/
  ├── capacitor/
  ├── ic/
  └── ...
         │
         ▼
  ┌──────────────┐
  │  Label        │  ← Pascal VOC XML → YOLO txt format
  │  Converter    │
  └──────┬───────┘
         ▼
  yolo_dataset/
  ├── images/{train,val}/
  └── labels/{train,val}/
         │
         ▼
  ┌──────────────┐
  │  YOLOv8      │  ← 50 epochs, 640px, nano architecture
  │  Training    │
  └──────┬───────┘
         ▼
  yolov8_pcb_final.pt
```

### 2.4 Anti-Bot Techniques

Web scraping electronic component distributors requires bypassing anti-bot protection (PerimeterX, Cloudflare). Our approach:

- **Stealth Selenium**: Override `navigator.webdriver`, disable automation flags
- **Realistic User-Agents**: Mimic a real Chrome browser on Windows
- **Human-like delays**: Randomized wait times between requests (5–10s)
- **Cookie injection**: Pre-set consent cookies to avoid modal interruptions
- **Fallback chain**: If one source fails, the scraper tries the next

## 3. Class Taxonomy

The 20-class taxonomy covers the most common passive and active components found on consumer electronics PCBs:

| Category | Classes |
|----------|---------|
| **Passive** | Resistor, Capacitor, Inductor, Ferrite Bead, Fuse |
| **Semiconductor** | Diode, LED, Transistor, IC |
| **Electromechanical** | Connector, Button, Jumper, Potentiometer |
| **Magnetic** | Transformer, EMI Filter |
| **Thermal** | Heatsink |
| **Timing** | Clock |
| **Output** | Buzzer, Display |
| **Power** | Battery |

## 4. Metrics & Evaluation

The model is evaluated using standard COCO metrics:
- **mAP@0.5**: Mean Average Precision at IoU threshold 0.5
- **mAP@0.5:0.95**: Mean AP averaged over IoU thresholds from 0.5 to 0.95
- **Precision / Recall**: Per-class detection performance

## 5. Challenges & Lessons Learned

1. **Data scarcity**: The biggest bottleneck is annotated PCB data — hence the automated scraping pipeline
2. **Class imbalance**: Some components (resistors, capacitors) are far more common than others (buzzers, displays)
3. **Scale variation**: Components range from tiny 0402 SMDs (< 1mm) to large ICs (> 20mm)
4. **Visual similarity**: Many SMD packages look identical across component types (a 0805 resistor vs. 0805 capacitor)
5. **Anti-bot arms race**: Distributors continuously update their protection, requiring scraper maintenance

## 6. References

- Ultralytics YOLOv8: https://docs.ultralytics.com/
- WACV 2019 PCB Dataset: https://sites.google.com/view/wacv2019-pcb-dataset
- FiftyOne Documentation: https://docs.voxel51.com/
- Octopart API: https://octopart.com/
