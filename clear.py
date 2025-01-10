from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Step 1: Define the URL
url = "https://players.pokemon-card.com/event/result/list?offset=0"
base_url = "https://players.pokemon-card.com"

# Setup Chrome driver with Japanese language support
options = webdriver.ChromeOptions()
options.add_argument('--lang=ja')
options.add_argument('--charset=UTF-8')
driver = webdriver.Chrome(options=options)
driver.get(url)

driver_for_card = webdriver.Chrome(options=options)

def clean_text(text):
    return text.split("(")[0].strip() if "(" in text else text.strip()

try:
    #  Wait for the elements to load (up to 10 seconds)
    WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.CLASS_NAME, "eventListItem"))
    )
    
    # Get the page source after JavaScript has loaded the content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all event items
    event_items = soup.find_all('a', class_='eventListItem')[:2] #--------------------------
    # Open two text files to write the results
    
    with open('pokemon_events.txt', 'w', encoding="utf-8") as events_file, \
         open('pokemon_decks.txt', 'w', encoding="utf-8") as decks_file:

        # Write header for events file
        events_file.write("Pokemon Card Events List:\n")
        events_file.write("=" * 20 + "\n\n")
        
        # Write header for decks file
        decks_file.write("Pokemon Card Deck Details:\n")
        decks_file.write("=" * 20 + "\n\n")
        
        if event_items:
            # print(f"event_items===> {event_items}")
            for event in event_items:
                relative_link = event['href'] if 'href' in event.attrs else None
                full_link = f"{base_url}{relative_link}" if relative_link else None
                title = event.find('div', class_='title').text.strip() if event.find('div', class_='title') else None
                date = event.find('span', class_='day').text.strip() if event.find('span', class_='day') else None

                # Navigate to event details and write to decks file
                if full_link:
                    driver.get(full_link)

                    # Process both pages (page 1 and 2)
                    for page in range(1, 3):
                        try:
                            # Wait for the table rows to load
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "c-rankTable-row"))
                            )

                            # Get the updated page source after loading
                            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                            deck_rows = detail_soup.find_all('tr', class_='c-rankTable-row')[:2]
                            # print(f"detail_soup=======> {detail_soup}")
                            
                            if deck_rows:
                                for deck in deck_rows: #-----------------------------
                                    deck_link_container = deck.find('td', class_='deck').find('a')
                                    deck_link = deck_link_container['href'] if deck_link_container and 'href' in deck_link_container.attrs else None
                                    
                                    decks_file.write("The to second element's URL:\n")
                                    decks_file.write(f"{deck_link_container}")
                                    decks_file.write("=" * 20 + "\n\n")
                                    
                            # If this is page 1, click the next page button
                            if page == 1:
                                # Find and click the next page button
                                print("Here is Page_1")
                                events_file.write(f"Here is Page_1")
                                events_file.write("=" * 20 + "\n\n")
                                
                                pagination = detail_soup.find('nav', class_='pagination')
                                if pagination:
                                    button = soup.find('button', class_='btn', text='2')
                                    button.click()
                                # Wait for the page to load
                                    time.sleep(2)
                                    
                            else:
                                # print("Here is Page_2")
                                events_file.write(f"Here is Page_2")

                        except Exception as e:
                            decks_file.write(f"Error loading deck information for page {page}: {str(e)}\n")
                            decks_file.write("=" * 20 + "\n\n")
                    
                    time.sleep(2)
        else:
            events_file.write("No events found.")
            print("No events found.")
finally:
    driver.quit()