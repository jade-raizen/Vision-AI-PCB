import os
import subprocess
from pathlib import Path

BASE_DIR = Path(r"e:\New_vision_AI\datasets")

def run_cmd(cmd, cwd=None):
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

def download_datasets():
    datasets = [
        {
            "name": "DeepPCB",
            "url": "https://github.com/tangsanli5201/DeepPCB.git",
            "target": BASE_DIR / "deep_pcb",
            "method": "git"
        },
        {
            "name": "PCB-Vision",
            "url": "https://github.com/hifexplo/PCBVision.git",
            "target": BASE_DIR / "pcb_vision",
            "method": "git"
        },
        {
            "name": "F-PIC",
            "url": "https://figshare.com/ndownloader/articles/12581699/versions/1",
            "target": BASE_DIR / "fpic_dataset" / "fpic.zip",
            "method": "curl"
        }
    ]

    for ds in datasets:
        print(f"\n--- Processing {ds['name']} ---")
        if ds["method"] == "git":
            if not (ds["target"] / ".git").exists():
                # For git, we might want to clone into a temp then move or just clone directly if empty
                run_cmd(["git", "clone", ds["url"], str(ds["target"])])
            else:
                print(f"{ds['name']} already exists.")
        
        elif ds["method"] == "curl":
            if not ds["target"].exists():
                ds["target"].parent.mkdir(parents=True, exist_ok=True)
                run_cmd(["curl", "-L", ds["url"], "-o", str(ds["target"])])
                print(f"Downloaded {ds['name']} to {ds['target']}")
            else:
                print(f"{ds['name']} ZIP already exists.")

if __name__ == "__main__":
    download_datasets()
