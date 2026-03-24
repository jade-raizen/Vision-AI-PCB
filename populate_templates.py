import requests
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
TEMPLATES_DIR = BASE_DIR / "package_templates"

SOT23_URLS = [
    "https://assets.nexperia.com/documents/outline-3d/sot23_3d.png",
    "https://www.ntchip.com/uploadimg/2024/8/SOT23%20vs%20SOT223.jpg",
    "https://www.researchgate.net/publication/242742423/figure/fig63/AS:339689191034890@1457999622341/Outline-of-SOT23-package-i-The-dimensions-can-be-found-in-the-datasheet-30.png",
    "https://www.ablic.com/en/semicon/wp-content/uploads/2024/04/ABLIC_PKG_SOT-23-3_SQ.png",
    "https://www.allelcoelec.com/upfile/images/7f/20241030091046330.png"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_images(urls, package_name):
    folder = TEMPLATES_DIR / package_name
    folder.mkdir(parents=True, exist_ok=True)
    print(f"Downloading images for {package_name}...")
    for i, url in enumerate(urls):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                ext = url.split('.')[-1].split('?')[0]
                if len(ext) > 4: ext = 'jpg' # Fallback
                filename = f"{package_name}_{i}.{ext}"
                with open(folder / filename, 'wb') as f:
                    f.write(res.content)
                print(f"  Saved: {filename}")
            else:
                print(f"  Failed: {url} (Status: {res.status_code})")
        except Exception as e:
            print(f"  Error: {url} ({e})")

if __name__ == "__main__":
    download_images(SOT23_URLS, "SOT-23")
