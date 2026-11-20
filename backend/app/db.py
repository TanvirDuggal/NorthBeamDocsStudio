"""SQLite database helpers for the Flask application."""

from pathlib import Path
import sqlite3

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return the request-scoped SQLite connection."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None) -> None:
    """Close the request-scoped SQLite connection, if one was opened."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create the application schema if it does not exist yet."""
    database_path = Path(current_app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    db = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    db.executescript(schema_path.read_text(encoding="utf-8"))
    article_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(articles)").fetchall()
    }
    if "draft_content" not in article_columns:
        db.execute(
            "ALTER TABLE articles ADD COLUMN draft_content TEXT NOT NULL DEFAULT ''"
        )
    db.commit()


def init_app(app) -> None:
    """Register database lifecycle hooks and the ``init-db`` CLI command."""
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        init_db()
        print("Initialized the database.")
