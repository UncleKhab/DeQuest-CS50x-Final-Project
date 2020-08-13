import os
import requests
import urllib.parse
import sqlite3 

from flask import redirect, render_template, request, session, g, Flask
from functools import wraps

DATABASE = 'quiz.db'


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def add_db(query, args=()):
    with sqlite3.connect(DATABASE) as db:
        cur = db.cursor()
        cur.execute(query, args)
        db.commit()         
    db.close()

def get_q(user_id, quiz_id):
    q_list = []
    questions = query_db("SELECT question FROM questions WHERE user_id=? AND quiz_id=?", [user_id, quiz_id])
    for q in questions:
        q_list.append(q[0])
    return q_list

def get_dict(quiz_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM questions JOIN answers ON answers.question_id = questions.id WHERE questions.quiz_id=? ",[quiz_id])
    result = c.fetchall()
    return result

def get_profile(user_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM profile JOIN quiz ON profile.quiz_id = quiz.id WHERE profile.user_id = ?", [user_id])
    result = c.fetchall()
    return result


    