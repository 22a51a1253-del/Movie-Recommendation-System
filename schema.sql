-- Movie Recommendation System schema
-- Portable SQLite; matches the shape you'd use on MySQL/Postgres too.

CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    release_year INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    rating REAL NOT NULL CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (movie_id) REFERENCES movies (id)
);

-- Indexes: this is the "structured query logic" that keeps genre lookups
-- and per-movie rating aggregation fast as the table grows.
CREATE INDEX IF NOT EXISTS idx_movies_genre ON movies (genre);
CREATE INDEX IF NOT EXISTS idx_movies_title ON movies (title);
CREATE INDEX IF NOT EXISTS idx_ratings_movie_id ON ratings (movie_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings (user_id);
