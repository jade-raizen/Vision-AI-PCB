# 🔬 Vision-AI: Automated PCB Component Detection & Reverse Engineering

<p align="center">
  <b>An end-to-end AI pipeline for detecting and classifying electronic components on Printed Circuit Boards</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/YOLO11-Ultralytics-blueviolet?logo=yolo&logoColor=white" alt="YOLO11">
  <img src="https://img.shields.io/badge/OpenVINO-Optimization-0071C5?logo=intel&logoColor=white" alt="OpenVINO">
  <img src="https://img.shields.io/badge/Colab-GPU_Training-F9AB00?logo=googlecolab&logoColor=white" alt="Colab">
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
| 🚀 **YOLO11 & OpenVINO** | Optimized CPU inference for lack of GPU and high-res reverse engineering |
| 🧩 **SAHI Slicing** | Slicing Aided Hyper Inference for detecting tiny 0402 components |
| ⚠️ **Anomaly Detection** | Autoencoder-based inspection for solder joints and traces |
| 🖥️ **Full Web App** | Integrated dashboard for all features, including research bibliographies |

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
│     datasets/all_pcb_yolo/                               │
│     ├── images/train/  (1,421 annotated PCB images)      │
│     ├── images/val/    (147 annotated PCB images)        │
│     ├── labels/train/                                    │
│     └── labels/val/                                      │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    TRAINING                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  • YOLOv8n / YOLO11n (Ultralytics)                     │   │
│  │  • 50 epochs, 640px/1080px input                     │   │
│  │  • 20-class PCB component detection                   │   │
│  │  • Optimization: OpenVINO (CPU fallback)              │   │
│  │  • Output: yolov8_pcb_final.pt / yolo11_pcb_final.pt  │   │
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

Each scraper uses anti-detection techniques (stealth Selenium, realistic user agents, human-like delays). Data is then unified using `unify_all_to_yolo.py` to create a massive 1,500+ image training set from DeepPCB and WACV sources.

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

### ☁️ Cloud Training (Recommended for Speed)
If you don't have a high-end NVIDIA GPU locally, use **Google Colab**:
1. Uploader `datasets/all_pcb_yolo.zip` sur Colab.
2. Suivre le [COLAB_GUIDE.md](./COLAB_GUIDE.md).

### Training Configuration
```yaml
Model: YOLO11n (Next-gen — optimized for small PCB objects)
Epochs: 5 (Fine-tuning) / 50 (Full)
Image Size: 640×640
Dataset: Unified all_pcb_yolo (1,400+ images)
```

---

---

## 💻 Command Line Interface (CLI)

Vous pouvez utiliser les scripts directement depuis votre terminal pour plus de flexibilité.

### 🔍 Inférence (Détection)
Utilisez `inference.py` pour détecter des composants sur une image ou un dossier spécifique.
```bash
# Lancer sur le dossier par défaut (inference_input/)
python inference.py

# Lancer sur une image spécifique
python inference.py --source e:\images\ma_pcb.jpg

# Utiliser un modèle spécifique
python inference.py --source e:\images\test_dir --model runs/detect/train/weights/best.pt
```

### 🚅 Entraînement
Utilisez `train_full.py` pour lancer ou reprendre un entraînement.
```bash
# Lancer l'entraînement par défaut (5 epochs)
python train_full.py

# Personnaliser le nombre d'époques et la taille d'image
python train_full.py --epochs 10 --imgsz 1080
```

### 🔄 Unification du Dataset
Si vous ajoutez manuellement des images dans `datasets/deep_pcb`, relancez l'unification :
```bash
python unify_all_to_yolo.py
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
├── yolo11_openvino.py       # Optimized YOLO11 inference with OpenVINO
├── sahi_inference.py        # Slicing Aided Hyper Inference for small objects
├── defect_analysis.py       # Autoencoder-based anomaly detection
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

---

## 🎨 Interfaces Graphiques (GUI)

Le projet propose deux interfaces complémentaires pour une gestion visuelle du pipeline.

### 1. 🖥️ Dashboard Web (Gestion & Inférence)
Idéal pour piloter l'entraînement, scraper des composants et tester l'inférence via un navigateur.
```bash
python app.py
```
Accédez à : `http://localhost:5000`
- **Dashboard** : Statistiques en temps réel sur le dataset unifié.
- **Scraping** : Interface de contrôle pour les scrapers Octopart/LCSC.
- **Training** : Lancement d'entraînements YOLO11 avec monitoring de progression.
- **Inference** : Upload d'images PCB et visualisation immédiate des détections (avec SAHI/OpenVINO).

### 2. 👁️ Inspection Visuelle (FiftyOne)
Idéal pour vérifier la qualité des annotations et nettoyer le dataset avant l'entraînement.
```bash
python VisionIA.py
```
Accédez à : `http://localhost:5151`
- Visualisation interactive des bounding boxes.
- Filtrage par classe et score de confiance.
- Correction/Suppression d'annotations erronées.

---

## 🏃 Getting Started

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

## 📚 Bibliography & Inspiration (Local Copies in `./inspiration_sources`)

- **PCB Tracer** ([pcb-tracer](./inspiration_sources/pcb-tracer)): Techniques for PCB trace extraction.
- **PCB Fault Detection UI** ([pcb_fault_detection_ui](./inspiration_sources/pcb_fault_detection_ui)): User interface patterns for defect detection.
- **Anomaly Detection for Solder** ([Anomaly-detection-for-solder](./inspiration_sources/Anomaly-detection-for-solder)): Solder joint inspection methods.

## 📄 License

This project is developed for research and educational purposes.

## 👤 Author

**Engineering R&D Project** — Automated PCB Analysis using Computer Vision and Deep Learning.
