"""
Vision-AI PCB Detection — Web Interface
========================================
Flask-based dashboard for managing the PCB component detection pipeline:
  - Dashboard with system overview
  - Scraping Manager (add sites, run scrapers)
  - Model Manager (upload, list, train)
  - Inference (upload PCB image → detect components)
  - Space Qualification Checker (verify rad-hard / MIL-STD compliance)

Usage:
    python app.py
    → Open http://localhost:5000
"""

import os
import sys
import json
import time
import glob
import shutil
import threading
import subprocess
from pathlib import Path
from datetime import datetime

from flask import (Flask, render_template, request, redirect, url_for,
                   jsonify, flash, send_from_directory)

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
DATASET_DIR = BASE_DIR / "yolo_dataset"
SCRAPED_DIR = BASE_DIR / "scraped_components"
MODELS_DIR = BASE_DIR / "models"
UPLOAD_DIR = BASE_DIR / "uploads"
INFERENCE_INPUT = BASE_DIR / "inference_input"
INFERENCE_OUTPUT = BASE_DIR / "inference_output"
CONFIG_FILE = BASE_DIR / "app_config.json"

# Ensure directories exist
for d in [MODELS_DIR, UPLOAD_DIR, INFERENCE_INPUT, INFERENCE_OUTPUT, SCRAPED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"),
            static_folder=str(BASE_DIR / "static"))
app.secret_key = "vision-ai-pcb-2026"
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max upload

# --- GLOBAL STATE ---
training_status = {
    "running": False,
    "progress": 0,
    "epoch": 0,
    "total_epochs": 50,
    "log": [],
    "model_path": None,
    "started_at": None
}

scraping_status = {
    "running": False,
    "site": None,
    "images_found": 0,
    "log": []
}


