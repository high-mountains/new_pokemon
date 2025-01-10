import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'test',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

def insert_data_into_db(cursor, data):
    sql = """
    INSERT INTO cards_cards (date_date, category, name, count, image, league)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, data)
    except mysql.connector.Error as err:
        print(f"Error: {err}")

url = "https://players.pokemon-card.com/event/result/list?offset=100&order=4&result_resist=1&event_type=3:1&event_type=3:2&event_type=3:7"
base_url = "https://players.pokemon-card.com"
options = webdriver.ChromeOptions()
options.add_argument('--lang=ja')
options.add_argument('--charset=UTF-8')
driver = webdriver.Chrome(options=options)
driver_for_card = webdriver.Chrome(options=options)

driver.get(url)

def clean_text(text):
    return text.split("(")[0].strip() if "(" in text else text.strip()

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "eventListItem"))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    event_items = soup.find_all('a', class_='eventListItem')
    if event_items:
        # for event in event_items[14:]:   #------
        for event in event_items:
            time.sleep(1)
            relative_link = event['href'] if 'href' in event.attrs else None
            full_link = f"{base_url}{relative_link}" if relative_link else None
            date = event.find('span', class_='day').text.strip() if event.find('span', class_='day') else None
            league = event.find('div', class_='league').text.strip() if event.find('div', class_='league') else None
            if league:
                league = league[2:].strip()

            if full_link:
                driver.get(full_link)

                # for page in range(1, 3):
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "c-rankTable-row"))
                )
                detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                deck_rows = detail_soup.find_all('tr', class_='c-rankTable-row')

                date_info = detail_soup.find('div', class_='date-day')
                date_text = date_info.text.strip()
                match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', date_text)
                if match:
                    year, month, day = match.groups()
                    formatted_date = f"{year}-{month}-{day}"
                else:
                    print("Date format not recognized.")

                if deck_rows:
                    # for deck in deck_rows[:1]:   #---------
                    for deck in deck_rows:
                        time.sleep(0.5)
                        deck_link_container = deck.find('td', class_='deck').find('a', class_='deck-link')
                        deck_link = deck_link_container['href'] if deck_link_container and 'href' in deck_link_container.attrs else None

                        if deck_link:
                            driver_for_card.get(deck_link)
                            card_soup = BeautifulSoup(driver_for_card.page_source, 'html.parser')
                            card_list_view = card_soup.find("section", id="cardListView")
                            list_data = []

                            if card_list_view:
                                for grid_item in card_list_view.find_all("div", class_="Grid_item"):
                                    table = grid_item.find("table", class_="KSTable")
                                    tbody = table.find("tbody")
                                    th_text = clean_text(tbody.find("th").get_text())

                                    rows = tbody.find_all("tr")[1:]
                                    for row in rows:
                                        tds = row.find_all("td")
                                        if len(tds) == 2:
                                            card_name = tds[0].find("span").get_text(strip=True)
                                            card_count = tds[1].find("span").get_text(strip=True).replace("枚", "")
                                            list_data.append({
                                                "category": th_text,
                                                "name": card_name,
                                                "count": card_count,
                                            })

                            card_images_view = card_soup.find("section", id="cardImagesView")
                            image_data = []
                            if card_images_view:
                                for grid_item in card_images_view.find_all("div", class_="Grid_item"):
                                    img_tag = grid_item.find("img", class_="thumbsImage")
                                    if img_tag:
                                        image_data.append(img_tag["src"])

                            if len(list_data) == len(image_data):
                                for idx, item in enumerate(list_data):
                                    item["image_src"] = image_data[idx]
                                    data_tuple = (
                                        formatted_date,
                                        item["category"],
                                        item["name"],
                                        item["count"],
                                        item["image_src"],
                                        league
                                    )
                                    insert_data_into_db(cursor, data_tuple)
                                    connection.commit()


            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//li[@class="pagination-item"]//button[not(@disabled) and contains(text(), "2")]'))
            )

            if next_button:
                next_button.click()
                
                time.sleep(3)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "c-rankTable-row"))
                )
                next_page_detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                next_page_deck_rows = next_page_detail_soup.find_all('tr', class_='c-rankTable-row')
                
                if next_page_deck_rows:
                    # for next_page_deck in next_page_deck_rows[:1]:  #------
                    for next_page_deck in next_page_deck_rows:  #------
                        time.sleep(0.5)

                        deck_link_container_second = next_page_deck.find('td', class_='deck').find('a', class_='deck-link')
                        deck_link_second = deck_link_container_second['href'] if deck_link_container_second and 'href' in deck_link_container_second.attrs else None

                        if deck_link_second:
                            driver_for_card.get(deck_link_second)
                            card_soup_second = BeautifulSoup(driver_for_card.page_source, 'html.parser')

                            card_list_view_second = card_soup_second.find("section", id="cardListView")
                            list_data = []

                            if card_list_view_second:
                                for grid_item in card_list_view_second.find_all("div", class_="Grid_item"):
                                    table = grid_item.find("table", class_="KSTable")
                                    tbody = table.find("tbody")
                                    th_text = clean_text(tbody.find("th").get_text())

                                    rows = tbody.find_all("tr")[1:]
                                    for row in rows:
                                        tds = row.find_all("td")
                                        if len(tds) == 2:
                                            card_name = tds[0].find("span").get_text(strip=True)
                                            card_count = tds[1].find("span").get_text(strip=True).replace("枚", "")
                                            list_data.append({
                                                "category": th_text,
                                                "name": card_name,
                                                "count": card_count,
                                            })

                            card_images_view = card_soup_second.find("section", id="cardImagesView")
                            image_data = []
                            if card_images_view:
                                for grid_item in card_images_view.find_all("div", class_="Grid_item"):
                                    img_tag = grid_item.find("img", class_="thumbsImage")
                                    if img_tag:
                                        image_data.append(img_tag["src"])

                            if len(list_data) == len(image_data):
                                for idx, item in enumerate(list_data):
                                    item["image_src"] = image_data[idx]
                                    data_tuple = (
                                        formatted_date,
                                        item["category"],
                                        item["name"],
                                        item["count"],
                                        item["image_src"],
                                        league
                                    )
                                    insert_data_into_db(cursor, data_tuple)
                                    connection.commit()

finally:
    driver.quit()
    driver_for_card.quit()
    if connection.is_connected():
        cursor.close()
        connection.close()