# Movie Recommendation System

**Python, SQL, Pandas** · 2026

- Built a recommendation system to suggest movies based on genre and
  average user ratings, with a cold-start fallback to overall top-rated
  titles.
- Used SQL (SQLite, indexed and portable to MySQL) for data storage and
  Pandas for data processing, aggregation, and ranking.
- Improved search efficiency through structured query logic — indexed
  lookups on genre, title, and rating joins instead of scanning full tables.

## Resume bullet (matches your existing format)

> **Movie Recommendation System, Python, SQL, Pandas**
> ○ Built a recommendation system to suggest movies based on genre and user ratings.
> ○ Used SQL for data storage and Python for data processing and filtering.
> ○ Improved search efficiency through structured query logic.

## How the recommendations work

1. **By genre** — SQL joins `movies` to `ratings` and filters by genre
   (indexed), then Pandas aggregates average rating and rating count per
   movie and ranks them.
2. **Per user** — SQL pulls everything a user has rated; Pandas finds
   their top 3 favorite genres by average rating given, then SQL fetches
   the best unwatched movies in those genres (`NOT IN` the user's
   watched list).
3. **Search** — title/genre `LIKE` search backed by indexes, joined with
   live rating averages.
4. **Cold-start fallback** — `top_rated()` returns the highest-rated
   movies overall, useful when a user has no rating history yet.

## Project structure

```
movie-recommendation-system/
├── schema.sql        # tables + indexes (genre, title, movie_id, user_id)
├── database.py        # SQLite connection + init/reset helpers
├── seed_data.py        # generates sample movies/users/ratings with pandas
├── recommender.py      # MovieRecommender: search, genre, per-user, top-rated
├── cli.py               # interactive command-line interface
├── app.py                # Flask web interface (same engine, browser UI)
├── templates/            # Jinja templates for the web UI
├── static/style.css      # cinema-themed styling for the web UI
└── requirements.txt
```

## Run it locally

There are two ways to use this project — pick whichever you want.

### Option A — Web interface (browser)

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. You get:
- A home page with top-rated movies, a genre quick-pick, and a member list
- `/search` — search by title or genre
- `/genre` — top-rated movies in a chosen genre
- `/user/<id>` — personalized picks + rating history for a member
- `/users` — full member list

### Option B — Command-line interface

```bash
pip install -r requirements.txt
python cli.py
```

Drops you into a text menu:

```
1. Search movies (title or genre)
2. Recommend top movies by genre
3. Recommend for a specific user
4. Show overall top-rated movies
5. List genres
6. List users
0. Exit
```

Either way, on first run it seeds the database with 50 sample movies
across 10 genres, 40 users, and 700+ ratings — both interfaces share
the same `movies.db` file and the same `recommender.py` logic.

To regenerate the sample data from scratch:

```bash
python seed_data.py
```

## Using your own data

Point `seed_data.py` at a real dataset (e.g. MovieLens) instead of the
synthetic generator — load it into a pandas DataFrame with the same
`title`, `genre`, `release_year` / `user_id`, `movie_id`, `rating`
columns and use `DataFrame.to_sql()` to load it, exactly like `seed_data.py`
does now.

## Using MySQL instead of SQLite

The schema is plain SQL. Swap `get_connection()` in `database.py` for a
MySQL connector (e.g. `mysql-connector-python`), change
`AUTOINCREMENT` → `AUTO_INCREMENT` in `schema.sql`, and everything else
— the recommender, the CLI, the pandas logic — works unchanged, since
`pandas.read_sql()` works with any DB-API connection.

## Possible extensions

- Collaborative filtering (user-user or item-item similarity) instead
  of genre-based recommendations
- Weighted ratings that discount movies with very few reviews
- Pagination / CSV export for large catalogs
- User login so "recommendations for me" doesn't require picking an ID
