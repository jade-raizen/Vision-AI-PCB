import os
import shutil
import zipfile
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
DATASETS_DIR = BASE_DIR / "datasets"

def zip_directory(directory_path, output_path):
    """Zips a directory."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 
                                           os.path.join(directory_path, '..')))

def prepare_for_cloud():
    print("--- Preparing Datasets for Cloud Training (Colab/Kaggle) ---")
    
    # 1. Consolidate into ZIPs for easier upload
    for dataset_folder in DATASETS_DIR.iterdir():
        if dataset_folder.is_dir():
            zip_name = dataset_folder.with_suffix(".zip")
            if not zip_name.exists():
                print(f"Zipping {dataset_folder.name}...")
                zip_directory(dataset_folder, zip_name)
    
    print("\nCloud Preparation Complete!")
    print(f"You can now upload the .zip files from {DATASETS_DIR} to your cloud storage.")

def main():
    # Example: Move existing data if not already there
    # (This is a simplified version, real logic depends on where users put their raw files)
    wacv_src = BASE_DIR / "pcb_wacv_2019"
    wacv_dst = DATASETS_DIR / "pcb_wacv_2019"
    
    if wacv_src.exists() and not (wacv_dst / "images").exists():
        print(f"Consolidating {wacv_src.name}...")
        # Simple copy example
        # shutil.copytree(wacv_src, wacv_dst, dirs_exist_ok=True)
    
    prepare_for_cloud()

if __name__ == "__main__":
    main()
