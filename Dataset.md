# Dataset.MD

**Vision-AI-PCB – Datasets for PCB Component Detection, Trace Detection, and Reverse Engineering**

---

# Overview

This document lists **all datasets used in the Vision-AI-PCB project**.
The objective is to gather a **large-scale dataset (~120,000 images)** allowing training of AI models for:

* PCB component detection
* PCB defect detection
* PCB trace segmentation
* OCR of component markings
* reverse engineering of electronic boards

The datasets come from **academic research**, **open industrial inspection datasets**, and **automatically scraped component images**.

---

# Dataset Summary

| Dataset                             | Purpose                   | Images  |
| ----------------------------------- | ------------------------- | ------- |
| PCB Component Detection (WACV 2019) | Component detection       | ~1,400  |
| DeepPCB                             | PCB defect detection      | ~3,000  |
| PCB Defect Dataset                  | AOI defect classification | ~1,300  |
| FPIC Dataset                        | Semantic segmentation     | ~10,000 |
| PCB Kaggle Dataset                  | Component detection       | ~1,400  |
| PCB DSLR Dataset                    | IC detection              | ~748    |
| PCB-METAL Dataset                   | Industrial inspection     | ~5,000  |
| PCB-Vision Dataset                  | RGB + hyperspectral PCB   | ~2,000  |
| Scraped Component Images            | Component classification  | ~80,000 |
| Open Hardware PCB Images            | PCB topology detection    | ~20,000 |

Estimated total:

```
~120,000 images
```

---

# 1. PCB Component Detection Dataset (WACV 2019)

Official project page:

https://sites.google.com/view/chiawen-kuo/home/pcb-component-detection

This dataset is widely used for **PCB component detection research**.

Paper:

Data-Efficient Graph Embedding Learning for PCB Component Detection

Content:

* ~1400 images
* ~11,000 component instances
* annotations in XML format

Component classes include:

```
resistor
capacitor
inductor
diode
transistor
IC
connector
switch
transformer
```

Typical structure:

```
pcb_wacv_2019
   images
   annotations
```

Annotations are provided in **Pascal VOC XML format**.

---

# 2. DeepPCB Dataset

GitHub repository:

https://github.com/tangsanli5201/DeepPCB

Paper:

DeepPCB: A Dataset for PCB Defect Detection

Content:

* 1500 pairs of images
* defect-free PCB
* defective PCB

Defect categories:

```
open circuit
short circuit
mouse bite
spur
spurious copper
missing hole
```

Typical usage:

* defect detection
* segmentation
* CNN training for AOI systems.

---

# 3. PCB Defect Dataset (Huang & Wei)

Paper:

https://arxiv.org/abs/1901.08204

Dataset description:

Synthetic dataset used for **industrial PCB inspection research**.

Content:

* 1386 images
* 6 defect classes

Defect types:

```
missing hole
mouse bite
open circuit
short
spur
spurious copper
```

---

# 4. FPIC Dataset

GitHub repository:

https://github.com/AsadizanjaniLab/FPIC

Paper:

FPIC: A Novel Semantic Dataset for Optical PCB Assurance

Content:

* several thousand images
* semantic segmentation masks
* component-level labeling

Use cases:

* component segmentation
* PCB inspection
* automated optical inspection systems.

---

# 5. Kaggle PCB Component Dataset

Dataset page:

https://www.kaggle.com/datasets/animeshkumarnayak/pcb-fault-detection

Content:

* ~1410 images
* bounding box annotations
* multiple component categories.

Used for:

```
YOLO
FasterRCNN
SSD
```

training.

---

# 6. PCB DSLR Dataset

Research dataset:

https://research.tuwien.ac.at/en/publications/a-dataset-for-computer-vision-based-pcb-analysis

Content:

* 748 images
* 9313 IC components

Focus:

* IC detection
* segmentation of PCB structures.

---

# 7. PCB-METAL Dataset

Research dataset:

https://www.researchgate.net/publication/334427584_PCB-METAL_A_PCB_Image_Dataset_for_Advanced_Computer_Vision_Machine_Learning_Component_Analysis

Content:

* high resolution PCB inspection images
* industrial manufacturing samples.

Use cases:

* component classification
* automated inspection.

---

# 8. PCB-Vision Dataset

GitHub repository:

https://github.com/hifexplo/PCBVision

Paper:

PCB-Vision: RGB-Hyperspectral PCB Dataset

Content:

* RGB images
* hyperspectral PCB images
* segmentation labels.

Applications:

* material identification
* copper trace analysis.

---

# 9. Scraped Electronic Component Images

Large dataset collected automatically from:

```
Octopart
DigiKey
Mouser
LCSC
```

Images include:

```
SMD resistors
capacitors
IC packages
connectors
transistors
MOSFETs
inductors
```

Estimated size:

```
80,000 images
```

Metadata includes:

```
manufacturer
part number
package
datasheet
```

---

# 10. Open Hardware PCB Images

Sources:

```
GitHub electronics projects
Open hardware repositories
KiCad example projects
Arduino projects
```

Collected images include:

```
PCB top layer
PCB bottom layer
assembled boards
bare PCBs
```

Estimated size:

```
20,000 images
```

---

# Final Combined Dataset

| Source                   | Images  |
| ------------------------ | ------- |
| Academic PCB datasets    | ~18,000 |
| Component scraping       | ~80,000 |
| Open hardware PCB images | ~20,000 |

Total estimated dataset size:

```
≈118,000 images
```

Approximate storage size:

```
30-60 GB
```

---

# Dataset Usage in the Project

The dataset will be used for training multiple AI models:

### Component Detection

Model:

```
YOLOv8
YOLOv11
```

Purpose:

```
detect components on PCB
```

---

### Trace Detection

Model:

```
U-Net
SegFormer
Mask-RCNN
```

Purpose:

```
detect copper traces
vias
pads
```

---

### Reverse Engineering

Pipeline:

```
PCB Image
→ component detection
→ trace segmentation
→ graph construction
→ netlist generation
→ KiCad PCB reconstruction
```

---

# Dataset Storage Layout

Recommended project structure:

```
datasets
│
├── pcb_wacv_2019       (Academic, ~600MB) [STATUS: OK]
├── deep_pcb             (1500 pairs, ~150MB) [STATUS: OK]
├── pku_defect           (Tiny-Defect, ~50MB) [STATUS: OK]
├── pcba_dataset         (Industrial, ~5GB) [STATUS: OK]
├── pcb_bank             (Consolidated, ~1GB) [STATUS: OK]
├── pcb_vision           (RGB/HSI, ~5MB repo) [STATUS: LFS limited]
├── fpic_dataset         (20GB Figshare) [STATUS: MANUEL REQUIS]
├── scraped_components
└── open_hardware_pcbs
```

---

# References

Academic references used in this project:

```
DeepPCB dataset
FPIC dataset
PCB Component Detection (WACV)
PCB-Vision dataset
PCB-METAL dataset
```

These datasets are commonly used in **industrial automated optical inspection research** and **PCB computer vision studies**.

---

# Notes for Future Dataset Expansion

Additional dataset sources may include:

```
electronics manufacturing inspection datasets
AOI industrial datasets
semiconductor inspection datasets
PCB assembly datasets
```

Future improvements:

* annotate PCB traces
* annotate vias
* annotate pads
* annotate component footprints
* create netlist ground truth

These annotations will enable **full PCB reverse engineering using AI**.
