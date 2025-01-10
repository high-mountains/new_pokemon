from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # Use your appropriate driver
driver.get("https://example.com")  # Replace with the target website

# Loop through multiple pages
while True:
    try:
        # Scrape the current page using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract data
        data = soup.find_all('div', class_='data-class')  # Replace with actual HTML structure
        for item in data:
            print(item.text.strip())  # Process your scraped data
        
        # Locate the "Next" button (replace with actual button attributes)
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "next-button-class"))  # Replace with actual class or locator
        )
        
        # Click the "Next" button
        next_button.click()
        
        # Wait for the next page to load
        time.sleep(3)  # Adjust based on your website's load time or use WebDriverWait
        
    except Exception as e:
        print(f"No more pages or an error occurred: {e}")
        break

# Close the browser
driver.quit()
