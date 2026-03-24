import os
from bs4 import BeautifulSoup

html_path = r"e:\New_vision_AI\debug_lcsc.html"
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        print("All image URLs:")
        for img in soup.find_all("img"):
            print(img.get("src"))
        
        print("\nAll Part Numbers found in text:")
        for tag in soup.find_all(string=lambda s: s and ("C95781" in s or "2N3904" in s)):
            print(f"Text: {tag.strip()}")
            parent = tag.find_parent()
            if parent:
                print(f"Parent Tag: {parent.name}, Class: {parent.get('class')}")
else:
    print("File not found.")
