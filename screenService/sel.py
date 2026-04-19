from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def sschek(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.save_screenshot("screenshot.png")
    #TODO: Isse GCS mein daalo
    print(driver.title)

sschek(url)
