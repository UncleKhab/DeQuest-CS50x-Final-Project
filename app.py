import os
from datetime import date
import sqlite3 as sql
# Flask and Helpers
from flask import g, Flask, request, session, render_template, redirect
from flask_session import Session
from helpers import get_db, query_db, add_db, login_required, get_q, get_dict, get_profile_dict
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

#----------------------------------------------------------------------------------------------------DEFAULT ROUTE 
@app.route('/')
@login_required
def index():
    
    return render_template("index.html")

#----------------------------------------------------------------------------------------------------PROFILE ROUTE
@app.route('/profile')
@login_required
def profile():
    user_id = session["user_id"]
    user = query_db("SELECT * FROM users WHERE id = ?", [user_id], one=True)
    made_by_user = get_profile_dict("SELECT * FROM quiz WHERE user_id=?", user_id)
    profile = get_profile_dict("SELECT * FROM profile JOIN quiz ON profile.quiz_id = quiz.id WHERE profile.user_id = ?", user_id)
    
    return render_template("profile.html", user=user, profile=profile, made_by_user=made_by_user, x=1)

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
    created = 0 
    taken = 0
    add_db("INSERT INTO users(username, hash, email, taken, created) VALUES(?, ?, ?, ?, ?)", (username, hashed, email, taken, created))
                 
    log = query_db("SELECT * FROM users WHERE username=?", [username], one=True)
    session["user_id"] = log[0]
    return redirect("/")
#----------------------------------------------------------------------------------------------------LOGOUT ROUTE
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
#----------------------------------------------------------------------------------------------------CREATE ROUTE
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("create.html", r=0)
    else:
        title = request.form.get("title")
        description = request.form.get("description")
        subjects = request.form.get("subjects")
        difficulty = request.form.get("difficulty")
        db_check = query_db("SELECT * FROM quiz WHERE title=?",[title], one=True)
        #CHECKING IF THE QUIZ NAME IS AVAILABLE!
        if db_check != None:
            return render_template("create.html", r=0, e=0)#-------------------------------------------------------e=0 Quiz Already Exists
        #UPDATING THE DATABASE WITH QUIZ INFO
        times_taken = 0
        c = query_db("SELECT * FROM users WHERE id=?", [user_id], one=True)
        created = str(c[5] + 1)
        add_db("INSERT INTO quiz(title, description, subjects, user_id, times_taken,difficulty) VALUES (?,?,?,?,?,?)", (title, description, subjects, user_id, times_taken,difficulty))
        
        add_db("UPDATE users SET created = ?",(created))
        quiz = query_db("SELECT * FROM quiz WHERE title=? AND user_id=?",[title, user_id], one=True)
        return render_template("create.html", quiz=quiz, r=1)

#----------------------------------------------------------------------------------------------------LEADERBOARD ROUTE

@app.route("/leaderboards")
@login_required
def leaderboards():
    user_t = query_db("SELECT * FROM users ORDER BY taken DESC")
    user_c = query_db("SELECT * FROM users ORDER BY created DESC")
    return render_template("leaderboards.html", user_t=user_t, user_c=user_c)
#----------------------------------------------------------------------------------------------------REMOVE QUIZ ROUTE

@app.route("/deleteQuiz", methods=["POST"])
@login_required
def deleteQuiz():
    quiz_id = request.form.get("delQuiz")

    add_db("DELETE FROM answers WHERE quiz_id=?",(quiz_id))
    add_db("DELETE FROM questions WHERE quiz_id=?",(quiz_id))
    add_db("DELETE FROM quiz WHERE id=?",(quiz_id))
    return redirect("/profile")
#----------------------------------------------------------------------------------------------------ADD QUESTIONS ROUTE

@app.route("/add", methods=["POST"])
@login_required
def add():
    user_id = session["user_id"]
    question = request.form.get("question")
    checked = request.form.get("check") 
    answers = request.form.getlist("answer")
    quiz_title = request.form.get("qTitle")
    a0 = answers[0]
    a1 = answers[1]
    a2 = answers[2]
    a3 = answers[3]
    #Getting the quiz info
    quiz = query_db("SELECT * FROM quiz WHERE title=? AND user_id=?",[quiz_title, user_id], one=True)
    quiz_id = quiz[0]
    #Checking if the question is already in the quiz
    db_check = query_db("SELECT * FROM questions JOIN quiz ON questions.quiz_id = quiz.id WHERE question=? and quiz.id=?",[question, quiz_id], one=True)
    if db_check == None:
        # Adding question and answers to Database
        add_db("INSERT INTO questions(user_id, question, correct_answer, quiz_id) VALUES(?,?,?,?)",
        (user_id, question, checked, quiz_id))
        log = query_db("SELECT id FROM questions WHERE question=?", [question], one=True)
        question_id = log[0]
        add_db("INSERT INTO answers(question_id, a0, a1, a2, a3, quiz_id) VALUES (?,?,?,?,?,?)", (question_id, a0, a1, a2, a3, quiz_id))
        q_list = get_q(user_id, quiz_id)
        return render_template("create.html",q_list=q_list, quiz=quiz, r=2)
    else:
        q_list = get_q(user_id, quiz_id)
        return render_template("create.html",q_list=q_list, quiz=quiz, r=2, e=1)#-------------Question Already in the quiz



