import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"

# conexão com o banco
conn = sqlite3.connect("database/prices.db")
cursor = conn.cursor()

# cria tabelas se não existirem
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    category TEXT,
    rating INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    price REAL,
    collected_at DATETIME,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
)
""")

response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

books = soup.find_all("article", class_="product_pod")

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

for book in books:
    title = book.h3.a["title"]
    price = float(book.find("p", class_="price_color").text.replace("£", ""))
    rating_class = book.find("p", class_="star-rating")["class"][1]
    rating = rating_map[rating_class]
    category = "Travel"
    collected_at = datetime.now()
