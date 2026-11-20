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


def list_all_articles_with_snapshots(db):
    return db.execute(
        """
        SELECT articles.id,
               articles.title,
               articles.slug,
               CAST(articles.state_id AS INTEGER) AS state_id,
               articles.creation_date,
               article_versions.id AS snapshot_id,
               article_versions.version_number,
               article_versions.content AS snapshot_content,
               article_versions.creation_date AS snapshot_creation_date
        FROM articles
        LEFT JOIN article_versions
            ON article_versions.article_id = articles.id
        ORDER BY articles.creation_date DESC,
                 article_versions.version_number DESC
        """
    ).fetchall()


def article_exists(db, article_id: str) -> bool:
    return db.execute(
        "SELECT 1 FROM articles WHERE id = ?",
        (article_id,),
    ).fetchone() is not None


def unpublish_article(db, article_id: str) -> bool:
    cursor = db.execute(
        """
        UPDATE articles
        SET state_id = 3,
            draft_content = (
                SELECT content
                FROM article_versions
                WHERE article_versions.id = articles.current_snapshot_id
            )
        WHERE id = ? AND state_id = 2
        """,
        (article_id,),
    )
    return cursor.rowcount == 1


def get_article_for_publish(db, article_id: str):
    return db.execute(
        """
        SELECT articles.id,
               articles.title,
               articles.slug,
               articles.state_id,
               articles.draft_content,
               COALESCE(MAX(article_versions.version_number), 0) AS latest_version_number
        FROM articles
        LEFT JOIN article_versions
            ON article_versions.article_id = articles.id
        WHERE articles.id = ?
        GROUP BY articles.id
        """,
        (article_id,),
    ).fetchone()


def update_article_content(db, article_id: str, content: str) -> bool:
    cursor = db.execute(
        """
        UPDATE articles
        SET draft_content = ?
        WHERE id = ? AND state_id IN (1, 3)
        """,
        (content, article_id),
    )
    return cursor.rowcount == 1


def publish_article(
    db,
    article_id: str,
    version_id: str,
    version_number: int,
    content: str,
    creation_date: str,
) -> None:
    db.execute(
        """
        INSERT INTO article_versions
            (id, article_id, version_number, content, creation_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (version_id, article_id, version_number, content, creation_date),
    )
    db.execute(
        """
        UPDATE articles
        SET state_id = 2,
            current_snapshot_id = ?,
            draft_content = ?
        WHERE id = ?
        """,
        (version_id, content, article_id),
    )


def get_snapshot_delete_info(db, snapshot_id: str):
    return db.execute(
        """
        SELECT article_versions.id,
               articles.id AS article_id,
               articles.state_id,
               articles.current_snapshot_id,
               article_versions.version_number,
               (
                   SELECT MAX(version_number)
                   FROM article_versions AS latest_versions
                   WHERE latest_versions.article_id = article_versions.article_id
               ) AS latest_version_number
        FROM article_versions
        INNER JOIN articles
            ON articles.id = article_versions.article_id
        WHERE article_versions.id = ?
        """,
        (snapshot_id,),
    ).fetchone()


def delete_snapshot(db, snapshot_id: str, article_id: str) -> None:
    db.execute(
        """
        UPDATE articles
        SET current_snapshot_id = NULL
        WHERE id = ? AND current_snapshot_id = ?
        """,
        (article_id, snapshot_id),
    )
    db.execute(
        "DELETE FROM article_versions WHERE id = ?",
        (snapshot_id,),
    )


def list_article_snapshots(db, article_id: str):
    return db.execute(
        """
        SELECT id, version_number, content, creation_date
        FROM article_versions
        WHERE article_id = ?
        ORDER BY version_number DESC
        """,
        (article_id,),
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
    draft_content: str,
) -> None:
    db.execute(
        """
        INSERT INTO articles
            (id, title, state_id, slug, current_snapshot_id, creation_date, draft_content)
        VALUES (?, ?, ?, ?, NULL, ?, ?)
        """,
        (article_id, title, state_id, slug, creation_date, draft_content),
    )


def insert_article_version(
    db,
    version_id: str,
    article_id: str,
    version_number: int,
    content: str,
    creation_date: str,
) -> None:
    db.execute(
        """
        INSERT INTO article_versions
            (id, article_id, version_number, content, creation_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (version_id, article_id, version_number, content, creation_date),
    )


def set_current_snapshot(db, article_id: str, version_id: str) -> None:
    db.execute(
        "UPDATE articles SET current_snapshot_id = ? WHERE id = ?",
        (version_id, article_id),
    )
