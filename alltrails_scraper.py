import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

ALLTRAILS_URL = "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park"


def setup_driver():
    """Setup Chrome driver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scrape_alltrails_hikes():
    print(f"Fetching {ALLTRAILS_URL} with Selenium...")
    driver = setup_driver()
    
    try:
        driver.get(ALLTRAILS_URL)
        print("Page loaded, waiting for content...")
        
        # Wait for the page to load
        time.sleep(5)
        
        # Wait for trail cards to appear
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="trail-card"]')))
        
        print("Trail cards found, extracting data...")
        
        hikes = []
        cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="trail-card"]')
        
        for i, card in enumerate(cards):
            try:
                print(f"Processing card {i+1}/{len(cards)}...")
                
                # Extract name and URL
                name_element = card.find_element(By.CSS_SELECTOR, 'a[data-testid="trail-card-title-link"]')
                name = name_element.text.strip()
                url = name_element.get_attribute('href')
                
                if not name or not url:
                    continue
                
                # Extract image
                try:
                    img_element = card.find_element(By.CSS_SELECTOR, 'img')
                    image = img_element.get_attribute('src')
                except:
                    image = None
                
                # Extract summary
                try:
                    summary_element = card.find_element(By.CSS_SELECTOR, '[data-testid="trail-card-summary"]')
                    summary = summary_element.text.strip()
                except:
                    summary = ""
                
                # Extract metadata
                try:
                    meta_element = card.find_element(By.CSS_SELECTOR, '[data-testid="trail-card-meta"]')
                    meta = meta_element.text.strip()
                except:
                    meta = ""
                
                # Extract rating
                try:
                    rating_element = card.find_element(By.CSS_SELECTOR, '[data-testid="rating-value"]')
                    rating = rating_element.text.strip()
                except:
                    rating = None
                
                # Extract review count
                try:
                    reviews_element = card.find_element(By.CSS_SELECTOR, '[data-testid="rating-count"]')
                    reviews = reviews_element.text.strip()
                except:
                    reviews = None
                
                hike_data = {
                    "name": name,
                    "url": url,
                    "image": image,
                    "summary": summary,
                    "meta": meta,
                    "rating": rating,
                    "reviews": reviews
                }
                
                hikes.append(hike_data)
                print(f"✓ {name}")
                
            except Exception as e:
                print(f"Error processing card {i+1}: {e}")
                continue
        
        print(f"\nFound {len(hikes)} hikes successfully.")
        
        # Save to JSON
        with open("alltrails_hikes.json", "w", encoding="utf-8") as f:
            json.dump(hikes, f, indent=2, ensure_ascii=False)
        
        print("Saved to alltrails_hikes.json")
        
        # Print sample data
        if hikes:
            print(f"\nSample hike: {hikes[0]['name']}")
            print(f"URL: {hikes[0]['url']}")
            if hikes[0]['rating']:
                print(f"Rating: {hikes[0]['rating']}")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_alltrails_hikes() 