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
    # 1. Unification des datasets
    run_step("UNIFYING DATASETS", "python e:\\New_vision_AI\\unify_all_to_yolo.py")
    
    # 2. Training (Optimisé CPU)
    run_step("TRAINING MODEL (YOLO11)", "python e:\\New_vision_AI\\train_full.py")
    
    # 3. Inference de test
    run_step("VERIFYING PIPELINE", "python e:\\New_vision_AI\\inference.py")
    
    print("\n[PIPELINE COMPLETE] Your model is trained and ready for inference!")

if __name__ == "__main__":
    main()
