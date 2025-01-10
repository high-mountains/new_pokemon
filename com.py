from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Define the URL and base URL
url = "https://players.pokemon-card.com/event/result/list?offset=0"
base_url = "https://players.pokemon-card.com"

# Setup Chrome driver with Japanese language support
options = webdriver.ChromeOptions()
options.add_argument('--lang=ja')
options.add_argument('--charset=UTF-8')
driver = webdriver.Chrome(options=options)
driver.get(url)

# Driver for card details
driver_for_card = webdriver.Chrome(options=options)

def clean_text(text):
    """Clean the text by removing unwanted characters"""
    return text.split("(")[0].strip() if "(" in text else text.strip()

def extract_event_details(event):
    """Extract event details from a single event item"""
    relative_link = event['href'] if 'href' in event.attrs else None
    full_link = f"{base_url}{relative_link}" if relative_link else None
    title = event.find('div', class_='title').text.strip() if event.find('div', class_='title') else None
    date = event.find('span', class_='day').text.strip() if event.find('span', class_='day') else None
    return full_link, title, date

def scrape_deck_details(driver, full_link):
    """Scrape deck details for a given event"""
    driver.get(full_link)
    decks_data = []

    # Process both pages (page 1 and 2)
    for page in range(1, 3):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "c-rankTable-row")))

            # Get updated page source after loading
            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
            deck_rows = detail_soup.find_all('tr', class_='c-rankTable-row')

            if deck_rows:
                for idx, deck in enumerate(deck_rows[:1]):  # Scraping first deck for simplicity
                    deck_link_container = deck.find('td', class_='deck').find('a', class_='deck-link')
                    deck_link = deck_link_container['href'] if deck_link_container else None

                    if deck_link:
                        # Scrape the deck link and its card data
                        driver_for_card.get(deck_link)
                        card_soup = BeautifulSoup(driver_for_card.page_source, 'html.parser')
                        cards_data = extract_card_data(card_soup)
                        decks_data.append(cards_data)

            # Handle pagination (click next page)
            if page == 1:
                pagination = detail_soup.find('nav', class_='pagination')
                if pagination:
                    next_button = driver.find_element(By.CSS_SELECTOR, "button.btn:not([disabled])")
                    if next_button:
                        next_button.click()
                        time.sleep(2)
        except Exception as e:
            print(f"Error loading deck information for page {page}: {e}")

    return decks_data

def extract_card_data(card_soup):
    """Extract card data (name, count, and image) from a card page"""
    list_data = []
    image_data = []

    card_list_view = card_soup.find("section", id="cardListView")
    if card_list_view:
        for grid_item in card_list_view.find_all("div", class_="Grid_item")[:2]:  # Limit to first 2 items for brevity
            table = grid_item.find("table", class_="KSTable")
            tbody = table.find("tbody")
            th_text = clean_text(tbody.find("th").get_text())

            rows = tbody.find_all("tr")[1:]  # Skip the header row
            for row in rows:
                tds = row.find_all("td")
                if len(tds) == 2:
                    card_name = tds[0].find("span").get_text(strip=True)
                    card_count = tds[1].find("span").get_text(strip=True).replace("枚", "")
                    list_data.append({"category": th_text, "name": card_name, "count": card_count})

    card_images_view = card_soup.find("section", id="cardImagesView")
    if card_images_view:
        for grid_item in card_images_view.find_all("div", class_="Grid_item"):
            img_tag = grid_item.find("img")
            if img_tag:
                image_data.append(img_tag["src"])

    # Ensure list_data and image_data lengths match
    if len(list_data) != len(image_data):
        raise ValueError(f"Mismatch in number of items: list_data ({len(list_data)}) and image_data ({len(image_data)})")

    combined_data = [{"category": item["category"], "name": item["name"], "count": item["count"], "image_src": image_data[idx]} 
                     for idx, item in enumerate(list_data)]
    
    return combined_data

# Main scraping logic
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "eventListItem")))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    event_items = soup.find_all('a', class_='eventListItem')[:1]  # Scraping first event item for brevity

    # Open files for saving data
    with open('pokemon_events.txt', 'w', encoding="utf-8") as events_file, \
         open('pokemon_decks_url.txt', 'w', encoding="utf-8") as pokemon_decks_url, \
         open("scraped_card_data.txt", "w", encoding="utf-8") as scraped_card_data_file:

        events_file.write("Pokemon Card Events List:\n" + "="*20 + "\n\n")
        scraped_card_data_file.write("Pokemon Card Data:\n" + "="*20 + "\n\n")

        if event_items:
            for event in event_items:
                full_link, title, date = extract_event_details(event)

                # Write event details to file
                events_file.write(f"Title: {title}\nDate: {date}\nLink: {full_link}\n{'-'*10}\n")

                # Scrape deck details for each event
                if full_link:
                    decks_data = scrape_deck_details(driver, full_link)

                    # Write the scraped card data
                    for deck in decks_data:
                        for item in deck:
                            scraped_card_data_file.write(f"Category: {item['category']}\n")
                            scraped_card_data_file.write(f"Name: {item['name']}\n")
                            scraped_card_data_file.write(f"Count: {item['count']}\n")
                            scraped_card_data_file.write(f"Image: {item['image_src']}\n")
                            scraped_card_data_file.write("-" * 10 + "\n")

            print("Results saved to pokemon_events.txt and scraped_card_data.txt")

        else:
            print("No events found.")

finally:
    driver.quit()
    driver_for_card.quit()
