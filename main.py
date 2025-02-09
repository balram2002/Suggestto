import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_database

# Global variables for cached data and similarity matrix
data = None
similarity = None

def create_similarity():
    """Create or load the movie similarity matrix."""
    global data, similarity
    
    if data is None:  # Load data only once per request
        data = pd.read_csv('main_data.csv')  # Ensure this path is correct in production
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(data['comb'])  # 'comb' column should be the combined features
        similarity = cosine_similarity(count_matrix)  # Compute cosine similarity
        
    return data, similarity

def rcmd(movie_name):
    """Recommend similar movies based on cosine similarity."""
    movie_name = movie_name.strip().lower()  # Normalize movie name input
    
    # Initialize data and similarity matrix if not already done
    data, similarity = create_similarity()

    # Check if the movie exists in the dataset
    if movie_name not in data['movie_title'].str.lower().values:
        return 'Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies.'
    
    # Get index of the movie in the dataset
    movie_index = data[data['movie_title'].str.lower() == movie_name].index[0]

    # Get similarity scores for the movie and sort by score
    similar_movies = list(enumerate(similarity[movie_index]))
    similar_movies_sorted = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:11]  # Exclude the movie itself

    # Collect movie titles for recommendations
    recommendations = [data.iloc[i[0]]['movie_title'] for i in similar_movies_sorted]
    
    return recommendations

def convert_to_list(my_list):
    """Convert a string representation of a list to an actual list."""
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

def get_suggestions():
    """Fetch movie titles as suggestions for the user."""
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

def get_current_user():
    """Get the current logged-in user."""
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
    """User registration route."""
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
    """Home page route."""
    user = get_current_user()
    suggestions = get_suggestions()
    return render_template('home.html', suggestions=suggestions, user=user)

@app.route("/similarity", methods=["POST"])
def similarity():
    """Route to fetch similar movies based on user input."""
    movie = request.form['name']
    recommendations = rcmd(movie)  # Get the recommended movies
    if isinstance(recommendations, str):  # Check if it's an error message
        return recommendations
    else:
        m_str = "---".join(recommendations)  # Join recommendations with '---'
        return m_str  # Return the recommendations as a string

@app.route("/login", methods = ["POST", "GET"])
def login():
    """Login route."""
    user = get_current_user()
    errorpass = None
    if request.method == "POST":
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
    return render_template('login.html', loginerror=errorpass, user=user)

@app.route("/logout")
def logout():
    """Logout route."""
    session.pop('user', None)
    return redirect(url_for("login"))

@app.route("/about")
def about():
    """About page route."""
    user = get_current_user()
    suggestionss = get_suggestions()
    return render_template('about.html', suggestionss=suggestionss, user=user)

@app.route("/recommend", methods=["POST"])
def recommend():
    """Movie recommendation route."""
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
    casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                           vote_count=vote_count, release_date=release_date, runtime=runtime, status=status, genres=genres,
                           movie_cards=movie_cards, casts=casts)

if __name__ == '__main__':
    app.run()
