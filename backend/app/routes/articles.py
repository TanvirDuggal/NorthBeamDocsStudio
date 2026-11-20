"""Writer article routes."""

from datetime import datetime, timezone
import re
import unicodedata
from uuid import uuid4

from flask import Blueprint, jsonify, request

from ..db import get_db
from ..queries.articles import article_exists
from ..queries.articles import delete_snapshot
from ..queries.articles import get_snapshot_delete_info
from ..queries.articles import get_article_for_publish
from ..queries.articles import insert_article
from ..queries.articles import insert_article_version
from ..queries.articles import list_all_articles_with_snapshots
from ..queries.articles import list_article_snapshots
from ..queries.articles import list_published_articles
from ..queries.articles import publish_article
from ..queries.articles import set_current_snapshot
from ..queries.articles import slug_exists
from ..queries.articles import update_article_content
from ..queries.articles import unpublish_article


articles_bp = Blueprint("articles", __name__, url_prefix="/api/writer")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_slug(title: str) -> str:
    ascii_title = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    slug = re.sub(r"\s+", "_", ascii_title)
    return re.sub(r"[^a-z0-9_]", "", slug).strip("_")


def _unique_slug(db, base_slug: str) -> str:
    slug = base_slug
    suffix = 2
    while slug_exists(db, slug):
        slug = f"{base_slug}_{suffix}"
        suffix += 1
    return slug


@articles_bp.get("/article")
def list_articles():
    articles = list_published_articles(get_db())
    return jsonify(
        [
            {
                "title": article["title"],
                "content": article["content"],
                "creation_date": article["creation_date"],
                "slug": article["slug"],
            }
            for article in articles
        ]
    )


@articles_bp.get("/article/all")
def list_all_articles():
    rows = list_all_articles_with_snapshots(get_db())
    articles = {}

    for row in rows:
        article = articles.setdefault(
            row["id"],
            {
                "id": row["id"],
                "title": row["title"],
                "slug": row["slug"],
                "state_id": row["state_id"],
                "creation_date": row["creation_date"],
                "snapshots": [],
            },
        )
        if row["snapshot_id"] is not None:
            article["snapshots"].append(
                {
                    "id": row["snapshot_id"],
                    "version_number": row["version_number"],
                    "content": row["snapshot_content"],
                    "creation_date": row["snapshot_creation_date"],
                }
            )

    return jsonify(list(articles.values()))


@articles_bp.get("/article/<article_id>")
def get_article_snapshots(article_id: str):
    db = get_db()
    if not article_exists(db, article_id):
        return jsonify({"error": "Article not found."}), 404

    snapshots = list_article_snapshots(db, article_id)
    return jsonify(
        [
            {
                "id": snapshot["id"],
                "version_number": snapshot["version_number"],
                "content": snapshot["content"],
                "creation_date": snapshot["creation_date"],
            }
            for snapshot in snapshots
        ]
    )


@articles_bp.post("/article/<article_id>/unpublish")
def unpublish(article_id: str):
    db = get_db()
    if not article_exists(db, article_id):
        return jsonify({"error": "Article not found."}), 404

    with db:
        if not unpublish_article(db, article_id):
            return jsonify({"error": "Only published articles can be unpublished."}), 400

    return jsonify({"id": article_id, "state_id": 3})


@articles_bp.patch("/article/<article_id>")
def update_article(article_id: str):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("content"), str):
        return jsonify({"error": "content is required and must be a string."}), 400

    db = get_db()
    article = get_article_for_publish(db, article_id)
    if article is None:
        return jsonify({"error": "Article not found."}), 404
    if int(article["state_id"]) == 2:
        return jsonify({"error": "Published articles must be unpublished before editing."}), 400

    with db:
        update_article_content(db, article_id, payload["content"])

    return jsonify(
        {
            "id": article_id,
            "title": article["title"],
            "slug": article["slug"],
            "state_id": int(article["state_id"]),
            "content": payload["content"],
        }
    )


