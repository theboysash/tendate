from fastapi import FastAPI
import sqlite3
from data import books
from pydantic import BaseModel

class Book(BaseModel):
    id: int
    title: str
    author: str

app = FastAPI()

@app.get("/books")
def get_books():
    return books 


@app.get("/books/search")
def get_book_by_author(author: str):
    results = [book for book in books if book["author"] == author]
    return results

@app.get("/books/{id}")
def get_individual_book(id: int):
    b = next((book for book in books if book["id"] == id), None)
    if not b:
        return {"error": "not found"}
    return b


@app.post("/books")
def create_book(book: Book):
    books.append(book)
    return book


