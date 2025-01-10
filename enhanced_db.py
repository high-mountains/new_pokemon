import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# MySQL Database setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pokemon_schema',
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

# Selenium setup
url = "https://players.pokemon-card.com/event/result/list?offset="
base_url = "https://players.pokemon-card.com"
options = webdriver.ChromeOptions()
options.add_argument('--lang=ja')
options.add_argument('--charset=UTF-8')
driver = webdriver.Chrome(options=options)

driver_for_card = webdriver.Chrome(options=options)

def clean_text(text):
    return text.split("(")[0].strip() if "(" in text else text.strip()

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Loop for 240 iterations, incrementing offset by 20 each time
    for offset in range(0, 4800, 20):  # 240 * 20 = 4800 (0 to 4799, step 20)
        driver.get(f"{url}{offset}")  # Update URL with current offset

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "eventListItem"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        event_items = soup.find_all('a', class_='eventListItem')

        if event_items:
            for event in event_items:
                relative_link = event['href'] if 'href' in event.attrs else None
                full_link = f"{base_url}{relative_link}" if relative_link else None
                date = event.find('span', class_='day').text.strip() if event.find('span', class_='day') else None
                year = event.find('div', class_='title').text.strip() if event.find('div', class_='title') else None
                league = event.find('div', class_='league').text.strip() if event.find('div', class_='league') else None
                if league:
                    league = league[2:].strip()  # Remove the symbol and any following whitespace

                year_count = re.search(r'\d+', year)

                if year_count:
                    converted_year_count = year_count.group()
                else:
                    raise ValueError("No valid year found in the string")

                formatted_date = f"{converted_year_count}-{date.replace('/', '-')}"

                if full_link:
                    driver.get(full_link)

                    for page in range(1, 3):
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "c-rankTable-row"))
                        )
                        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        deck_rows = detail_soup.find_all('tr', class_='c-rankTable-row')

                        if deck_rows:
                            for deck in deck_rows:
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

finally:
    driver.quit()
    driver_for_card.quit()
    if connection.is_connected():
        cursor.close()
        connection.close()
