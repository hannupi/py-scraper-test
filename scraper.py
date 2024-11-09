import requests
from bs4 import BeautifulSoup
import sqlite3
import argparse

class Scraper:
    def __init__(self, db_path="entries.db"):
        self.db = sqlite3.connect(db_path)
        self.client = requests.Session()
        self.create_table()

    def create_table(self):
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS entries 
                          (name TEXT, price TEXT, img TEXT, url TEXT)''')
        self.db.commit()

    def insert_entry(self, name, price, img, url):
        try:
            cursor = self.db.cursor()
            cursor.execute('INSERT INTO entries (name, price, img, url) VALUES (?, ?, ?, ?)', (name, price, img, url))
            self.db.commit()
        except sqlite3.Error as e:
            print(f"Failed to insert entry into db: {e}")

    def extract_entry(self, item):
        try:
            name = item.find('h2').get_text(strip=True)
            price = item.find('div', class_='price').get_text(strip=True)
            img = item.find('img')['src']
            url = item.find('a')['href']
            return {"name": name, "price": price, "img": img, "url": url}
        except Exception as e:
            print(f"Failed to extract entry: {e}")
            return None

    def scrape_page(self, keyword):
        url = f"https://www.tori.fi/recommerce/forsale/search?computeracc_type=3&product_category=2.93.3215.46&q={keyword}&sort=PUBLISHED_DESC"
        print(f"\nSearching keyword '{keyword}' URL: {url}\n")
        res = self.client.get(url)
        if res.status_code != 200:
            print("GET request failed")
            return

        soup = BeautifulSoup(res.text, 'html.parser')
        entries = soup.select("section > div > article")
        print(entries)
        
        for item in entries:
            entry = self.extract_entry(item)
            if entry:
                self.insert_entry(entry['name'], entry['price'], entry['img'], entry['url'])
                print(f"Name: {entry['name']} \nPrice: {entry['price']}\nImg: {entry['img']}\nUrl: {entry['url']}\n")

    def close(self):
        self.db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape listings from Tori.fi based on a keyword.")
    parser.add_argument("keyword", type=str, help="Keyword to search for")
    args = parser.parse_args()

    scraper = Scraper()
    try:
        scraper.scrape_page(args.keyword)
    finally:
        scraper.close()

