# MEMOIR.MD - PCB AI Reverse Engineering

## Project Overview
This project aims to use AI (YOLOv8 and FiftyOne) to recognize electronic components on PCBs and eventually generate KiCad files.

## Current State (2026-03-12)
- Project files are located in `e:\New_vision_AI`.
- Dataset directories: `pcb_wacv_2019` and `pcb_wacv_2019_formatted`.
- Model: `yolo26s.pt` exists in the folder.
- `VisionIA.py` is configured for YOLOv8 classification.

## Configuration Fixes
- Hardcoded paths to `C:\Users\machouri\Desktop\...` in `VisionIA.py` and `pcb_data.yaml` need to be updated to `e:\New_vision_AI\...`.

## Development Notes
- Interface used: **FiftyOne**.
- Model architecture: **YOLOv8 Object Detection** (Training on full PCB images).
- Dataset: YOLO format generated from Pascal VOC XML annotations.

## Research & Data Alternatives (Step 1.18)
To improve detection accuracy beyond the WACV 2019 dataset, I recommend the following sources:
- **Kaggle**: "PCB Component Detection Consolidated Dataset" (Consolidated labels, YOLO format).
- **Roboflow**: "ElectroCom61" (61 classes of electronic components).
- **GitHub**: "PCBA-Dataset" (4,000 images for defect and component detection).
- **Scraping Idea**: Use the `selenium` or `playwright` tools to scrape "DigiKey" or "Mouser" for high-resolution component images paired with their dimensions to help KiCad generation.

## Task Log
- [x] Corrected hardcoded Desktop paths.
- [x] Converted XML annotations to YOLO format (`extract_labels.py`).
- [x] Updated `VisionIA.py` for full object detection.
