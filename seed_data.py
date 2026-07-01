"""
Populates the database with a sample catalog of movies, users, and
ratings so the recommender has something to work with out of the box.

Uses pandas to build and load the data, and sqlite3 (via SQL) to store it.
"""

import random
import pandas as pd
from database import get_connection, init_db, reset_db, is_empty

GENRES = [
    "Action", "Comedy", "Drama", "Sci-Fi", "Horror",
    "Romance", "Animation", "Thriller", "Fantasy", "Documentary",
]

MOVIE_TITLES = [
    "Silent Horizon", "The Last Signal", "Paper Moonlight", "Ironclad Dawn",
    "Whispers of Neon", "The Glass Orchard", "Midnight Frequency", "Salt & Static",
    "Echo Valley", "The Long Descent", "Coral Drift", "Nightshade City",
    "Furnace Road", "The Quiet Machine", "Velvet Static", "Hollow Point",
    "The Amber Line", "Rooftop Season", "Gravity's Edge", "The Painted Hour",
    "Blue Corridor", "Ashwood", "The Forgotten Frequency", "Static Bloom",
    "Winter's Gambit", "The Cartographer's Dream", "Lanternfish", "Broken Compass",
    "The Sleeping City", "Afterglow", "Marrow", "The Last Reel",
    "Concrete Sky", "Paperweight", "The Hollow Crown", "Driftwood",
    "Signal Lost", "The Quiet Riot", "Firelight", "The Cold Shoulder",
    "Static Season", "The Long Way Home", "Nightfall Junction", "Ember & Ash",
    "The Slow Fade", "Glasshouse", "Redshift", "The Waiting Room",
    "Salt Line", "Wildfire Season",
]


def _build_dataframes():
    random.seed(42)

    movies = pd.DataFrame({
        "title": MOVIE_TITLES,
        "genre": [random.choice(GENRES) for _ in MOVIE_TITLES],
        "release_year": [random.randint(1995, 2026) for _ in MOVIE_TITLES],
    })

    user_names = [f"User {i}" for i in range(1, 41)]
    users = pd.DataFrame({"name": user_names})

    return movies, users


def _build_ratings(movie_ids, user_ids):
    random.seed(7)
    rows = []
    for user_id in user_ids:
        # each user rates a random subset of movies (10-25)
        sample_size = random.randint(10, 25)
        for movie_id in random.sample(movie_ids, sample_size):
            rows.append({
                "user_id": user_id,
                "movie_id": movie_id,
                "rating": round(random.uniform(1, 5) * 2) / 2,  # 0.5 increments
            })
    return pd.DataFrame(rows)


def seed(force=False):
    """Load sample data. If force=True, wipes and regenerates everything."""
    if force:
        reset_db()
    else:
        init_db()

    if not force and not is_empty():
        print("Database already has data — use seed(force=True) to regenerate.")
        return

    movies_df, users_df = _build_dataframes()

    with get_connection() as conn:
        movies_df.to_sql("movies", conn, if_exists="append", index=False)
        users_df.to_sql("users", conn, if_exists="append", index=False)

        movie_ids = pd.read_sql("SELECT id FROM movies", conn)["id"].tolist()
        user_ids = pd.read_sql("SELECT id FROM users", conn)["id"].tolist()

        ratings_df = _build_ratings(movie_ids, user_ids)
        ratings_df.to_sql("ratings", conn, if_exists="append", index=False)

    print(f"Seeded {len(movies_df)} movies, {len(users_df)} users, "
          f"{len(ratings_df)} ratings.")


if __name__ == "__main__":
    seed(force=True)
