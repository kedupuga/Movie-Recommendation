from flask import Flask, render_template, request, redirect, url_for
import database

# Initialize the Flask app
app = Flask(__name__)

# Initialize the database
database.initialize_database()

@app.route("/")
def index():
    return redirect(url_for("get_movies"))

@app.route("/movies")
def get_movies():
    movies = database.get_all_movies()
    return render_template("movies.html", movies=movies)

@app.route("/movies/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        database.add_movie(title, genre)
        return redirect(url_for("get_movies"))
    return render_template("add_movie.html")

@app.route("/movies/<int:movie_id>")
def movie_details(movie_id):
    movie = database.get_movie_details(movie_id)
    ratings = database.get_ratings_for_movie(movie_id)
    return render_template("movie_details.html", movie=movie, ratings=ratings)

@app.route("/movies/<int:movie_id>/add_rating", methods=["GET", "POST"])
def add_rating(movie_id):
    if request.method == "POST":
        rating_value = int(request.form["rating"])
        database.add_rating(movie_id, rating_value)
        return redirect(url_for("movie_details", movie_id=movie_id))
    return render_template("add_rating.html", movie_id=movie_id)

@app.route("/movies/<int:movie_id>/update", methods=["GET", "POST"])
def update_movie(movie_id):
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        database.update_movie(movie_id, title, genre)
        return redirect(url_for("get_movies"))
    movie = database.get_movie_details(movie_id)
    return render_template("update_movie.html", movie=movie)

@app.route("/movies/<int:movie_id>/delete")
def delete_movie(movie_id):
    database.delete_movie(movie_id)
    return redirect(url_for("get_movies"))

if __name__ == "__main__":
    app.run(debug=True)
