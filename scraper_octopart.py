"""
Octopart Scraper - Component Image Extraction
==============================================
Scrapes electronic component images from octopart.com for PCB dataset enrichment.
Uses Selenium with stealth techniques to handle PerimeterX protection.

Usage:
    python scraper_octopart.py                     # Run default catalog
    python scraper_octopart.py --query "2N2222"    # Single component search
"""

import os
import re
import time
import json
import argparse
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
BASE_DIR = Path(r"e:\New_vision_AI")
DATASET_DIR = BASE_DIR / "scraped_components" / "octopart"
LOG_FILE = BASE_DIR / "octopart_scraping_log.json"
BASE_URL = "https://octopart.com/fr/search"

# Delay between requests (seconds) to avoid PerimeterX detection
MIN_DELAY = 5
MAX_DELAY = 10

# Component catalog for PCB detection training
# Maps: component_type -> list of MPN queries
DEFAULT_CATALOG = {
    "resistor": [
        "RC0805FR-071KL", "CRCW08051K00FKEA", "ERJ-6ENF1001V",
        "RC0603FR-0710KL", "CRCW060310K0FKEA"
    ],
    "capacitor": [
        "CL21B104KBCNNNC", "GRM21BR71C104KA01", "CC0805KRX7R9BB104",
        "CL10B104KB8NNNC", "GRM188R71C104KA01D"
    ],
    "inductor": [
        "LQH3NPN100MJ0L", "SRN4018-100M", "NR3015T100M"
    ],
    "diode": [
        "1N4148W-7-F", "BAT54S", "SS14", "1N5819HW-7-F"
    ],
    "led": [
        "LTST-C171GKT", "SML-LX0805GW-TR", "APTD3216QBC-D"
    ],
    "ic": [
        "STM32F103C8T6", "ATmega328P-AU", "NE555DR",
        "LM358DR", "TL072CDR"
    ],
    "transistor": [
        "2N2222A", "2N3904", "BC547B", "MMBT3904",
        "IRF540NPBF", "IRLZ44NPBF"
    ],
    "connector": [
        "USB-B-Micro", "PJ-002A", "SMA-Edge-Mount"
    ],
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}


