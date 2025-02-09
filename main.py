import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
from functools import wraps

# Global variables for data and similarity matrix
global_data = None
global_similarity = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_similarity():
    try:
        data = pd.read_csv('main_data.csv')
        if data.empty:
            raise ValueError("Empty dataset")
        
        # Handle missing values
        data['comb'] = data['comb'].fillna('')
        
        cv = CountVectorizer(stop_words='english')
        count_matrix = cv.fit_transform(data['comb']).toarray()
        similarity = cosine_similarity(count_matrix)
        
        return data, similarity
    except Exception as e:
        print(f"Error in create_similarity: {str(e)}")
        return None, None

def initialize_data():
    global global_data, global_similarity
    if global_data is None or global_similarity is None:
        global_data, global_similarity = create_similarity()
    return global_data, global_similarity

def rcmd(m):
    if not m:
        return 'Please enter a movie name.'
    
    m = m.lower().strip()
    data, similarity = initialize_data()
    
    if data is None or similarity is None:
        return 'Error loading movie database.'
    
    try:
        if m not in data['movie_title'].str.lower().unique():
            return 'Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies'
        
        i = data.loc[data['movie_title'].str.lower() == m].index[0]
        lst = list(enumerate(similarity[i]))
        lst = sorted(lst, key=lambda x: x[1], reverse=True)
        lst = lst[1:11]
        recommendations = []
        for i in range(len(lst)):
            a = lst[i][0]
            recommendations.append(data['movie_title'][a])
        return recommendations
    except Exception as e:
        print(f"Error in rcmd: {str(e)}")
        return 'An error occurred while getting recommendations.'

def convert_to_list(my_list):
    try:
        if not my_list:
            return []
        if isinstance(my_list, str):
            my_list = my_list.replace('["', '').replace('"]', '')
            return [item.strip().strip('"') for item in my_list.split(',')]
        return my_list
    except Exception as e:
        print(f"Error in convert_to_list: {str(e)}")
        return []

def get_suggestions():
    try:
        data = pd.read_csv('main_data.csv')
        return list(data['movie_title'].str.capitalize().unique())
    except Exception as e:
        print(f"Error in get_suggestions: {str(e)}")
        return []

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes session timeout

def get_current_user():
    try:
        if "user" in session:
            user = session['user']
            db = get_database()
            user_cursor = db.execute("select * from users where username = ?", [user])
            user = user_cursor.fetchone()
            return user
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
    return None

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/registration", methods=["POST", "GET"])
def registration():
    if get_current_user():
        return redirect(url_for("home"))
    
    register_error = None
    success = None
    
    if request.method == "POST":
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            email = request.form.get('email', '').strip()
            
            if not all([username, password, email]):
                register_error = "All fields are required!"
                return render_template('registration.html', register_error=register_error)
            
            db = get_database()
            
            # Check for existing username or email
            existing_user = db.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?", 
                [username, email]
            ).fetchone()
            
            if existing_user:
                register_error = "Username or email already taken!"
                return render_template('registration.html', register_error=register_error)
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            db.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                [username, hashed_password, email]
            )
            db.commit()
            
            success = "Account Created Successfully!"
            return render_template('registration.html', success=success, useracc=username)
            
        except Exception as e:
            print(f"Error in registration: {str(e)}")
            register_error = "An error occurred during registration."
            
    return render_template('registration.html')

@app.route("/home")
@login_required
def home():
    user = get_current_user()
    suggestions = get_suggestions()
    return render_template('home.html', suggestions=suggestions, user=user)

@app.route("/similarity", methods=["POST"])
@login_required
def similarity():
    try:
        movie = request.form.get('name', '').strip()
        if not movie:
            return jsonify({'error': 'No movie name provided'})
        
        rc = rcmd(movie)
        if isinstance(rc, str):
            return jsonify({'error': rc})
        
        return jsonify({'recommendations': rc})
    except Exception as e:
        print(f"Error in similarity: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'})

@app.route("/login", methods=["POST", "GET"])
def login():
    if get_current_user():
        return redirect(url_for("home"))
    
    error = None
    
    if request.method == "POST":
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            if not all([email, password]):
                error = "All fields are required!"
                return render_template('login.html', loginerror=error)
            
            db = get_database()
            user = db.execute("SELECT * FROM users WHERE email = ?", [email]).fetchone()
            
            if user and check_password_hash(user['password'], password):
                session.permanent = True
                session['user'] = user['username']
                return redirect(url_for("home"))
            else:
                error = "Invalid email or password!"
        
        except Exception as e:
            print(f"Error in login: {str(e)}")
            error = "An error occurred during login."
    
    return render_template('login.html', loginerror=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/about")
@login_required
def about():
    user = get_current_user()
    suggestions = get_suggestions()
    return render_template('about.html', suggestionss=suggestions, user=user)

@app.route("/recommend", methods=["POST"])
@login_required
def recommend():
    try:
        # Get form data with default values
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
        cast_ids = convert_to_list(form_data['cast_ids'])
        
        # Create dictionaries for template
        movie_cards = {rec_posters[i]: rec_movies[i] for i in range(min(len(rec_posters), len(rec_movies)))}
        casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] 
                for i in range(min(len(cast_names), len(cast_ids), len(cast_chars), len(cast_profiles)))}
        
        return render_template(
            'recommend.html',
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
            casts=casts
        )
        
    except Exception as e:
        print(f"Error in recommend: {str(e)}")
        return redirect(url_for('home'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize data at startup
    initialize_data()
    app.run(debug=False)  # Set to False in production
