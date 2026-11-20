"""Writer article routes."""

from datetime import datetime, timezone
import re
import unicodedata
from uuid import uuid4

from flask import Blueprint, jsonify, request

from ..db import get_db
from ..queries.articles import article_exists
from ..queries.articles import insert_article
from ..queries.articles import insert_article_version
from ..queries.articles import list_article_snapshots
from ..queries.articles import list_published_articles
from ..queries.articles import set_current_snapshot
from ..queries.articles import slug_exists


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
            db, article_id, title.strip(), state_id, slug, created_at
        )

        if state_id == 2:
            version_id = str(uuid4())
            insert_article_version(
                db, version_id, article_id, content, created_at
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
