"""
Command-line interface for the Movie Recommendation System.

Run:
    python cli.py
"""

import pandas as pd
from database import init_db, is_empty
from seed_data import seed
from recommender import MovieRecommender

pd.set_option("display.max_colwidth", 30)


def print_df(df: pd.DataFrame, empty_message: str):
    if df.empty:
        print(f"\n{empty_message}\n")
        return
    print()
    print(df.to_string(index=False))
    print()


def list_users(engine: MovieRecommender):
    users = pd.read_sql("SELECT id, name FROM users ORDER BY id", engine.conn)
    print_df(users.head(10), "No users found.")
    print("(showing first 10 users)")


def list_genres(engine: MovieRecommender):
    genres = pd.read_sql(
        "SELECT DISTINCT genre FROM movies ORDER BY genre", engine.conn
    )["genre"].tolist()
    print("\nGenres:", ", ".join(genres), "\n")


def menu():
    print("""
Movie Recommendation System
----------------------------
1. Search movies (title or genre)
2. Recommend top movies by genre
3. Recommend for a specific user
4. Show overall top-rated movies
5. List genres
6. List users
0. Exit
""")


def main():
    init_db()
    if is_empty():
        print("No data found — seeding sample movies, users, and ratings...")
        seed(force=True)

    engine = MovieRecommender()

    try:
        while True:
            menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                query = input("Search title or genre: ").strip()
                print_df(engine.search(query), "No movies matched that search.")

            elif choice == "2":
                list_genres(engine)
                genre = input("Genre: ").strip()
                try:
                    top_n = int(input("How many results? [5]: ") or 5)
                except ValueError:
                    top_n = 5
                print_df(
                    engine.recommend_by_genre(genre, top_n=top_n),
                    f"No rated movies found for genre '{genre}'.",
                )

            elif choice == "3":
                list_users(engine)
                try:
                    user_id = int(input("User ID: ").strip())
                except ValueError:
                    print("Please enter a numeric user ID.")
                    continue
                print_df(
                    engine.recommend_for_user(user_id),
                    "Not enough rating history for this user yet.",
                )

            elif choice == "4":
                print_df(engine.top_rated(), "No ratings recorded yet.")

            elif choice == "5":
                list_genres(engine)

            elif choice == "6":
                list_users(engine)

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Not a valid option, try again.")
    finally:
        engine.close()


if __name__ == "__main__":
    main()
