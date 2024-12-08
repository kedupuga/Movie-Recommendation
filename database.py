import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Connect to SQLite database
connection = sqlite3.connect("movie_recommendation_system.db")

# Initialize the database
def initialize_database():
    cursor = connection.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS Movies")
        cursor.execute("DROP TABLE IF EXISTS Ratings")
    except sqlite3.Error as e:
        print(f"Error during table deletion: {e}")

    # Create Movies and Ratings tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES Movies (id)
        )
    ''')

    # Insert sample movies
    movies = [
        {'title': 'Avengers', 'genre': 'Action'},
        {'title': 'RRR', 'genre': 'Drama'},
        {'title': 'Inception', 'genre': 'Sci-Fi'},
        {'title': 'The Dark Knight', 'genre': 'Action'},
        {'title': 'Interstellar', 'genre': 'Sci-Fi'}
    ]
    cursor.executemany("INSERT INTO Movies (title, genre) VALUES (?, ?)", [(m['title'], m['genre']) for m in movies])

    # Insert sample ratings
    ratings = [
        {'user_id': 1, 'movie_id': 1, 'rating': 5},
        {'user_id': 1, 'movie_id': 2, 'rating': 4},
        {'user_id': 2, 'movie_id': 1, 'rating': 4},
        {'user_id': 2, 'movie_id': 3, 'rating': 5},
        {'user_id': 3, 'movie_id': 4, 'rating': 5},
        {'user_id': 3, 'movie_id': 5, 'rating': 4}
    ]
    cursor.executemany(
        "INSERT INTO Ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
        [(r['user_id'], r['movie_id'], r['rating']) for r in ratings]
    )

    connection.commit()
    print("Database initialized successfully.")

# Fetch all movies
def get_all_movies():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Movies")
    movies = cursor.fetchall()
    return movies

# Movie recommendation system
def recommend_movies(user_id, top_n=3):
    # Fetch ratings data
    ratings_df = pd.read_sql_query("SELECT user_id, movie_id, rating FROM Ratings", connection)
    movies_df = pd.read_sql_query("SELECT * FROM Movies", connection)

    # Create user-movie matrix
    user_movie_matrix = ratings_df.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)

    # Calculate similarity between users
    user_similarity = cosine_similarity(user_movie_matrix)
    similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)

    # Get similar users
    similar_users = similarity_df[user_id].sort_values(ascending=False).index[1:]

    # Aggregate ratings from similar users for recommendation
    user_ratings = user_movie_matrix.loc[similar_users].mean().sort_values(ascending=False)
    user_seen_movies = ratings_df[ratings_df['user_id'] == user_id]['movie_id']

    # Exclude already rated movies
    recommendations = user_ratings[~user_ratings.index.isin(user_seen_movies)].head(top_n)
    recommended_movie_ids = recommendations.index.tolist()

    # Fetch recommended movies
    recommended_movies = movies_df[movies_df['id'].isin(recommended_movie_ids)]
    return recommended_movies[['id', 'title', 'genre']].to_dict('records')

# Add a new rating
def add_rating(user_id, movie_id, rating):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Ratings (user_id, movie_id, rating) VALUES (?, ?, ?)", (user_id, movie_id, rating))
    connection.commit()
    print(f"Rating {rating} added for movie ID {movie_id} by user ID {user_id}.")

# Main function
if __name__ == "__main__":
    initialize_database()

    # Example: Get all movies
    print("Movies in the database:")
    for movie in get_all_movies():
        print(movie)

    # Example: Add a new rating
    add_rating(user_id=4, movie_id=1, rating=5)

    # Example: Recommend movies for user 1
    print("\nRecommended movies for user 1:")
    recommendations = recommend_movies(user_id=1, top_n=3)
    for movie in recommendations:
        print(movie)
