from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Constants
URL = "https://players.pokemon-card.com/event/result/list?offset=0"
BASE_URL = "https://players.pokemon-card.com"

# Setup Chrome driver with Japanese language support
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=ja')
    options.add_argument('--charset=UTF-8')
    return webdriver.Chrome(options=options)

# Clean text helper function
def clean_text(text):
    return text.split("(")[0].strip() if "(" in text else text.strip()

# Wait and get the page source
def get_page_source(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "eventListItem"))
        )
        return BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print(f"Error loading page: {str(e)}")
        return None

# Navigate to the next page
def navigate_to_next_page(driver, button_text):
    try:
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[text()='{button_text}']"))
        )
        button.click()
        print(f"Success to navigate to next page.")
        time.sleep(2)  # Allow time for the page to load
    except Exception as e:
        print(f"Failed to navigate to next page: {str(e)}")

# Process deck rows
def process_deck_rows(detail_soup, decks_file):
    deck_rows = detail_soup.find_all('tr', class_='c-rankTable-row')
    for deck in deck_rows:
        deck_link_container = deck.find('td', class_='deck').find('a')
        deck_link = deck_link_container['href'] if deck_link_container and 'href' in deck_link_container.attrs else None
        decks_file.write(f"Deck Link: {deck_link}\n")
        decks_file.write("=" * 20 + "\n\n")

# Main scraping logic
def scrape_events():
    driver = setup_driver()
    driver.get(URL)

    with open('pokemon_events.txt', 'w', encoding="utf-8") as events_file, \
         open('pokemon_decks.txt', 'w', encoding="utf-8") as decks_file:

        try:
            soup = get_page_source(driver)
            if not soup:
                return
            
            event_items = soup.find_all('a', class_='eventListItem')[:2]
            if not event_items:
                events_file.write("No events found.")
                print("No events found.")
                return

            for event in event_items:
                relative_link = event['href'] if 'href' in event.attrs else None
                full_link = f"{BASE_URL}{relative_link}" if relative_link else None
                title = event.find('div', class_='title').text.strip() if event.find('div', class_='title') else None
                date = event.find('span', class_='day').text.strip() if event.find('span', class_='day') else None

                events_file.write(f"Event Title: {title}\nEvent Date: {date}\nLink: {full_link}\n\n")

                if full_link:
                    driver.get(full_link)
                    for page in range(1, 3):
                        detail_soup = get_page_source(driver)
                        if detail_soup:
                            process_deck_rows(detail_soup, decks_file)
                            if page == 1:
                                navigate_to_next_page(driver, '2')

        except Exception as e:
            print(f"Error during scraping: {str(e)}")
        finally:
            driver.quit()

# Run the scraper
scrape_events()