@articles_bp.post("/article/<article_id>/publish")
def publish_existing_article(article_id: str):
    db = get_db()
    article = get_article_for_publish(db, article_id)
    if article is None:
        return jsonify({"error": "Article not found."}), 404
    if int(article["state_id"]) == 2:
        return jsonify({"error": "Article is already published."}), 400

    version_id = str(uuid4())
    published_at = _utc_now()
    version_number = int(article["latest_version_number"]) + 1

    with db:
        publish_article(
            db,
            article_id,
            version_id,
            version_number,
            article["draft_content"],
            published_at,
        )

    return jsonify(
        {
            "id": article_id,
            "title": article["title"],
            "slug": article["slug"],
            "state_id": 2,
            "version_id": version_id,
            "version_number": version_number,
        }
    )


@articles_bp.delete("/article/snapshot/<snapshot_id>")
def delete_article_snapshot(snapshot_id: str):
    db = get_db()
    snapshot = get_snapshot_delete_info(db, snapshot_id)
    if snapshot is None:
        return jsonify({"error": "Snapshot not found."}), 404

    if snapshot["version_number"] == snapshot["latest_version_number"]:
        return jsonify({"error": "The latest snapshot cannot be deleted."}), 400

    if int(snapshot["state_id"]) == 2 and snapshot["current_snapshot_id"] == snapshot_id:
        return jsonify({"error": "The current snapshot of a published article cannot be deleted."}), 400

    with db:
        delete_snapshot(db, snapshot_id, snapshot["article_id"])

    return jsonify({"id": snapshot_id, "deleted": True})


@articles_bp.post("/article/replace")
def replace_published_article():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    previous_article_id = payload.get("previous_article_id")
    title = payload.get("title")
    content = payload.get("content")
    if not isinstance(previous_article_id, str) or not previous_article_id:
        return jsonify({"error": "previous_article_id is required."}), 400
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required."}), 400
    if not isinstance(content, str):
        return jsonify({"error": "content must be a string."}), 400

    db = get_db()
    previous_article = get_article_for_publish(db, previous_article_id)
    if previous_article is None:
        return jsonify({"error": "Previous article not found."}), 404
    if int(previous_article["state_id"]) != 2:
        return jsonify({"error": "Previous article must be published."}), 400

    slug = _unique_slug(db, _make_slug(title.strip()))
    if not slug:
        return jsonify({"error": "title must contain letters or numbers."}), 400

    article_id = str(uuid4())
    version_id = str(uuid4())
    created_at = _utc_now()

    with db:
        unpublish_article(db, previous_article_id)
        insert_article(
            db, article_id, title.strip(), 2, slug, created_at, content
        )
        insert_article_version(
            db, version_id, article_id, 1, content, created_at
        )
        set_current_snapshot(db, article_id, version_id)

    return jsonify(
        {
            "id": article_id,
            "title": title.strip(),
            "slug": slug,
            "state_id": 2,
            "version_id": version_id,
            "previous_article_id": previous_article_id,
        }
    ), 201


@articles_bp.post("/article")
def create_article():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    title = payload.get("title")
    content = payload.get("content")
    state_id = payload.get("state_id")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required."}), 400
    if not isinstance(content, str):
        return jsonify({"error": "content must be a string."}), 400
    if state_id not in (1, 2):
        return jsonify({"error": "state_id must be 1 (Draft) or 2 (Published)."}), 400

    db = get_db()
    slug = _unique_slug(db, _make_slug(title.strip()))
    if not slug:
        return jsonify({"error": "title must contain letters or numbers."}), 400

    article_id = str(uuid4())
    created_at = _utc_now()
    version_id = None

    with db:
        insert_article(
            db, article_id, title.strip(), state_id, slug, created_at, content
        )

        if state_id == 2:
            version_id = str(uuid4())
            insert_article_version(
                db, version_id, article_id, 1, content, created_at
            )
            set_current_snapshot(db, article_id, version_id)

    return jsonify(
        {
            "id": article_id,
            "title": title.strip(),
            "slug": slug,
            "state_id": state_id,
            "creation_date": created_at,
            "version_id": version_id,
        }
    ), 201
