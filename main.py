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

# Global variables to store data and similarity matrix
data = None
similarity = None

def create_similarity():
    try:
        data = pd.read_csv('main_data.csv')
        # Handle potential encoding issues
        data = data.fillna('')  # Replace NaN values
        cv = CountVectorizer(stop_words='english')
        count_matrix = cv.fit_transform(data['comb']).toarray()
        similarity = cosine_similarity(count_matrix)
        return data, similarity
    except Exception as e:
        print(f"Error in create_similarity: {str(e)}")
        return None, None

def rcmd(m):
    global data, similarity
    
    if data is None or similarity is None:
        data, similarity = create_similarity()
        if data is None:
            return 'Error loading movie database. Please try again later.'
    
    try:
        m = m.lower().strip()
        if m not in data['movie_title'].str.lower().unique():
            return 'Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies'
        
        i = data.loc[data['movie_title'].str.lower() == m].index[0]
        lst = list(enumerate(similarity[i]))
        lst = sorted(lst, key=lambda x: x[1], reverse=True)
        lst = lst[1:11]
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        return l
    except Exception as e:
        print(f"Error in rcmd: {str(e)}")
        return 'An error occurred while processing your request. Please try again.'

def convert_to_list(my_list):
    try:
        if isinstance(my_list, str):
            my_list = my_list.replace('["', '').replace('"]', '')
            return [item.strip() for item in my_list.split('","')]
        return my_list
    except Exception as e:
        print(f"Error in convert_to_list: {str(e)}")
        return []

def get_suggestions():
    try:
        global data
        if data is None:
            data, _ = create_similarity()
        return list(data['movie_title'].str.capitalize())
    except Exception as e:
        print(f"Error in get_suggestions: {str(e)}")
        return []

app = Flask(__name__)
# Use a fixed secret key for deployment
app.secret_key = 'your-fixed-secret-key-here'  # Replace with your actual secret key

def get_current_user():
    try:
        if "user" in session:
            user = session['user']
            db = get_database()
            user_cursor = db.execute("select * from users where username = ?", [user])
            user = user_cursor.fetchone()
            return user
        return None
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
        return None

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/registration", methods=["POST", "GET"])
def registration():
    try:
        user = get_current_user()
        register_error = None
        success = None
        
        if request.method == "POST":
            username = request.form['username'].strip()
            password = request.form['password']
            email = request.form['email'].strip()
            
            if not username or not password or not email:
                register_error = "All fields are required!"
                return render_template('registration.html', register_error=register_error)
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            db = get_database()
            
            user_cursor = db.execute("select * from users where username = ? or email = ?", 
                                   [username, email])
            existing_user = user_cursor.fetchone()
            
            if existing_user:
                register_error = "Username or email already taken!"
                return render_template('registration.html', register_error=register_error)
            
            db.execute("insert into users (username, password, email) values (?,?,?)", 
                      [username, hashed_password, email])
            db.commit()
            success = "Account Created Successfully!"
            return render_template('registration.html', success=success, useracc=username)
        
        return render_template('registration.html', user=user)
    except Exception as e:
        print(f"Error in registration: {str(e)}")
        return render_template('registration.html', register_error="An error occurred. Please try again.")

@app.route("/home")
def home():
    try:
        user = get_current_user()
        if not user:
            return redirect(url_for("login"))
        suggestions = get_suggestions()
        return render_template('home.html', suggestions=suggestions, user=user)
    except Exception as e:
        print(f"Error in home: {str(e)}")
        return redirect(url_for("login"))

@app.route("/similarity", methods=["POST"])
def similarity_route():
    try:
        if not get_current_user():
            return "Please login first"
        movie = request.form['name']
        rc = rcmd(movie)
        if isinstance(rc, str):
            return rc
        return "---".join(rc)
    except Exception as e:
        print(f"Error in similarity: {str(e)}")
        return "An error occurred while processing your request"

@app.route("/login", methods=["POST", "GET"])
def login():
    try:
        user = get_current_user()
        if user:
            return redirect(url_for("home"))
        
        error = None
        if request.method == "POST":
            email = request.form['email'].strip()
            password = request.form['password']
            
            if not email or not password:
                error = "All fields are required!"
                return render_template('login.html', loginerror=error)
            
            db = get_database()
            user_cursor = db.execute("select * from users where email = ?", [email])
            user = user_cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user'] = user['username']
                return redirect(url_for("home"))
            error = "Invalid email or password!"
        
        return render_template('login.html', loginerror=error)
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return render_template('login.html', loginerror="An error occurred. Please try again.")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("login"))

@app.route("/about")
def about():
    try:
        user = get_current_user()
        if not user:
            return redirect(url_for("login"))
        suggestions = get_suggestions()
        return render_template('about.html', suggestionss=suggestions, user=user)
    except Exception as e:
        print(f"Error in about: {str(e)}")
        return redirect(url_for("login"))

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        if not get_current_user():
            return redirect(url_for("login"))
            
        # Get form data with error handling
        form_data = {
            'title': request.form.get('title', ''),
            'imdb_id': request.form.get('imdb_id', ''),
            'cast_ids': request.form.get('cast_ids', '[]'),
            'cast_names': request.form.get('cast_names', '[]'),
            'cast_chars': request.form.get('cast_chars', '[]'),
            'cast_profiles': request.form.get('cast_profiles', '[]'),
            'poster': request.form.get('poster', ''),
            'genres': request.form.get('genres', ''),
            'overview': request.form.get('overview', ''),
            'rating': request.form.get('rating', '0'),
            'vote_count': request.form.get('vote_count', '0'),
            'release_date': request.form.get('release_date', ''),
            'runtime': request.form.get('runtime', '0'),
            'status': request.form.get('status', ''),
            'rec_movies': request.form.get('rec_movies', '[]'),
            'rec_posters': request.form.get('rec_posters', '[]')
        }
        
        # Convert string lists to actual lists
        rec_movies = convert_to_list(form_data['rec_movies'])
        rec_posters = convert_to_list(form_data['rec_posters'])
        cast_names = convert_to_list(form_data['cast_names'])
        cast_chars = convert_to_list(form_data['cast_chars'])
        cast_profiles = convert_to_list(form_data['cast_profiles'])
        
        # Process cast IDs
        cast_ids = form_data['cast_ids'].replace('[', '').replace(']', '').split(',')
        cast_ids = [id.strip() for id in cast_ids if id.strip()]
        
        # Create dictionaries for template
        movie_cards = {rec_posters[i]: rec_movies[i] for i in range(min(len(rec_posters), len(rec_movies)))}
        casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] 
                for i in range(min(len(cast_names), len(cast_ids), len(cast_chars), len(cast_profiles)))}
        
        return render_template('recommend.html',
                            title=form_data['title'],
                            poster=form_data['poster'],
                            overview=form_data['overview'],
                            vote_average=form_data['rating'],
                            vote_count=form_data['vote_count'],
                            release_date=form_data['release_date'],
                            runtime=form_data['runtime'],
                            status=form_data['status'],
                            genres=form_data['genres'],
                            movie_cards=movie_cards,
                            casts=casts)
    except Exception as e:
        print(f"Error in recommend: {str(e)}")
        return redirect(url_for("home"))

if __name__ == '__main__':
    # Load data at startup
    data, similarity = create_similarity()
    # Use production server when deploying
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
