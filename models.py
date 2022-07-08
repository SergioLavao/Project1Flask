import requests
from flask import request

GoodReadsKey ="LdMXrYpP6QkcVQIozREDzQ"

class Users():
	def get_users(db):
		return db.execute("SELECT * FROM users").fetchall()	

	def get_user(db,user_id):
		return db.execute("SELECT * FROM users WHERE (id = :user_id)",
			{"id":user_id}).fetchone()

	def login(db):
		username = request.form.get("username")	
		password = request.form.get("password")	
		return db.execute("SELECT * FROM users WHERE (username = :username) AND (password = :password)",
			{"username":username,"password":password}).fetchone()	

	def register(db):
		username = request.form.get("username")	
		password = request.form.get("password")
		firstname = request.form.get("firstname")	
		lastname = request.form.get("lastname")	
		icon_id = request.form.get("icon_id")	
		if db.execute("SELECT * FROM users WHERE (username = :username)", {"username":username}).fetchone():
			return
		db.execute("INSERT INTO users (username, password, firstname, lastname, icon_id) VALUES (:username, :password,:firstname,:lastname,:icon_id)",
		{"username":username,"password":password,"firstname":firstname,"lastname":lastname,"icon_id":icon_id})
		db.commit()
		return Users.login(db)

class Books():
	def search(db):
		searchform = request.form.get("searchform")	
		search = "%" + searchform + "%"
		return db.execute(" SELECT * FROM books WHERE title LIKE :searchform OR author LIKE :searchform OR isbn LIKE :searchform",
			{"searchform":search}).fetchall()

	def get_book(db,isbn):
		return db.execute("SELECT * FROM books WHERE (isbn = :isbn)",
			{"isbn":isbn}).fetchone()

class APIS():	
	def get_api(isbn):	
		try:
			res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GoodReadsKey, "isbns": isbn})
		except (IndexError, KeyError):
			return None	
		data = res.json()
		return data

	def set_api(db,isbn):
		book = db.execute("SELECT * FROM books WHERE (isbn = :isbn)",
			{"isbn":isbn}).fetchone()
		if not book:
			return None	
		count = db.execute("SELECT COUNT(*) FROM reviews WHERE (isbn = :isbn)",{"isbn":isbn}).scalar()		 
		avg = db.execute("SELECT AVG(rating) FROM reviews WHERE (isbn = :isbn)",{"isbn":isbn}).scalar()				
		if not avg:
			avg = float(0)	
		model = {
		    "title": book.title,
		    "author": book.author,
		    "year": book.year,
		    "isbn": book.isbn,
		    "review_count": count,
		    "average_score": float(avg)
		}
		return model

class Reviews():
	def get_reviews(db,isbn):	
		return db.execute("SELECT * FROM users JOIN reviews ON reviews.user_id = users.id WHERE (reviews.isbn = :isbn)",
			{"isbn":isbn}).fetchall()

	def get_review(db,isbn,user_id):
		return db.execute(" SELECT user_id FROM reviews WHERE (isbn = :isbn) AND (user_id = :user_id)",
			{"user_id":user_id,"isbn":isbn}).fetchone()

	def post_review(db, user_id):
		isbn = request.form.get("isbn")	
		rating = request.form.get("rating")
		review = request.form.get("review")	
		db.execute("INSERT INTO reviews (isbn, user_id, rating, review) VALUES (:isbn, :user_id,:rating,:review)",
		{"isbn":isbn,"user_id":user_id,"rating":rating,"review":review})
		db.commit()