def get_driver(headless=False):
    """Initialize a stealth Selenium driver for Octopart."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)

    # Hide automation flags
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def download_image(url, folder, filename):
    """Download a single image to disk."""
    try:
        if url.startswith("//"):
            url = "https:" + url
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200 and len(res.content) > 1000:  # Skip tiny/broken images
            folder.mkdir(parents=True, exist_ok=True)
            filepath = folder / filename
            with open(filepath, 'wb') as f:
                f.write(res.content)
            print(f"    ✅ Saved: {filepath.name} ({len(res.content) // 1024}KB)")
            return True
    except Exception as e:
        print(f"    ❌ Download error: {e}")
    return False


def search_octopart(driver, query, component_type, max_images=5):
    """
    Search Octopart for a component and extract product images.
    Returns the list of successfully downloaded file paths.
    """
    search_url = f"{BASE_URL}?q={query.replace(' ', '+')}"
    print(f"\n🔍 Searching Octopart: {query} (type: {component_type})")
    print(f"   URL: {search_url}")

    saved_files = []

    try:
        driver.get(search_url)
        time.sleep(4)  # Let the page render fully

        # Check for PerimeterX challenge
        if "one more step" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
            print("   ⚠️  PerimeterX challenge detected! Waiting 15s...")
            time.sleep(15)
            # Try refreshing
            driver.refresh()
            time.sleep(5)

        # Strategy 1: Product images with object-contain class
        imgs = driver.find_elements(By.CSS_SELECTOR, "img.object-contain")

        # Strategy 2: Fallback - any image in the results area
        if not imgs:
            imgs = driver.find_elements(By.CSS_SELECTOR, "img[src*='sigma.octopart']")

        # Strategy 3: Broader fallback
        if not imgs:
            imgs = driver.find_elements(By.TAG_NAME, "img")
            imgs = [img for img in imgs if _is_product_image(img)]

        print(f"   Found {len(imgs)} candidate images")

        count = 0
        for i, img in enumerate(imgs):
            if count >= max_images:
                break

            src = img.get_attribute("src") or img.get_attribute("data-src")
            if not src:
                continue

            # Filter out logos, icons, and tiny images
            if _is_valid_image_url(src):
                safe_query = re.sub(r'[^\w\-]', '_', query)
                filename = f"{safe_query}_{count}.jpg"
                target_dir = DATASET_DIR / component_type

                if download_image(src, target_dir, filename):
                    saved_files.append(str(target_dir / filename))
                    count += 1

        if not saved_files:
            print(f"   ⚠️  No valid images found for {query}")

    except Exception as e:
        print(f"   ❌ Error searching for {query}: {e}")

    return saved_files


def _is_product_image(img_element):
    """Check if an img element likely contains a product photo."""
    try:
        src = img_element.get_attribute("src") or ""
        alt = img_element.get_attribute("alt") or ""
        width = img_element.get_attribute("width")
        height = img_element.get_attribute("height")

        # Skip tiny images (icons/logos)
        if width and int(width) < 40:
            return False
        if height and int(height) < 40:
            return False

        # Skip known non-product patterns
        skip_patterns = ["logo", "icon", "avatar", "flag", "banner", "sprite",
                         "tracking", "pixel", "analytics", "google", "facebook"]
        for p in skip_patterns:
            if p in src.lower() or p in alt.lower():
                return False

        return True
    except:
        return False


def _is_valid_image_url(url):
    """Filter image URLs to keep only product-relevant ones."""
    if not url or url.startswith("data:"):
        return False
    skip = ["logo", "icon", "sprite", "tracking", "pixel", "1x1",
            "analytics", "facebook", "google", "twitter", "badge"]
    url_lower = url.lower()
    return not any(s in url_lower for s in skip)


def run_scraper(catalog=None, headless=False):
    """Main scraping loop over the component catalog."""
    if catalog is None:
        catalog = DEFAULT_CATALOG

    log = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "results": {}}
    driver = get_driver(headless=headless)

    total_saved = 0
    try:
        for comp_type, queries in catalog.items():
            print(f"\n{'='*60}")
            print(f"📦 Component type: {comp_type.upper()} ({len(queries)} queries)")
            print(f"{'='*60}")

            type_count = 0
            for query in queries:
                files = search_octopart(driver, query, comp_type, max_images=3)
                type_count += len(files)
                total_saved += len(files)

                log["results"].setdefault(comp_type, []).append({
                    "query": query,
                    "images_saved": len(files),
                    "files": files
                })

                # Random delay between searches to avoid detection
                delay = MIN_DELAY + (MAX_DELAY - MIN_DELAY) * (hash(query) % 100) / 100
                print(f"   ⏳ Waiting {delay:.1f}s before next search...")
                time.sleep(delay)

            print(f"\n   📊 {comp_type}: {type_count} images saved")

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user.")
    finally:
        driver.quit()

    # Save log
    log["total_images"] = total_saved
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\n🏁 Scraping complete! {total_saved} images saved.")
    print(f"   Log: {LOG_FILE}")
    print(f"   Data: {DATASET_DIR}")

    return total_saved


def main():
    parser = argparse.ArgumentParser(description="Octopart Component Image Scraper")
    parser.add_argument("--query", "-q", type=str, help="Single component to search")
    parser.add_argument("--type", "-t", type=str, default="ic", help="Component type for single query")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--max-images", "-n", type=int, default=3, help="Max images per query")
    args = parser.parse_args()

    if args.query:
        # Single query mode
        driver = get_driver(headless=args.headless)
        try:
            files = search_octopart(driver, args.query, args.type, max_images=args.max_images)
            print(f"\n✅ Done. {len(files)} images saved for '{args.query}'")
        finally:
            driver.quit()
    else:
        # Full catalog mode
        run_scraper(headless=args.headless)


if __name__ == "__main__":
    main()
