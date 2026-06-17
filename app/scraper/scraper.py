import requests
from bs4 import BeautifulSoup
import time
import sqlite3

BASE_URL = "https://easytenders.co.za/tenders-in"

PROVINCES = [
    "gauteng",
    "western-cape",
    "kwazulu-natal",
    "eastern-cape",
    "free-state",
    "limpopo",
    "mpumalanga",
    "northern-cape",
    "north-west",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def scrape_tenders(province, max_pages=3):
    all_tenders = []

    for i in range(1, max_pages + 1):
        url = f"{BASE_URL}/{province}?page={i}"
        print(f"Scraping: {url}")

        output = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(output.text, "lxml")
        cards = soup.select("div.card.tender")

        if not cards:
            print(f"No tenders found on page {i}, stopping")
            break

        for card in cards:
            try:
                link = card.select_one("a")
                url_tender = link["href"]
                tender_id = link.get("data-id", "")
                department = card.select_one(".text-primary").text.strip()
                description = card.select_one(".font-size-14").text.strip()
                closing_date = card.select_one(".closing-date").text.strip()
                tender_number = card.select_one(".font-weight-bold.font-size-13").text.strip()
                province_badge = card.select_one(".badge-info")
                province_name = province_badge.text.strip() if province_badge else province

                all_tenders.append({
                    "id": tender_id,
                    "url": url_tender,
                    "department": department,
                    "description": description,
                    "closing_date": closing_date,
                    "tender_number": tender_number,
                    "province": province_name
                })
            except Exception as e:
                print(f"Error parsing card: {e}")
                continue

        time.sleep(1)

    return all_tenders


def init_db(db_path="tenders.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenders (
            id TEXT PRIMARY KEY,
            url TEXT,
            department TEXT,
            description TEXT,
            closing_date TEXT,
            tender_number TEXT,
            province TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def save_tenders(conn, tenders):
    cursor = conn.cursor()
    saved = 0
    skipped = 0

    for tender in tenders:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tenders 
                (id, url, department, description, closing_date, tender_number, province)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tender["id"],
                tender["url"],
                tender["department"],
                tender["description"],
                tender["closing_date"],
                tender["tender_number"],
                tender["province"]
            ))
            if cursor.rowcount > 0:
                saved += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error saving tender: {e}")

    conn.commit()
    return saved, skipped

if __name__ == "__main__":
    conn = init_db()
    
    results = scrape_tenders("gauteng", max_pages=2)
    
    saved, skipped = save_tenders(conn, results)
    
    print(f"\n--- Results ---")
    print(f"Total tenders scraped: {len(results)}")
    print(f"Saved to database: {saved}")
    print(f"Skipped (duplicates): {skipped}")
    
    conn.close()