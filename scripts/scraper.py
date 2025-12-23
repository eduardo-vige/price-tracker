import sqlite3
import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "prices.db")


# conexão com o banco
def init_db():
    return sqlite3.connect(DB_PATH)

def create_tables(conn):
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

def scrape_books():
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

    books_list = []

    for book in books:
        title = book.h3.a["title"]
        text_price = book.find("p", class_="price_color").text

        price = float(
            text_price.translate(str.maketrans("", "", "£Â"))
        )

        rating_class = book.find("p", class_="star-rating")["class"][1]
        rating = rating_map[rating_class]
        category = "Travel"
        collected_at = datetime.now()

        books_list.append({
            "title": title,
            "price": price,
            "rating": rating,
            "category": category,
            "collected_at": collected_at
        })

    return books_list

def insert_books(conn):
    cursor = conn.cursor()
    books_list = scrape_books()

    # insere livro (se não existir)
    for book in books_list:
        cursor.execute("""
            INSERT OR IGNORE INTO books (title, category, rating)
            VALUES (?, ?, ?)
        """, (book["title"], book["category"], book["rating"]))

        # pega id do livro
        cursor.execute("SELECT book_id FROM books WHERE title = ?", (book["title"],))
        book_id = cursor.fetchone()[0]

        # insere preço
        cursor.execute("""
            INSERT INTO prices (book_id, price, collected_at)
            VALUES (?, ?, ?)
        """, (book_id, book["price"], book["collected_at"]))

def main():
    conn = init_db()
    create_tables(conn)
    insert_books(conn)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
