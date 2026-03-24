import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import sys

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
DOWNLOAD_DIR = BASE_DIR / "scraped_components"
# Wikimedia Commons search terms
KEYWORDS = ["Electronic component", "Surface-mount technology", "Integrated circuit", "Light-emitting diode", "Resistor"]
MAX_IMAGES_PER_KEYWORD = 20

def scrape_wikimedia(keyword):
    print(f"Scraping Wikimedia Commons for: {keyword}...")
    sys.stdout.flush()
    
    # Wikimedia search URL
    search_url = f"https://commons.wikimedia.org/w/index.php?search={keyword.replace(' ', '+')}&title=Special:MediaSearch&fulltext=Search&type=image"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(search_url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Wikimedia MediaSearch uses a different structure, often links to file pages
            # Simplified: look for any image tags with 'data-src' or 'src' that look like thumbnails
            imgs = soup.find_all('img')
            print(f"  Found {len(imgs)} candidate images.")
            sys.stdout.flush()
            
            count = 0
            for img in imgs:
                src = img.get('data-src') or img.get('src')
                if not src:
                    continue
                
                print(f"  Checking candidate: {src[:80]}...")
                sys.stdout.flush()

                if not src.startswith('http'):
                    src = "https:" + src

                try:
                    img_res = requests.get(src, timeout=10)
                    if img_res.status_code == 200:
                        class_name = keyword.split()[0].lower()
                        class_folder = DOWNLOAD_DIR / class_name
                        class_folder.mkdir(parents=True, exist_ok=True)
                        
                        img_name = f"wiki_{class_name}_{count}.jpg"
                        with open(class_folder / img_name, 'wb') as f:
                            f.write(img_res.content)
                        
                        count += 1
                        print(f"  Downloaded: {img_name}")
                        sys.stdout.flush()
                except Exception as e:
                    pass
        else:
            print(f"  Failed to access Wikimedia: {res.status_code}")
            
    except Exception as e:
        print(f"Error scraping {keyword}: {e}")

def main():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for kw in KEYWORDS:
        scrape_wikimedia(kw)
    print(f"Scraping complete. Images saved in: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    main()
