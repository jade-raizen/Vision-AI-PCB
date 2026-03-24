from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("Initializing Chrome...")
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
print("Loading Google...")
driver.get("https://www.google.com")
print(f"Title: {driver.title}")
driver.quit()
print("Success!")
