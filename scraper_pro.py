import requests
import os
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
import re

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
DATASET_DIR = BASE_DIR / "scraped_components"
TEMPLATES_DIR = BASE_DIR / "package_templates"
LOG_FILE = BASE_DIR / "scraping_log.json"

# Generic package mapping (Package Name -> List of Keywords for fallback search)
PACKAGE_TEMPLATES = {
    "SOT-23": ["SOT-23 package", "SOT-23 transistor", "SOT-23 diode"],
    "0805": ["0805 resistor smd", "0805 capacitor smd"],
    "0603": ["0603 resistor smd", "0603 capacitor smd"],
    "SOIC-8": ["SOIC-8 package", "SOIC-8 ic"],
    "QFP-32": ["QFP-32 package", "LQFP-32"],
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_image(url, folder, filename):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            folder.mkdir(parents=True, exist_ok=True)
            with open(folder / filename, 'wb') as f:
                f.write(res.content)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def get_driver():
    """Initialize a stealthy standard Selenium driver."""
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # User-Agent is crucial for stealth
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Timeouts to prevent hanging
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)
    
    # Hide automation flags
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver

def search_google_images(query, max_results=5):
    """Image search via Google using standard Selenium with stealth."""
    print(f"Searching Google for: {query}...")
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=isch"
    
    driver = get_driver()
    image_urls = []
    
    try:
        driver.get(search_url)
        time.sleep(3)
        
        # Cookie consent
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if any(kw in btn.text for kw in ["Tout accepter", "Accept all", "I agree", "Accepter"]):
                    btn.click()
                    time.sleep(2)
                    break
        except: pass

        imgs = driver.find_elements(By.CSS_SELECTOR, "img.YQ4gaf")
        if not imgs:
            imgs = driver.find_elements(By.TAG_NAME, "img")

        for img in imgs:
            if len(image_urls) >= max_results:
                break
            src = img.get_attribute('src') or img.get_attribute('data-src')
            if src and not src.startswith('data:image'):
                image_urls.append(src)
                
    except Exception as e:
        print(f"Error searching Google for {query}: {e}")
    finally:
        driver.quit()
    return image_urls

