import os
from bs4 import BeautifulSoup

html_path = r"e:\New_vision_AI\debug_lcsc.html"
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        # Find all images and print their src
        print("Product images found (filtered):")
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get("src")
            if src and ("product" in src or "sz.lcsc.com" in src) and not src.endswith(".gif"):
                print(src)
        
        # Look for the part number C95781 specifically
        print("\nPart C95781 context:")
        for tag in soup.find_all(string=lambda s: s and "C95781" in s):
            parent = tag.find_parent("tr")
            if parent:
                row_imgs = parent.find_all("img")
                for rimg in row_imgs:
                    print(f"Row Image: {rimg.get('src')}")
else:
    print(f"File {html_path} not found.")
