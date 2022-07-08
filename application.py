import os
from flask import Flask,render_template, session, redirect,url_for,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
	return redirect(url_for('main'))

@app.route("/main")
def main():
	if 'username' in session:
		return render_template("index.html") 
	return redirect(url_for('login'))

@app.route("/login")
def login():
	if 'username' in session:
		return redirect(url_for('main'))
	return render_template("login.html",login=True)

@app.route("/login", methods=["POST"])
def validate():
	user = Users.login(db)
	if not user:
		return render_template("login.html",error=1)
	set_session(user)
	return redirect(url_for('main'))


@app.route("/register")
def register():
	if 'username' in session:
		return redirect(url_for('main'))
	return render_template("register.html")

@app.route("/register", methods=["POST"])
def postregister():
	user = Users.register(db)
	if not user:
		return render_template("register.html",error=1)
	set_session(user)
	return redirect(url_for('main'))

@app.route("/results")
def results():
	if 'username' in session:
		return redirect(url_for('main'))
	return redirect(url_for('login'))

@app.route("/results", methods=["POST"])
def search():
	books = Books.search(db)
	if not books:
		return render_template("results.html",error=1)	
	return render_template("results.html",books=books)	

@app.route("/book")
def book():
	if 'username' in session:
		return redirect(url_for('main'))
	return redirect(url_for('login'))	

@app.route("/book/<string:isbn>")
def bookpage(isbn):
	if not 'username' in session:
		return redirect(url_for('login'))
	book = Books.get_book(db,isbn)
	avg_rating = APIS.get_api(isbn)['books'][0]['average_rating']
	reviews = Reviews.get_reviews(db, isbn)	
	reviewed = None	
	if Reviews.get_review(db,isbn,session['user_id']):
		reviewed = 1	
	return render_template("book.html",book=book, avg_rating=avg_rating, reviews=reviews, reviewed=reviewed)		
 
@app.route("/book/<string:isbn>", methods=["POST"])
def postpage(isbn):
	Reviews.post_review(db,session['user_id'])
	return bookpage(isbn)	

@app.route("/api/<string:isbn>", methods=["GET"])
def apiroute(isbn):
	api_model = APIS.set_api(db,isbn)		
	if not api_model:	
		return render_template("error.html",error=404)		
	return jsonify(api_model)	

@app.route("/logout")
def logout():
    session.pop('user_id',None)
    session.pop('username',None)
    session.pop('firstname',None)
    session.pop('lastname',None)
    session.pop('icon_id',None)
    return redirect(url_for('login'))

def set_session(user):
	session['user_id'] = user.id
	session['username'] = user.username
	session['firstname'] = user.firstname
	session['lastname'] = user.lastname
	session['icon_id'] = user.icon_id