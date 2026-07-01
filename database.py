"""
Database helpers for the Movie Recommendation System.

Uses SQLite for zero-setup storage; the schema and queries are plain
SQL so this maps directly onto MySQL/Postgres if you want to swap the
backend later (see README).
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "movies.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables and indexes if they don't already exist."""
    with open(SCHEMA_PATH) as f:
        schema = f.read()
    with get_connection() as conn:
        conn.executescript(schema)


def is_empty():
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    return count == 0


def reset_db():
    """Drop and recreate all tables — useful for regenerating sample data.

    Clears tables through an open connection instead of deleting the file,
    since deleting can fail on Windows if something (an editor, a DB
    viewer) still has the file open.
    """
    with get_connection() as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS ratings;
            DROP TABLE IF EXISTS movies;
            DROP TABLE IF EXISTS users;
            """
        )
    init_db()
