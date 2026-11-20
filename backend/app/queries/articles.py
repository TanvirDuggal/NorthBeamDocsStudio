"""Queries used by the writer article endpoints."""


def list_published_articles(db):
    return db.execute(
        """
        SELECT articles.title,
               article_versions.content,
               articles.creation_date,
               articles.slug
        FROM articles
        INNER JOIN article_versions
            ON article_versions.id = articles.current_snapshot_id
        WHERE articles.state_id = 2
        """
    ).fetchall()


def slug_exists(db, slug: str) -> bool:
    return db.execute(
        "SELECT 1 FROM articles WHERE slug = ?",
        (slug,),
    ).fetchone() is not None


def insert_article(
    db,
    article_id: str,
    title: str,
    state_id: int,
    slug: str,
    creation_date: str,
) -> None:
    db.execute(
        """
        INSERT INTO articles (id, title, state_id, slug, current_snapshot_id, creation_date)
        VALUES (?, ?, ?, ?, NULL, ?)
        """,
        (article_id, title, state_id, slug, creation_date),
    )


def insert_article_version(
    db,
    version_id: str,
    article_id: str,
    content: str,
    creation_date: str,
) -> None:
    db.execute(
        """
        INSERT INTO article_versions
            (id, article_id, version_number, content, creation_date)
        VALUES (?, ?, 1, ?, ?)
        """,
        (version_id, article_id, content, creation_date),
    )


def set_current_snapshot(db, article_id: str, version_id: str) -> None:
    db.execute(
        "UPDATE articles SET current_snapshot_id = ? WHERE id = ?",
        (version_id, article_id),
    )
