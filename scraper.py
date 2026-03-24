import undetected_chromedriver as uc
import time
import requests
from pathlib import Path
import sys
from selenium.webdriver.common.by import By

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
DOWNLOAD_DIR = BASE_DIR / "scraped_components"
KEYWORDS = ["resistor smd pcb", "capacitor smd pcb", "ic chip pcb", "led smd pcb", "transistor smd pcb"]
MAX_IMAGES_PER_KEYWORD = 10

def scrape_google(keyword):
    print(f"Scraping Google for: {keyword}...")
    sys.stdout.flush()
    # Using 'tbm=isch' for image search
    search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&tbm=isch"
    
    options = uc.ChromeOptions()
    options.add_argument("--headless") # uc supports headless but sometimes it's better to test without it
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = uc.Chrome(options=options)
    
    try:
        driver.get(search_url)
        time.sleep(3) # Let it load
        
        # Handle Cookie Consent if it appears
        try:
            # Google often shows a "Tout accepter" or "Accept all" button
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if "Tout accepter" in btn.text or "Accept all" in btn.text or "I agree" in btn.text:
                    btn.click()
                    time.sleep(2)
                    break
        except:
            pass
            
        # Scroll to load more
        driver.execute_script("window.scrollTo(0, 2000);")
        time.sleep(2)
        
        # Google Image results are often in <img> tags with class 'YQ4gaf'
        imgs = driver.find_elements(By.CSS_SELECTOR, "img.YQ4gaf")
        if not imgs:
            print(f"  Warning: No images found with 'img.YQ4gaf'. Saving source to debug_google.html")
            with open("debug_google.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            # Try a broader selector as backup
            imgs = driver.find_elements(By.TAG_NAME, "img")
            print(f"  Alternative: Found {len(imgs)} total images on page.")
            
        print(f"  Found {len(imgs)} candidate images.")
        sys.stdout.flush()
        
        count = 0
        for img in imgs:
            if count >= MAX_IMAGES_PER_KEYWORD:
                break
            
            try:
                # Click the image to get a better resolution if possible, or just grab the src
                src = img.get_attribute('src')
                if not src or src.startswith('data:image'):
                    # Sometimes we need to wait or click to get the real URL, 
                    # but for classification, even thumbnails might be OK.
                    # Let's try to get data-src if src is base64
                    src = img.get_attribute('data-src') or src
                
                if not src:
                    continue

                res = requests.get(src, timeout=10)
                if res.status_code == 200:
                    class_name = keyword.split()[0]
                    class_folder = DOWNLOAD_DIR / class_name
                    class_folder.mkdir(parents=True, exist_ok=True)
                    
                    img_name = f"google_{class_name}_{count}.jpg"
                    with open(class_folder / img_name, 'wb') as f:
                        f.write(res.content)
                    
                    count += 1
                    print(f"  Downloaded: {img_name}")
                    sys.stdout.flush()
                else:
                    print(f"  Failed: {src[:50]}... (Status: {res.status_code})")
            except Exception as e:
                # print(f"  Error downloading image: {e}")
                pass

    except Exception as e:
        print(f"Error scraping {keyword}: {e}")
    finally:
        driver.quit()

def main():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for kw in KEYWORDS:
        scrape_google(kw)
    print(f"Scraping complete. Images saved in: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    main()