def load_config():
    """Load scraping sites and settings from config file."""
    default = {
        "scraping_sites": [
            {"name": "Octopart", "url": "https://octopart.com/fr", "scraper": "scraper_octopart.py", "enabled": True},
            {"name": "LCSC", "url": "https://www.lcsc.com", "scraper": "scraper_pro.py", "enabled": True},
            {"name": "Google Images", "url": "https://images.google.com", "scraper": "scraper_simple.py", "enabled": True}
        ],
        "training": {
            "epochs": 50,
            "imgsz": 640,
            "batch": 16,
            "base_model": "yolov8n.pt"
        },
        "space_qual_keywords": [
            "MIL-STD-883", "ESCC", "QML", "rad-hard", "radiation tolerant",
            "space grade", "hi-rel", "military grade", "JANS", "JAN",
            "QPL", "Class V", "Class K", "MIL-PRF"
        ]
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved = json.load(f)
                default.update(saved)
        except:
            pass
    return default


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_dataset_stats():
    """Count images and labels in the dataset."""
    stats = {"train_images": 0, "val_images": 0, "train_labels": 0, "val_labels": 0, "classes": 0}
    train_img = DATASET_DIR / "images" / "train"
    val_img = DATASET_DIR / "images" / "val"
    train_lbl = DATASET_DIR / "labels" / "train"
    val_lbl = DATASET_DIR / "labels" / "val"

    if train_img.exists():
        stats["train_images"] = len(list(train_img.glob("*.*")))
    if val_img.exists():
        stats["val_images"] = len(list(val_img.glob("*.*")))
    if train_lbl.exists():
        stats["train_labels"] = len(list(train_lbl.glob("*.txt")))
    if val_lbl.exists():
        stats["val_labels"] = len(list(val_lbl.glob("*.txt")))

    yaml_path = BASE_DIR / "pcb_data.yaml"
    if yaml_path.exists():
        with open(yaml_path, 'r') as f:
            for line in f:
                if line.strip().startswith(("0:", "1:", "2:", "3:", "4:", "5:", "6:", "7:", "8:", "9:",
                                            "10:", "11:", "12:", "13:", "14:", "15:", "16:", "17:", "18:", "19:")):
                    stats["classes"] += 1
    return stats


def get_models():
    """List all available .pt model files."""
    models = []
    for pt in BASE_DIR.glob("*.pt"):
        models.append({
            "name": pt.name,
            "path": str(pt),
            "size_mb": round(pt.stat().st_size / (1024 * 1024), 1),
            "modified": datetime.fromtimestamp(pt.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        })
    for pt in MODELS_DIR.glob("*.pt"):
        models.append({
            "name": pt.name,
            "path": str(pt),
            "size_mb": round(pt.stat().st_size / (1024 * 1024), 1),
            "modified": datetime.fromtimestamp(pt.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        })
    return models


def get_scraped_stats():
    """Count scraped images per component type."""
    stats = {}
    if SCRAPED_DIR.exists():
        for folder in SCRAPED_DIR.iterdir():
            if folder.is_dir():
                count = len(list(folder.rglob("*.jpg"))) + len(list(folder.rglob("*.png")))
                if count > 0:
                    stats[folder.name] = count
    return stats


# =============================================================================
# ROUTES
# =============================================================================

@app.route("/")
def dashboard():
    config = load_config()
    stats = get_dataset_stats()
    models = get_models()
    scraped = get_scraped_stats()
    return render_template("index.html",
                           page="dashboard",
                           stats=stats,
                           models=models,
                           scraped=scraped,
                           config=config,
                           training_status=training_status,
                           scraping_status=scraping_status)


@app.route("/scraping")
def scraping_page():
    config = load_config()
    scraped = get_scraped_stats()
    return render_template("index.html",
                           page="scraping",
                           config=config,
                           scraped=scraped,
                           scraping_status=scraping_status)


@app.route("/training")
def training_page():
    config = load_config()
    models = get_models()
    stats = get_dataset_stats()
    return render_template("index.html",
                           page="training",
                           config=config,
                           models=models,
                           stats=stats,
                           training_status=training_status)


@app.route("/inference")
def inference_page():
    models = get_models()
    return render_template("index.html",
                           page="inference",
                           models=models)


@app.route("/space-check")
def space_check_page():
    return render_template("index.html", page="space_check")


# --- API ENDPOINTS ---

@app.route("/api/add-site", methods=["POST"])
def add_site():
    config = load_config()
    name = request.form.get("site_name", "").strip()
    url = request.form.get("site_url", "").strip()
    if name and url:
        config["scraping_sites"].append({
            "name": name, "url": url, "scraper": "custom", "enabled": True
        })
        save_config(config)
        flash(f"Site '{name}' added successfully!", "success")
    return redirect(url_for("scraping_page"))


@app.route("/api/remove-site/<int:idx>")
def remove_site(idx):
    config = load_config()
    if 0 <= idx < len(config["scraping_sites"]):
        removed = config["scraping_sites"].pop(idx)
        save_config(config)
        flash(f"Site '{removed['name']}' removed.", "info")
    return redirect(url_for("scraping_page"))


@app.route("/api/toggle-site/<int:idx>")
def toggle_site(idx):
    config = load_config()
    if 0 <= idx < len(config["scraping_sites"]):
        config["scraping_sites"][idx]["enabled"] = not config["scraping_sites"][idx]["enabled"]
        save_config(config)
    return redirect(url_for("scraping_page"))


@app.route("/api/run-scraper", methods=["POST"])
def run_scraper():
    if scraping_status["running"]:
        return jsonify({"error": "Scraper already running"}), 400

    site_idx = int(request.form.get("site_idx", 0))
    config = load_config()
    site = config["scraping_sites"][site_idx]

    def _run():
        scraping_status["running"] = True
        scraping_status["site"] = site["name"]
        scraping_status["images_found"] = 0
        scraping_status["log"] = [f"Starting scraper for {site['name']}..."]
        try:
            scraper_file = BASE_DIR / site["scraper"]
            if scraper_file.exists():
                proc = subprocess.Popen(
                    [sys.executable, str(scraper_file)],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, cwd=str(BASE_DIR)
                )
                for line in proc.stdout:
                    line = line.strip()
                    if line:
                        scraping_status["log"].append(line)
                        if "saved" in line.lower() or "✅" in line:
                            scraping_status["images_found"] += 1
                proc.wait()
                scraping_status["log"].append(f"Scraper finished with exit code {proc.returncode}")
            else:
                scraping_status["log"].append(f"Scraper file not found: {site['scraper']}")
        except Exception as e:
            scraping_status["log"].append(f"Error: {e}")
        finally:
            scraping_status["running"] = False

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    flash(f"Scraper started for {site['name']}!", "success")
    return redirect(url_for("scraping_page"))


@app.route("/api/upload-model", methods=["POST"])
def upload_model():
    if "model_file" not in request.files:
        flash("No file selected", "error")
        return redirect(url_for("training_page"))

    f = request.files["model_file"]
    if f.filename and f.filename.endswith(".pt"):
        dest = MODELS_DIR / f.filename
        f.save(str(dest))
        flash(f"Model '{f.filename}' uploaded ({dest.stat().st_size // (1024*1024)}MB)", "success")
    else:
        flash("Please upload a .pt model file", "error")
    return redirect(url_for("training_page"))


@app.route("/api/start-training", methods=["POST"])
def start_training():
    if training_status["running"]:
        return jsonify({"error": "Training already in progress"}), 400

    base_model = request.form.get("base_model", "yolov8n.pt")
    epochs = int(request.form.get("epochs", 50))
    imgsz = int(request.form.get("imgsz", 640))

    def _train():
        training_status["running"] = True
        training_status["progress"] = 0
        training_status["epoch"] = 0
        training_status["total_epochs"] = epochs
        training_status["log"] = [f"Starting training with {base_model}, {epochs} epochs, {imgsz}px..."]
        training_status["started_at"] = datetime.now().strftime("%H:%M:%S")

        try:
            yaml_path = str(BASE_DIR / "pcb_data.yaml")
            cmd = [
                sys.executable, "-c",
                f"""
from ultralytics import YOLO
model = YOLO(r'{base_model}')
model.train(data=r'{yaml_path}', epochs={epochs}, imgsz={imgsz}, plots=True,
            project=r'{str(BASE_DIR / "runs")}', name='train_web')
model.save(r'{str(MODELS_DIR / "latest_trained.pt")}')
print('TRAINING_COMPLETE')
"""
            ]
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, cwd=str(BASE_DIR)
            )
            for line in proc.stdout:
                line = line.strip()
                if line:
                    training_status["log"].append(line)
                    # Parse epoch progress
                    if "Epoch" in line or "epoch" in line:
                        try:
                            parts = line.split("/")
                            if len(parts) >= 2:
                                current = int(''.join(filter(str.isdigit, parts[0][-4:])))
                                training_status["epoch"] = current
                                training_status["progress"] = int(100 * current / epochs)
                        except:
                            pass
                    if "TRAINING_COMPLETE" in line:
                        training_status["progress"] = 100
                        training_status["model_path"] = str(MODELS_DIR / "latest_trained.pt")

            proc.wait()
            training_status["log"].append(f"Training finished (exit code: {proc.returncode})")
        except Exception as e:
            training_status["log"].append(f"Error: {e}")
        finally:
            training_status["running"] = False

    thread = threading.Thread(target=_train, daemon=True)
    thread.start()
    flash("Training started!", "success")
    return redirect(url_for("training_page"))


@app.route("/api/run-inference", methods=["POST"])
def run_inference():
    if "pcb_image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    f = request.files["pcb_image"]
    model_name = request.form.get("model", "yolov8_pcb_final.pt")

    if f.filename:
        img_path = INFERENCE_INPUT / f.filename
        f.save(str(img_path))

        try:
            from ultralytics import YOLO

            # Find the model file
            model_path = BASE_DIR / model_name
            if not model_path.exists():
                model_path = MODELS_DIR / model_name
            if not model_path.exists():
                return jsonify({"error": f"Model {model_name} not found"}), 404

            model = YOLO(str(model_path))
            results = model.predict(str(img_path), save=True,
                                    project=str(INFERENCE_OUTPUT), name="web_inference",
                                    exist_ok=True)

            detections = []
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        detections.append({
                            "class_id": cls_id,
                            "class_name": r.names.get(cls_id, f"class_{cls_id}"),
                            "confidence": round(conf, 3),
                            "bbox": [round(x1), round(y1), round(x2), round(y2)]
                        })

            # Get result image path
            result_img = INFERENCE_OUTPUT / "web_inference" / f.filename
            result_img_url = f"/inference-result/{f.filename}" if result_img.exists() else None

            return jsonify({
                "success": True,
                "detections": detections,
                "count": len(detections),
                "result_image": result_img_url
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file"}), 400


@app.route("/inference-result/<filename>")
def inference_result(filename):
    return send_from_directory(str(INFERENCE_OUTPUT / "web_inference"), filename)


@app.route("/api/space-check", methods=["POST"])
def space_check():
    """
    Check if a component is space-qualified by searching Octopart
    and checking for radiation/military keywords in the specs.
    """
    mpn = request.form.get("mpn", "").strip()
    if not mpn:
        return jsonify({"error": "Please provide a part number (MPN)"}), 400

    config = load_config()
    keywords = config.get("space_qual_keywords", [])

    result = {
        "mpn": mpn,
        "status": "unknown",
        "confidence": 0,
        "details": [],
        "octopart_url": f"https://octopart.com/fr/search?q={mpn}",
        "keywords_found": [],
        "specs": {}
    }

    try:
        # Search Octopart via requests (lighter than Selenium for a quick check)
        import requests as req
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Try the Octopart search page
        search_url = f"https://octopart.com/fr/search?q={mpn}"
        resp = req.get(search_url, headers=headers, timeout=10)
        page_text = resp.text.lower()

        # Check for space-grade keywords on the page
        found_keywords = []
        for kw in keywords:
            if kw.lower() in page_text:
                found_keywords.append(kw)

        result["keywords_found"] = found_keywords

        # Known space-grade prefixes
        space_prefixes = ["JANS", "JAN", "5962", "M55342", "M55310",
                          "5905", "5910", "5915", "5920", "5925", "5930",
                          "LM139W", "LM124W", "OP07A"]
        mpn_upper = mpn.upper()
        prefix_matches = [p for p in space_prefixes if mpn_upper.startswith(p)]

        # Decision logic
        score = 0
        if found_keywords:
            score += len(found_keywords) * 15
            result["details"].append(f"Found {len(found_keywords)} space qualification keyword(s) on Octopart")

        if prefix_matches:
            score += 40
            result["details"].append(f"MPN matches space-grade prefix: {', '.join(prefix_matches)}")

        # Check component description patterns
        space_patterns = ["rad hard", "radiation", "space", "military", "hi-rel",
                          "class v", "class k", "-883", "qml", "escc"]
        for pattern in space_patterns:
            if pattern in page_text:
                score += 10
                result["details"].append(f"Found '{pattern}' in component description")

        # Final classification
        if score >= 60:
            result["status"] = "space_qualified"
            result["confidence"] = min(score, 100)
        elif score >= 30:
            result["status"] = "possibly_qualified"
            result["confidence"] = score
        elif score > 0:
            result["status"] = "commercial_with_potential"
            result["confidence"] = score
        else:
            result["status"] = "commercial"
            result["confidence"] = 0
            result["details"].append("No space qualification indicators found")

    except Exception as e:
        result["details"].append(f"Error during check: {str(e)}")
        result["status"] = "error"

    return jsonify(result)


@app.route("/api/training-status")
def get_training_status():
    return jsonify(training_status)


@app.route("/api/scraping-status")
def get_scraping_status():
    return jsonify(scraping_status)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" Vision-AI PCB Detection - Web Interface")
    print(" -> http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
