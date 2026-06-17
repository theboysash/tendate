import requests
from bs4 import BeautifulSoup
import time
import sqlite3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

BASE_URL = "https://easytenders.co.za/tenders-in/gauteng"


#https://easytenders.co.za/tenders-in/gauteng?page=2

def scrape_links(BASE_URL, max=3):
    tender_links = []
    for i in range(1, max+1):
        URL = f"{BASE_URL}?page={i}"
        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.text,"lxml")
        cards = soup.select("div.card.tender")

        for card in cards: 
            link = card.select_one("a")
            tender_links.append(link["href"])
    return tender_links

def scrape_listing_information(url_list):
    all_details = []
    for url in url_list:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "lxml")
        
        details_div = soup.select_one(".tab-pane.active")
        
        if not details_div:
            continue
        
        text = details_div.get_text(separator="\n")
        
        department = ""
        description = ""
        closing_date = ""
        
        for line in text.split("\n"):
            line = line.strip()
            if "Department:" in line:
                department = line.split("Department:")[1].strip()
            if "Bid Description:" in line:
                description = line.split("Bid Description:")[1].strip()
            if "Closing Date:" in line:
                closing_date = line.split("Closing Date:")[1].strip()

        all_details.append({
            "url": url,
            "department": department,
            "description": description,
            "closing_date": closing_date
        })
    return all_details

def init_db(db_path="practice.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practice (
            url TEXT PRIMARY KEY,
            department TEXT,
            description TEXT,
            closing_date TEXT
        )
    """)
    conn.commit()
    return conn
def save_info(conn, details):
    cursor = conn.cursor()
    saved = 0
    skipped = 0
    
    for detail in details:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO practice
                (url, department, description, closing_date)
                VALUES (?, ?, ?, ?)
            """, (
                detail["url"],
                detail["department"],
                detail["description"],
                detail["closing_date"]
            ))
            if cursor.rowcount > 0:
                saved += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error saving: {e}")
    
    conn.commit()
    return saved, skipped

if __name__ == "__main__":
    conn = init_db()
    links = scrape_links(BASE_URL, max=1)
    results = scrape_listing_information(links)
    saved, skipped = save_info(conn, results)
    print(f"Saved: {saved} | Skipped: {skipped}")
    conn.close()   
