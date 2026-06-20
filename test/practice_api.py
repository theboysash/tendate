from fastapi import FastAPI
import sqlite3
from data import books
from pydantic import BaseModel
from typing import Optional


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int

app = FastAPI()

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None

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

@app.delete("/books/{id}")
def delete_book(id: int):
    b = next((book for book in books if book["id"]==id), None)
    if not b:
        return {"error": "not found"}
    books.remove(b)
    return {"message": "deleted"}

@app.put("/books/{id}")
def update_details(id: int, book: Book):
    b = next((bo for bo in books if bo["id"]==id), None)
    if not b:
        return {"message": "not found"}
    b["year"] = book.year
    b["title"] = book.title
    b["author"] = book.author
    b["id"] = book.id
    return b

    
@app.patch("/books/{id}")
def update_detail(id: int, book: BookUpdate):
    b = next((bo for bo in books if bo["id"]==id), None)
    if not b:
        return {"message": "not found"}
    if book.title is not None:
        b["title"] = book.title
    if book.author is not None:
        b["author"] = book.author
    if book.year is not None:
        b["year"] = book.year
    return b
   

