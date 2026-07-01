"""
Movie Recommendation System — web interface.

Same underlying engine as cli.py (recommender.py + SQL + pandas),
just wrapped in a Flask front end instead of a terminal menu.
"""

from flask import Flask, render_template, request
from database import init_db, is_empty
from seed_data import seed
from recommender import MovieRecommender

app = Flask(__name__)


def get_engine():
    return MovieRecommender()


@app.route("/")
def home():
    import pandas as pd
    engine = get_engine()
    top = engine.top_rated(top_n=8)
    genres = pd.read_sql(
        "SELECT DISTINCT genre FROM movies ORDER BY genre", engine.conn
    )["genre"].tolist()
    users = pd.read_sql(
        "SELECT id, name FROM users ORDER BY id LIMIT 12", engine.conn
    ).to_dict("records")
    engine.close()

    return render_template(
        "home.html",
        top=top.to_dict("records"),
        genres=genres,
        users=users,
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        engine = get_engine()
        results = engine.search(query).to_dict("records")
        engine.close()
    return render_template("search.html", query=query, results=results)


@app.route("/genre")
def genre():
    name = request.args.get("name", "").strip()
    top_n = request.args.get("top_n", 10, type=int)
    results = []
    if name:
        engine = get_engine()
        results = engine.recommend_by_genre(name, top_n=top_n).to_dict("records")
        engine.close()
    return render_template("genre.html", genre=name, top_n=top_n, results=results)


@app.route("/user/<int:user_id>")
def user_recommendations(user_id):
    engine = get_engine()
    import pandas as pd
    member = pd.read_sql(
        "SELECT id, name FROM users WHERE id = ?", engine.conn, params=(user_id,)
    )
    results = engine.recommend_for_user(user_id, top_n=10).to_dict("records")
    history = pd.read_sql(
        """
        SELECT m.title, m.genre, r.rating
        FROM ratings r JOIN movies m ON m.id = r.movie_id
        WHERE r.user_id = ?
        ORDER BY r.rating DESC
        """,
        engine.conn,
        params=(user_id,),
    ).to_dict("records")
    engine.close()

    if member.empty:
        return render_template("user.html", found=False, user_id=user_id)

    return render_template(
        "user.html",
        found=True,
        user_id=user_id,
        user_name=member.iloc[0]["name"],
        results=results,
        history=history,
    )


@app.route("/users")
def users_list():
    engine = get_engine()
    import pandas as pd
    all_users = pd.read_sql("SELECT id, name FROM users ORDER BY id", engine.conn).to_dict("records")
    engine.close()
    return render_template("users.html", users=all_users)


if __name__ == "__main__":
    init_db()
    if is_empty():
        seed(force=True)
    app.run(debug=True)
