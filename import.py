import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	books = open("books.csv")
	reader = csv.reader(books)

	db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL, firstname VARCHAR NOT NULL, lastname VARCHAR NOT NULL, icon_id INTEGER NOT NULL)")	
	db.execute("CREATE TABLE books(isbn VARCHAR NOT NULL,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year VARCHAR NOT NULL)")	
	db.execute("CREATE TABLE reviews(isbn VARCHAR NOT NULL, user_id INTEGER REFERENCES users,rating INTEGER NOT NULL, review VARCHAR NOT NULL)")	
	print("Tables created!")

	for isbn,title,author,year in reader:
		db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn,:title,:author,:year)",
		{"isbn":isbn,"title":title,"author":author,"year":year})
		print(f"Book {title} has been added")
	db.commit()
	print("Books has been added")

if __name__ == "__main__":
	main()