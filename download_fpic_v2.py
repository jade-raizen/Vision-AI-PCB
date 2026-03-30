import dataset_tools as dtools
import os
from pathlib import Path

dst_dir = Path(r"e:\New_vision_AI\datasets\fpic_component")
dst_dir.mkdir(parents=True, exist_ok=True)

print(f"Downloading FPIC-Component to {dst_dir}...")
# Supervisely FPIC-Component download
dtools.download(dataset='FPIC-Component', dst_dir=str(dst_dir))
print("Download complete.")
