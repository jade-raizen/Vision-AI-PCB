from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

def test_scrape():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    
    print("Starting driver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        url = "https://www.lcsc.com/search?q=resistor%20smd"
        print(f"Loading {url}...")
        driver.get(url)
        time.sleep(5)
        print(f"Page title: {driver.title}")
        print("Page source snippet (first 2000 chars):")
        print(driver.page_source[:2000])
        print("Checking for 'product' in source...")
        print(f"Found 'product' count: {driver.page_source.lower().count('product')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_scrape()
