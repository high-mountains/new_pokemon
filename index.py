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
        #  open('flag_file.txt', 'w', encoding="utf-8") as flag_file, \
        #  open('pokemon_decks_url.txt', 'w', encoding="utf-8") as pokemon_decks_url, \
        #  open('scraped_card_data.txt', 'w', encoding="utf-8") as scraped_card_data_file, \

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

                # Write basic event info to events file
                # events_file.write(f"Title: {title}\n")
                # events_file.write(f"Date: {date}\n")
                # events_file.write(f"Link: {full_link}\n")
                # events_file.write("-" * 10 + "\n\n")
                
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
                                    
                                    # if deck_link:
                                    #     pokemon_decks_url.write(f"Page {page} - Link: {deck_link}\n")

                                    #     # Dive deep more for get Card finally
                                    #     driver_for_card.get(deck_link)
                                    #     card_soup = BeautifulSoup(driver_for_card.page_source, 'html.parser')

                                    #     card_list_view = card_soup.find("section", id="cardListView")
                                    #     if card_list_view is None:
                                    #         flag_file.write(f"Here is no card_list_view \n")

                                    #     list_data = []
                                        
                                    #     if card_list_view:
                                    #         for grid_item in card_list_view.find_all("div", class_="Grid_item"): #-------------------------
                                    #             table = grid_item.find("table", class_="KSTable")
                                    #             tbody = table.find("tbody")
                                    #             flag_file.write(f"Here is card_list_view \n")
                                    #             # Get the `th` content and clean it
                                    #             th_text = clean_text(tbody.find("th").get_text())

                                    #             if not th_text:  # This condition is True if th_text is an empty string
                                    #                 print("Notice: th_text is empty!")
                                    #             else:
                                    #                 print(f"th_text: {th_text}")
                                    #             # Scrape each `tr` after the first one
                                    #             rows = tbody.find_all("tr")[1:]  # Skip the first `tr`
                                    #             for row in rows:
                                    #                 tds = row.find_all("td")
                                    #                 if len(tds) == 2:
                                    #                     # Extract text from `td` elements
                                    #                     card_name = tds[0].find("span").get_text(strip=True)
                                    #                     card_count = tds[1].find("span").get_text(strip=True).replace("枚", "")
                                    #                     list_data.append({
                                    #                         "category": th_text,
                                    #                         "name": card_name,
                                    #                         "count": card_count,
                                    #                     })
                                    #                     # scraped_card_data_file.write(f"Category: {th_text}")
                                    #                     # scraped_card_data_file.write(f"Card_Name: {card_name}")
                                    #                     # scraped_card_data_file.write(f"Card_Count: {card_count}")
                                    #     # Scrape data from cardImagesView
                                    #     card_images_view = card_soup.find("section", id="cardImagesView")
                                    #     image_data = []

                                    #     if card_images_view:
                                    #         for grid_item in card_images_view.find_all("div", class_="Grid_item"):
                                    #             img_tag = grid_item.find("img", class_="thumbsImage")
                                    #             if img_tag:
                                    #                 print(f"IMAGE_TAG====>", img_tag)
                                    #                 image_data.append(img_tag["src"])
                                    #             else:
                                    #                 flag_file.write(f"There is no image_data \n")
                                    #     else:
                                    #         print(f"Here IS NO IMAGE_TAGS")
                                    #     # Combine list_data and image_data
                                    #     try:
                                    #         if len(list_data) != len(image_data):
                                    #             print(f"Count of list_data: {len(list_data)}")
                                    #             print(f"Count of image_data: {len(image_data)}")
                                    #             raise Exception("Mismatch in number of items between cardListView and cardImagesView")
                                        
                                    #     except Exception as e:
                                    #         # Handle the exception
                                    #         print(f"ErrorOfSpecial: {e}")
                                        
                                    #     # raise Exception("Current is OK------>")

                                    #     combined_data = []
                                    #     for sub_idx, item in enumerate(list_data):
                                    #         item["image_src"] = image_data[sub_idx]
                                    #         combined_data.append(item)

                                    #     # Save to a text file

                                    #     # with open(output_file, "w", encoding="utf-8") as file:
                                    #     for item in combined_data:
                                    #         scraped_card_data_file.write(f"Date: {date}\n")
                                    #         scraped_card_data_file.write(f"Category: {item['category']}\n")
                                    #         scraped_card_data_file.write(f"Name: {item['name']}\n")
                                    #         scraped_card_data_file.write(f"Count: {item['count']}\n")
                                    #         scraped_card_data_file.write(f"Image: {item['image_src']}\n")
                                    #         scraped_card_data_file.write("-" * 10 + "\n")
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

                                #     next_button = driver.find_element(By.CSS_SELECTOR, "button.btn:not([disabled])")
                                #     if next_button:
                                #         next_button.click()
                                #         # Wait for the page to load
                                #         time.sleep(2)
                                
                        except Exception as e:
                            decks_file.write(f"Error loading deck information for page {page}: {str(e)}\n")
                            decks_file.write("=" * 20 + "\n\n")
                    
                    time.sleep(2)

            # print("Results have been saved to 'pokemon_events.txt' and 'pokemon_decks.txt'")
        else:
            events_file.write("No events found.")
            print("No events found.")
finally:
    driver.quit()