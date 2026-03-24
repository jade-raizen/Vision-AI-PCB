import requests
import re
import os
from pathlib import Path
import sys

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
DOWNLOAD_DIR = BASE_DIR / "scraped_components"
KEYWORDS = ["resistor smd pcb component", "capacitor smd pcb component", "ic chip pcb component", "led smd pcb component", "transistor smd pcb component"]
MAX_IMAGES_PER_KEYWORD = 15

def scrape_duckduckgo_simple(keyword):
    print(f"Scraping (Simple) DuckDuckGo for: {keyword}...")
    sys.stdout.flush()
    
    # DuckDuckGo's "html" version is often easier for simple scrapers
    url = "https://html.duckduckgo.com/html/"
    params = {'q': keyword}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Note: DuckDuckGo's "html" search is mostly text. For images, we need a different approach.
        # Let's try to get the image search page directly and look for URLs.
        image_url = f"https://duckduckgo.com/i.js?q={keyword.replace(' ', '+')}&o=json"
        res = requests.get(image_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            results = data.get('results', [])
            print(f"  Found {len(results)} potential images.")
            sys.stdout.flush()
            
            count = 0
            for item in results:
                if count >= MAX_IMAGES_PER_KEYWORD:
                    break
                
                src = item.get('image')
                if not src:
                    continue
                
                try:
                    img_res = requests.get(src, timeout=10)
                    if img_res.status_code == 200:
                        class_name = keyword.split()[0]
                        class_folder = DOWNLOAD_DIR / class_name
                        class_folder.mkdir(parents=True, exist_ok=True)
                        
                        img_name = f"ddg_simple_{class_name}_{count}.jpg"
                        with open(class_folder / img_name, 'wb') as f:
                            f.write(img_res.content)
                        
                        count += 1
                        print(f"  Downloaded: {img_name}")
                        sys.stdout.flush()
                except Exception as e:
                    pass # Skip errors
        else:
            print(f"  Failed to get results: {res.status_code}")
            
    except Exception as e:
        print(f"Error scraping {keyword}: {e}")

def main():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for kw in KEYWORDS:
        scrape_duckduckgo_simple(kw)
    print(f"Scraping complete. Images saved in: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    main()
