from fastapi import FastAPI
import sqlite3

app = FastAPI()
 
def get_db():
    conn = sqlite3.connect(r"C:\Users\Latitude 3420\Documents\GitHub\tendate\app\scraper\tenders.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_db2():
    conn = sqlite3.connect(r"C:\Users\Latitude 3420\Documents\GitHub\tendate\app\scraper\practice.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/tenders")
def get_tenders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenders")
    tenders = cursor.fetchall()
    conn.close()
    return [dict(tender) for tender in tenders]

@app.get("/details/{url}")
def get_tender_information(url):
    conn = get_db2()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM practice WHERE url LIKE ?", (f"%{url}%",))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return {"error": "not found"}
    return dict(result)