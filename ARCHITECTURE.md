# Architecture & R&D Documentation

## 1. Problem Statement

Manual PCB reverse engineering is time-consuming and error-prone. This project explores an automated approach using computer vision to:

1. **Detect** electronic components on a PCB photograph
2. **Classify** each component into one of 20 categories
3. **Locate** components with bounding box coordinates for potential schematic reconstruction

## 2. System Design

### 2.1 Detection Models & Optimization

We mainly use **YOLOv8** and **YOLO11** (Ultralytics) for object detection.

**Model Selection & Hardware Optimization:**
- **YOLOv8**: Base model for standard component detection.
- **YOLO11**: New generation model used for high-resolution images to read tiny SMD markings.
- **OpenVINO (Intel)**: Used to optimize inference on CPUs (local machines without dedicated GPUs).
- **SAHI (Slicing Aided Hyper Inference)**: To overcome the 640px/1024px input limitation of YOLO, we implement image slicing. This allows the model to "see" tiny components (e.g., 0402 resistors) on very large PCB photographs by processing them in overlapping patches.

**Anomaly Detection (R&D):**
- **Autoencoder (AE/VAE)**: Inspired by solder joint research, we use a convolutional autoencoder to learn "normal" PCB textures. Deviations in reconstruction error highlight potential defects (solder bridges, missing traces) without requiring a labeled defect dataset.

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

## 6. Software Stack & Integrations

- **Frontend**: Vanilla HTML5/CSS3 (Glassmorphism design), FontAwesome, Inter typography.
- **Backend**: Flask (Python 3.10+), PyTorch, Ultralytics YOLO.
- **Optimization**: Intel OpenVINO for CPU-accelerated inference.
- **Micro-Detection**: SAHI (Slicing Aided Hyper Inference) for small component detection.
- **Post-Processing**: Convolutional Autoencoders (CAE) for anomaly detection on component patches.

## 7. References

- Ultralytics YOLO11: https://docs.ultralytics.com/
- WACV 2019 PCB Dataset: https://sites.google.com/view/wacv2019-pcb-dataset
- FiftyOne Documentation: https://docs.voxel51.com/
- Local Inspiration Sources: [./inspiration_sources](./inspiration_sources)
  - `pcb-tracer`: Techniques for PCB trace extraction.
  - `pcb_fault_detection_ui`: UI patterns for defect detection.
  - `Anomaly-detection-for-solder`: Solder joint inspection methods.