def search_lcsc(query):
    """Search LCSC for a component and return its image and package."""
    print(f"Searching LCSC for: {query}...")
    search_url = f"https://www.lcsc.com/search?q={query.replace(' ', '+')}"
    
    driver = get_driver()
    result = {"image": None, "package": None}
    
    try:
        driver.get(search_url)
        # Inject cookie to bypass notice
        try:
            driver.add_cookie({"name": "LCSC_accepted-cookie-policy", "value": "yes_1", "domain": ".lcsc.com"})
            driver.refresh()
            time.sleep(5)
        except Exception as ce: 
            print(f"  Cookie injection error: {ce}")

        # DEBUG: Save screenshot and page source with query name
        safe_query = re.sub(r'[^\w\-_]', '_', query)
        driver.save_screenshot(f"debug_lcsc_{safe_query}.png")
        with open(f"debug_lcsc_{safe_query}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"  Debug data saved for {query}.")
        
        # Try to find the image - Targeted approach (Verified in scraper_test.py)
        try:
            # v-image containers handle the product thumbnails
            thumbnails = driver.find_elements(By.CSS_SELECTOR, "div.v-image__image")[:10]
            for i, thumb in enumerate(thumbnails):
                try:
                    if i < 3: # Targeted scroll triggers lazy load swap
                        driver.execute_script("arguments[0].scrollIntoView();", thumb)
                        time.sleep(2)
                    
                    style = thumb.get_attribute("style")
                    if style and "url(" in style:
                        # Clean the URL
                        match = re.search(r'url\("([^"]+)"\)', style)
                        if match:
                            url = match.group(1).replace('&quot;', '').replace('"', '')
                            if ("product" in url or "assets.lcsc.com" in url or "sz.lcsc.com" in url) and "no_goods" not in url:
                                result["image"] = url
                                print(f"  Found valid LCSC image URL: {url}", flush=True)
                                break
                except: continue
            
            # Fallback to img tags if thumbnails missed
            if not result["image"]:
                img_els = driver.find_elements(By.CSS_SELECTOR, "tr img")[:10]
                for img in img_els:
                    src = img.get_attribute("src")
                    if src and ("product" in src or "assets.lcsc.com" in src) and "no_goods" not in src:
                        result["image"] = src
                        print(f"  Found LCSC image URL (Fallback): {src}", flush=True)
                        break
        except Exception as ie:
            print(f"  Image extraction error: {ie}", flush=True)
            
        # Try to find the package
        try:
            pkg_cells = driver.find_elements(By.CSS_SELECTOR, "td.major2--text, td span, div.px-4.fz-12")
            for cell in pkg_cells:
                text = cell.text.strip()
                # Skip MPN entries (usually 6+ chars with numbers)
                if len(text) < 3 or text == query or "C" + query[1:] == text:
                    continue
                # Basic package matching
                if any(p in text.upper() for p in ["0805", "SOT-23", "SOIC-8", "TO-92", "QFP", "0603", "1206", "SOD-123", "SOT-223"]):
                    if not any(x in text.upper() for x in ["OHM", "VOLT", "WATT", "AMP"]): # Filter out other specs
                        result["package"] = text
                        print(f"  Found package info: {text}")
                        break
        except: pass

    except Exception as e:
        print(f"Error searching LCSC for {query}: {e}")
    finally:
        driver.quit()
    return result

def scrape_component(mpn, description, package_type=None):
    """Scrape specific component by MPN and fallback to package type."""
    print(f"Scraping component: {mpn} ({description})")
    
    # 1. Try LCSC (Specialized Source)
    lcsc_data = search_lcsc(mpn)
    if lcsc_data["image"]:
        if download_image(lcsc_data["image"], DATASET_DIR / mpn, f"{mpn}_lcsc.jpg"):
            print(f"  Success: Found image on LCSC for {mpn}")
            return True
            
    # 2. Try Google (General Source)
    images = search_google_images(f"{mpn} electronic component")
    if images:
        for i, img_url in enumerate(images):
            if download_image(img_url, DATASET_DIR / mpn, f"{mpn}_google_{i}.jpg"):
                print(f"  Success: Found image on Google for {mpn}")
                return True
    
    # 3. Fallback to package type if search fails
    if package_type:
        print(f"  Specific image not found for {mpn}. Falling back to package templates: {package_type}")
        template_folder = TEMPLATES_DIR / package_type
        
        # Check if we already have template images
        if template_folder.exists() and any(template_folder.iterdir()):
            print(f"  Using existing template for {package_type}")
            return True
        else:
            # Try to download template images from Google
            print(f"  Downloading templates for {package_type} from Google...")
            template_queries = PACKAGE_TEMPLATES.get(package_type, [f"{package_type} package"])
            for query in template_queries:
                t_images = search_google_images(query, max_results=3)
                for i, t_img_url in enumerate(t_images):
                    download_image(t_img_url, template_folder, f"{package_type}_{i}.jpg")
            return True
            
    print(f"  Failed: No image found for {mpn} and no fallback possible.")
    return False

def main():
    # Example components to scrape
    catalog = [
        {"mpn": "2N3904", "description": "NPN Transistor", "package": "SOT-23"},
        {"mpn": "RC0805FR-071KL", "description": "1k Ohm Resistor", "package": "0805"},
        {"mpn": "UNKNOWN_CHIP", "description": "Testing missing image", "package": "SOIC-8"},
    ]
    
    for item in catalog:
        scrape_component(item['mpn'], item['description'], item['package'])
        time.sleep(1) # Be nice to servers

if __name__ == "__main__":
    main()
