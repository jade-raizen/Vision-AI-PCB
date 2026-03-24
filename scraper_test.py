import os
import time
import re
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Setup
BASE_DIR = Path(r"e:\New_vision_AI")
DEBUG_LOG = BASE_DIR / "test_debug.log"

def log(msg):
    print(msg)
    with open(DEBUG_LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")

def test_lcsc(query):
    log(f"Testing LCSC for: {query}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    
    try:
        url = f"https://www.lcsc.com/search?q={query}"
        driver.get(url)
        time.sleep(5)
        
        # Cookie Injection
        driver.add_cookie({"name": "LCSC_accepted-cookie-policy", "value": "yes_1", "domain": ".lcsc.com"})
        driver.refresh()
        time.sleep(10)
        
        log("Looking for thumbnails...")
        thumbs = driver.find_elements(By.CSS_SELECTOR, "div.v-image__image")[:5]
        for i, thumb in enumerate(thumbs):
            driver.execute_script("arguments[0].scrollIntoView();", thumb)
            time.sleep(2)
            style = thumb.get_attribute("style")
            log(f"Thumb {i} style: {style[:100]}...")
            if style and "url(" in style:
                match = re.search(r'url\("([^"]+)"\)', style)
                if match:
                    img_url = match.group(1).replace('&quot;', '').replace('"', '')
                    if "no_goods" not in img_url:
                        log(f"SUCCESS: Found image -> {img_url}")
                        return img_url
        log("FAILED: No valid image found.")
    finally:
        driver.quit()
    return None

if __name__ == "__main__":
    if DEBUG_LOG.exists(): DEBUG_LOG.unlink()
    test_lcsc("2N3904")
