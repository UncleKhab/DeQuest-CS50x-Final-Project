import os
import datetime
import sqlite3 as sql
# Flask and Helpers
from flask import g, Flask, request, session, render_template, redirect
from flask_session import Session
from helpers import get_db, query_db, add_db, login_required
from tempfile import mkdtemp
# Security Related
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
# Configure Application
app = Flask(__name__)


# Ensure Template are auto-reloaded
app.config["TEMPLATE_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# SETUP DATABASE
DATABASE = 'quiz.db'

#------------------------------------------------------------------------------------------------DEFAULT ROUTE 
@app.route('/')
@login_required
def index():
    
    return render_template("index.html")



#----------------------------------------------------------------------------------------------------LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        select_user = query_db("SELECT * FROM users WHERE username = ?", [user], one=True)
        
        if select_user == None :
            return render_template("login.html", r=0)#----------------------------------------------------------------r=0 wrong username
        elif not check_password_hash(select_user["hash"], password):
            return render_template("login.html", r=1)#----------------------------------------------------------------r=1 password not correct
        else:
            session["user_id"] = select_user['id']
            return redirect("/")
    else:
        return render_template('login.html')


#----------------------------------------------------------------------------------------------------REGISTER ROUTE
@app.route("/register", methods=["POST"])
def register():
    session.clear()

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    hashed = generate_password_hash(password)

    usercheck = query_db("SELECT * FROM users WHERE username = ?", [username], one=True)
    if usercheck != None:
        return render_template("login.html", r=2)#----------------------------------------------------------------r=2 Username already exists
    emailcheck = query_db("SELECT * FROM users WHERE email = ?", [email], one=True)
    if emailcheck != None:
        return render_template("login.html", r=3)#----------------------------------------------------------------r=3 Email already in use
    if password != confirmation:
        return render_template("login.html", r=4)#----------------------------------------------------------------r=4 Passwords don't match

    add_db("INSERT INTO users(username, hash, email) VALUES(?, ?, ?)", (username, hashed, email))
                 
    log = query_db("SELECT * FROM users WHERE username=?", [username], one=True)
    session["user_id"] = log[0]
    return redirect("/")
#----------------------------------------------------------------------------------------------------LOGOUT ROUTE
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#----------------------------------------------------------------------------------------------------QUESTIONS ROUTE

@app.route("/questions", methods=["GET", "POST"])
@login_required
def questions():
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("questions.html")
    else:
        question = request.form.get("question")
        checked = request.form.get("check") 
        answers = request.form.getlist("answer")
        difficulty = request.form.get("difficulty")
        a0 = answers[0]
        a1 = answers[1]
        a2 = answers[2]
        a3 = answers[3]
        add_db("INSERT INTO questions(user_id, question, correct_answer, difficulty) VALUES(?,?,?,?)", (user_id, question, checked, difficulty))
        log = query_db("SELECT id FROM questions WHERE question=?", [question], one=True)
        question_id = log[0]
        add_db("INSERT INTO answers(question_id, a0, a1, a2, a3) VALUES (?,?,?,?,?)", (question_id, a0, a1, a2, a3))
        return render_template("index.html")

# Close the database conncection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

