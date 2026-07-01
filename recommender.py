"""
Movie Recommendation System — core engine.

Design:
- SQL does the heavy lifting of filtering and joining (structured query
  logic, backed by indexes on genre/title/movie_id/user_id).
- Pandas takes it from there for aggregation, ranking, and shaping
  results for display.
"""

import pandas as pd
from database import get_connection


class MovieRecommender:
    def __init__(self):
        self.conn = get_connection()

    def close(self):
        self.conn.close()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search(self, query: str) -> pd.DataFrame:
        """Search movies by title or genre (uses the title/genre indexes)."""
        like = f"%{query}%"
        sql = """
            SELECT m.id, m.title, m.genre, m.release_year,
                   ROUND(AVG(r.rating), 2) AS avg_rating,
                   COUNT(r.id) AS num_ratings
            FROM movies m
            LEFT JOIN ratings r ON r.movie_id = m.id
            WHERE m.title LIKE ? OR m.genre LIKE ?
            GROUP BY m.id
            ORDER BY avg_rating IS NULL, avg_rating DESC
        """
        return pd.read_sql(sql, self.conn, params=(like, like))

    # ------------------------------------------------------------------
    # Recommend by genre
    # ------------------------------------------------------------------
    def recommend_by_genre(self, genre: str, top_n: int = 5, min_ratings: int = 1) -> pd.DataFrame:
        """
        Top-rated movies in a genre, filtered in SQL and ranked with pandas.
        min_ratings avoids surfacing a movie with a single 5-star fluke.
        """
        sql = """
            SELECT m.id, m.title, m.genre, m.release_year,
                   r.rating
            FROM movies m
            JOIN ratings r ON r.movie_id = m.id
            WHERE m.genre = ?
        """
        raw = pd.read_sql(sql, self.conn, params=(genre,))
        if raw.empty:
            return raw

        agg = (
            raw.groupby(["id", "title", "genre", "release_year"])
            .agg(avg_rating=("rating", "mean"), num_ratings=("rating", "count"))
            .reset_index()
        )
        agg["avg_rating"] = agg["avg_rating"].round(2)
        agg = agg[agg["num_ratings"] >= min_ratings]
        return agg.sort_values(
            ["avg_rating", "num_ratings"], ascending=[False, False]
        ).head(top_n).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Recommend for a user
    # ------------------------------------------------------------------
    def recommend_for_user(self, user_id: int, top_n: int = 5) -> pd.DataFrame:
        """
        Look at which genres this user rates highly, then suggest their
        top-rated unwatched movies in those genres.
        """
        rated_sql = """
            SELECT m.genre, r.rating, r.movie_id
            FROM ratings r
            JOIN movies m ON m.id = r.movie_id
            WHERE r.user_id = ?
        """
        rated = pd.read_sql(rated_sql, self.conn, params=(user_id,))
        if rated.empty:
            return pd.DataFrame()

        # Favorite genres = highest average rating given by this user
        genre_pref = (
            rated.groupby("genre")["rating"].mean()
            .sort_values(ascending=False)
        )
        top_genres = genre_pref.head(3).index.tolist()
        watched_ids = rated["movie_id"].tolist()

        placeholders = ",".join("?" for _ in top_genres)
        watched_placeholders = ",".join("?" for _ in watched_ids) or "NULL"
        sql = f"""
            SELECT m.id, m.title, m.genre, m.release_year,
                   ROUND(AVG(r.rating), 2) AS avg_rating,
                   COUNT(r.id) AS num_ratings
            FROM movies m
            LEFT JOIN ratings r ON r.movie_id = m.id
            WHERE m.genre IN ({placeholders})
              AND m.id NOT IN ({watched_placeholders})
            GROUP BY m.id
            HAVING num_ratings >= 1
            ORDER BY avg_rating DESC, num_ratings DESC
        """
        params = top_genres + watched_ids
        candidates = pd.read_sql(sql, self.conn, params=params)
        return candidates.head(top_n).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Overall top rated (cold-start fallback)
    # ------------------------------------------------------------------
    def top_rated(self, top_n: int = 10, min_ratings: int = 3) -> pd.DataFrame:
        sql = """
            SELECT m.id, m.title, m.genre, m.release_year,
                   ROUND(AVG(r.rating), 2) AS avg_rating,
                   COUNT(r.id) AS num_ratings
            FROM movies m
            JOIN ratings r ON r.movie_id = m.id
            GROUP BY m.id
            HAVING num_ratings >= ?
            ORDER BY avg_rating DESC, num_ratings DESC
            LIMIT ?
        """
        return pd.read_sql(sql, self.conn, params=(min_ratings, top_n))
