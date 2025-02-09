import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
import sqlite3
import os
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash

def create_similarity():
    data = pd.read_csv('main_data.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb']).toarray()
    similarity = cosine_similarity(count_matrix)
    return data,similarity


def rcmd(m):
    m = m.lower()
    try:
        data.head()
        similarity.shape
    except:
        data, similarity = create_similarity()
    if m not in data['movie_title'].unique():
        return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    else:
        i = data.loc[data['movie_title']==m].index[0]
        lst = list(enumerate(similarity[i]))
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
        lst = lst[1:11] 
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        return l



def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list



def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())



app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

def get_current_user():
    user = None
    if "user" in session:
        user = session['user']
        db = get_database()
        user_cursor = db.execute("select * from users where username = ?", [user])
        user = user_cursor.fetchone()
    return user    

@app.route("/")
@app.route("/registration", methods = ["POST", "GET"])
def registration():
    user = get_current_user()
    register_error = None
    success = None
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        db = get_database()

        user_cursor = db.execute("select * from users where username = ?", [username])
        existing_user = user_cursor.fetchone()

        if existing_user:
            register_error = "Username Already Taken! Try Something Else."
            return render_template('registration.html', register_error=register_error)
        
        db.execute("insert into users (username, password, email) values (?,?,?)", [username, hashed_password, email])
        db.commit()
        useracc = username
        success = "Account Created Successfully!"
        return render_template('registration.html', success=success,  useracc=useracc)


    return render_template('registration.html', user=user)

@app.route("/home")
def home():
    user = get_current_user()
    suggestions = get_suggestions()
    return render_template('home.html',suggestions=suggestions, user=user)

@app.route("/similarity",methods=["POST"])
def similarity():
    movie = request.form['name']
    rc = rcmd(movie)
   if isinstance(rc, str):
        return rc
    else:
        m_str="---".join(rc)
        return m_str

@app.route("/login", methods = ["POST", "GET"])
def login():
    user = get_current_user()
    errorpass = None
    if request.method == "POST":
        # username = request.form['username']
        user_entered_password = request.form['password']
        user_entered_email = request.form['email']
        db = get_database()
        user_cursor = db.execute("select * from users where email = ?", [user_entered_email])
        user = user_cursor.fetchone()

        if user:
            if check_password_hash(user['password'], user_entered_password):
                session['user'] = user['username']
                return redirect(url_for("home"))
            else:
                errorpass = "Password Did Not Match!"
        # db.commit()
    return render_template('login.html', loginerror= errorpass, user=user)

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("login"))

@app.route("/about")
def about():
    user = get_current_user()
    suggestionss = get_suggestions()
    return render_template('about.html',suggestionss=suggestionss, user=user)

@app.route("/recommend",methods=["POST"])
def recommend():
    
    title = request.form['title']
    imdb_id = request.form['imdb_id']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_profiles = request.form['cast_profiles']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']



    suggestions = get_suggestions()    


    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)

 
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[","")
    cast_ids[-1] = cast_ids[-1].replace("]","")    



    movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}
    casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
        vote_count=vote_count,release_date=release_date,runtime=runtime,status=status,genres=genres,
        movie_cards=movie_cards,casts=casts)



if __name__ == '__main__':
    app.run(debug=True)
