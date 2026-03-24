import subprocess
import os
import sys

def run_step(name, command):
    print(f"\n{'='*20} {name} {'='*20}")
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during {name}: {e}")
        sys.exit(1)

def main():
    # 1. Scraping
    run_step("SCRAPING DATA", "python e:\\New_vision_AI\\scraper.py")
    
    # 2. Extracting labels (optional if only classification images added, 
    # but good to re-run if raw PCB data was added)
    run_step("EXTRACTING LABELS", "python e:\\New_vision_AI\\extract_labels.py")
    
    # 3. Training
    run_step("TRAINING MODEL", "python e:\\New_vision_AI\\VisionIA.py")
    
    print("\n[PIPELINE COMPLETE] Your model is trained and ready for inference!")

if __name__ == "__main__":
    main()