#----------------------------------------------------------------------------------------------------DELETE QUESTION ROUTE
@app.route("/delete", methods=["POST"])
@login_required
def delete():
    user_id = session["user_id"]
    question = request.form.get("delQuestion")
    quiz_title = request.form.get("qTitle")

    add_db("DELETE FROM questions WHERE user_id=? AND question=?",(user_id, question))
    quiz = query_db("SELECT * FROM quiz WHERE title=? AND user_id=?",[quiz_title, user_id], one=True)
    quiz_id = quiz[0]
    q_list = get_q(user_id, quiz_id)
    return render_template("create.html",q_list=q_list, quiz=quiz, r=2)

#----------------------------------------------------------------------------------------------------DISPLAY ALL ROUTE
@app.route("/quiz")
@login_required
def quiz():
    user_id = session["user_id"]
    quizList = query_db("SELECT * FROM quiz ORDER BY times_taken DESC")
    return render_template("quiz.html", quizList=quizList)


#----------------------------------------------------------------------------------------------------TAKE/LOAD QUIZ ROUTE
@app.route("/takeQuiz", methods=["POST"])
@login_required
def takeQuiz():
    user_id = session["user_id"]
    quiz_id = request.form.get("quizId")

    quiz = query_db("SELECT * FROM quiz WHERE id=?",[quiz_id], one=True)
    questions = get_dict(quiz_id)
    tags = quiz[3].split()
    q_list = [dict(row) for row in questions]
    
    return render_template("takeQuiz.html", quiz=quiz,tags=tags, questions=questions, q_list=q_list)

#----------------------------------------------------------------------------------------------------CHECK QUIZ ROUTE
@app.route("/checkQuiz", methods=["POST"])
@login_required
def checkQuiz():
    #GETTING INFO
    user_id = session["user_id"]
    quiz_id = request.form.get("quizId")
    quiz = query_db("SELECT * FROM quiz WHERE id=?",[quiz_id], one=True)


    #GETTING THE USER ANSWERS 
    userAnswers = request.form.getlist("answer")
    
    #GETTING THE ANSWERS TO QUESTIONS
    questions = get_dict(quiz_id)
    q_list = [dict(row) for row in questions]
    answers = []
    for row in q_list:
        answers.append(row['correct_answer'])
    
    
    #COUNTING THE CORRECT ANSWERS
    answersCount = len(answers)
    count = 0
    for i in range(answersCount):
        if answers[i] == userAnswers[i]:
            count += 1
    
    #UPDATING THE TIMES THE QUIZ WAS TAKEN
    times_taken = quiz[5] + 1
    add_db("UPDATE quiz SET times_taken=? WHERE id=?",(times_taken, quiz_id))
    
    #SENDING BACK RESULT 
    #PASSED
    if count >= answersCount / 2:
        return render_template("checkQuiz.html", r=0, answersCount=answersCount, count=count, quiz=quiz )
    #FAILED
    else:
        return render_template("checkQuiz.html", r=1, answersCount=answersCount, count=count, quiz=quiz )

#----------------------------------------------------------------------------------------------------ADD TO PROFILE
@app.route("/addToProfile", methods=["POST"])
@login_required
def addToProfile():
    user_id = session["user_id"]
    dToday = str(date.today())
    quiz_id = request.form.get("quizId")
    correct = request.form.get("correct")
    answersC = request.form.get("answersC")
    t = query_db("SELECT * FROM users WHERE id=?", [user_id], one=True)
    taken = str(t[4] + 1)
    add_db("UPDATE users SET taken = ?",(taken))
    add_db("INSERT INTO profile(user_id, quiz_id, correct_answers, total_questions, date) values (?,?,?,?,?)", (user_id, quiz_id, correct, answersC, dToday))
    return redirect("/profile")
# Close the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

