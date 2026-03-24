import os
from bs4 import BeautifulSoup
import re

html_path = r"e:\New_vision_AI\debug_lcsc_2N3904.html"
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        
        print("--- STYLE BACKGROUND IMAGES ---")
        for tag in soup.find_all(style=lambda s: s and "background-image" in s):
            style = tag.get("style")
            match = re.search(r'url\("([^"]+)"\)', style)
            if match:
                url = match.group(1)
                if "product" in url or "sz.lcsc.com" in url:
                    print(url)
        
        print("\n--- IMG TAGS ---")
        for img in soup.find_all("img"):
            src = img.get("src")
            dsrc = img.get("data-src")
            if (src and ("product" in src or "sz.lcsc.com" in src)) or (dsrc and ("product" in dsrc or "sz.lcsc.com" in dsrc)):
                print(f"src: {src} | data-src: {dsrc}")
else:
    print("File not found.")
