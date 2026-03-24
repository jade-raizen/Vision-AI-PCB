# 🔬 Vision-AI: Automated PCB Component Detection & Reverse Engineering

<p align="center">
  <b>An end-to-end AI pipeline for detecting and classifying electronic components on Printed Circuit Boards</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?logo=yolo&logoColor=white" alt="YOLOv8">
  <img src="https://img.shields.io/badge/FiftyOne-Voxel51-orange?logo=data:image/svg+xml;base64,..." alt="FiftyOne">
  <img src="https://img.shields.io/badge/Selenium-Scraping-43B02A?logo=selenium&logoColor=white" alt="Selenium">
</p>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Dataset Pipeline](#-dataset-pipeline)
- [Training & Inference](#-training--inference)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Results](#-results)
- [Future Work](#-future-work)

---

## 🎯 Project Overview

This project addresses the challenge of **automated PCB reverse engineering** — the ability to photograph a circuit board and automatically identify every electronic component on it (resistors, capacitors, ICs, transistors, etc.).

The system combines:
- **Deep Learning** (YOLOv8 object detection) for real-time component detection
- **Automated Data Acquisition** (web scraping from Octopart, LCSC, Google Images) to continuously expand the training dataset
- **Data Curation** (FiftyOne) for visual inspection and quality control of annotations

> **R&D Context**: This project was developed as part of an engineering research initiative to explore the feasibility of fully automated PCB analysis, from component detection to eventual schematic generation (KiCad).

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **20-Class Detection** | Detects resistors, capacitors, ICs, transistors, diodes, LEDs, connectors, and 13 more component types |
| 🤖 **Automated Dataset Expansion** | Web scrapers automatically collect component images from Octopart, LCSC, and Google |
| 📊 **Visual Data Curation** | FiftyOne integration for interactive dataset inspection |
| 🔄 **End-to-End Pipeline** | Single command runs scraping → label extraction → training |
| ⚡ **Real-Time Inference** | Trained model runs inference on new PCB images |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA ACQUISITION                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Octopart │  │   LCSC   │  │   Google Images      │  │
│  │ Scraper  │  │ Scraper  │  │   Scraper            │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
│       └──────────────┼───────────────────┘              │
│                      ▼                                   │
│            scraped_components/                           │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  DATA PROCESSING                         │
│  ┌───────────────┐    ┌──────────────────────────────┐  │
│  │ XML → YOLO    │    │  FiftyOne Visual Inspection   │  │
│  │ Converter     │    │  (Quality Control)            │  │
│  └───────┬───────┘    └──────────────────────────────┘  │
│          ▼                                               │
│     yolo_dataset/                                        │
│     ├── images/train/  (37 annotated PCB boards)        │
│     ├── images/val/                                      │
│     ├── labels/train/                                    │
│     └── labels/val/                                      │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    TRAINING                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  YOLOv8n (Ultralytics)                           │   │
│  │  • 50 epochs, 640px input                        │   │
│  │  • 20-class PCB component detection              │   │
│  │  • Output: yolov8_pcb_final.pt                   │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   INFERENCE                              │
│  Input: PCB photograph → Output: Detected components    │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Detection Model** | YOLOv8 (Ultralytics) | Real-time object detection |
| **Data Curation** | FiftyOne (Voxel51) | Dataset visualization & QC |
| **Web Scraping** | Selenium + Stealth | Automated image collection |
| **Annotation Format** | Pascal VOC XML → YOLO | Label conversion pipeline |
| **Language** | Python 3.10+ | Core development |

---

## 📦 Dataset Pipeline

### Source Data
- **WACV 2019 PCB Dataset**: Academic dataset with XML annotations for PCB components
- **ElectroCom61**: 61-class electronic component dataset from Roboflow
- **Web Scraped Data**: Automated collection from Octopart, LCSC, and Google Images

### Supported Component Classes (20)

| ID | Class | ID | Class | ID | Class | ID | Class |
|----|-------|----|-------|----|-------|----|-------|
| 0 | Resistor | 5 | IC | 10 | Button | 15 | Fuse |
| 1 | Capacitor | 6 | Transistor | 11 | Clock | 16 | Ferrite Bead |
| 2 | Inductor | 7 | Connector | 12 | Transformer | 17 | Buzzer |
| 3 | Diode | 8 | Jumper | 13 | Potentiometer | 18 | Display |
| 4 | LED | 9 | EMI Filter | 14 | Heatsink | 19 | Battery |

### Automated Scraping

The project includes three specialized scrapers:

1. **`scraper_octopart.py`** — Octopart.com (component distributor aggregator)
2. **`scraper_pro.py`** — LCSC + Google Images (with package template fallback)
3. **`scraper_simple.py`** — Lightweight Google Images scraper

Each scraper uses anti-detection techniques (stealth Selenium, realistic user agents, human-like delays) to reliably collect training data.

---

## 🚀 Training & Inference

### Full Pipeline (Recommended)
```bash
python run_pipeline.py
```
This runs: **Scraping → Label Extraction → Training** in sequence.

### Individual Steps

```bash
# 1. Scrape component images from Octopart
python scraper_octopart.py

# 2. Extract & convert annotations to YOLO format
python extract_labels.py

# 3. Train the model
python VisionIA.py

# 4. Run inference on new PCB images
python inference.py
```

### Training Configuration
```yaml
Model: YOLOv8n (nano — optimized for speed)
Epochs: 50
Image Size: 640×640
Classes: 20
```

---

## 📁 Project Structure

```
New_vision_AI/
├── VisionIA.py              # Main training script (YOLOv8 + FiftyOne)
├── run_pipeline.py           # End-to-end pipeline orchestrator
├── extract_labels.py         # XML → YOLO format converter
├── inference.py              # Run detection on new images
├── pcb_data.yaml             # Dataset configuration (20 classes)
│
├── scraper_octopart.py       # Octopart.com image scraper
├── scraper_pro.py            # LCSC + Google Images scraper
├── scraper_simple.py         # Lightweight Google scraper
│
├── yolo_dataset/             # Formatted training data
│   ├── images/{train,val}/
│   └── labels/{train,val}/
│
├── pcb_wacv_2019/            # Raw academic dataset
├── scraped_components/       # Web-scraped component images
├── package_templates/        # Generic package reference images
├── inference_input/          # Input folder for inference
└── runs/                     # Training run outputs
```

---

## 🏃 Getting Started

### Prerequisites
```bash
pip install ultralytics fiftyone selenium webdriver-manager requests beautifulsoup4
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/<your-username>/Vision-AI-PCB.git
cd Vision-AI-PCB

# Run the full pipeline
python run_pipeline.py

# Or run inference on an existing model
python inference.py
```

---

## 📈 Results

> *Training metrics and detection examples will be added after the next training run.*

The model is designed to detect components at various scales on full PCB images, from small 0402 SMD resistors to large QFP ICs.

---

## 🔮 Future Work

- [ ] **KiCad Integration**: Automatically generate schematic files from detected components
- [ ] **Component Value Reading**: OCR for reading component values (resistance, capacitance)
- [ ] **BOM Generation**: Automatic Bill of Materials from a PCB photograph
- [ ] **3D Model Matching**: Match detected components to 3D CAD models
- [ ] **Multi-Layer Detection**: Detect components on both sides of a PCB

---

## 📄 License

This project is developed for research and educational purposes.

## 👤 Author

**Engineering R&D Project** — Automated PCB Analysis using Computer Vision and Deep Learning.
