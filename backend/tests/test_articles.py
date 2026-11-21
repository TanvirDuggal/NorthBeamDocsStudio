"""Tests for the writer article API."""


def create_article(client, *, title="My Article", content="# Hello", state_id=1, tags="be, fe"):
    return client.post(
        "/api/writer/article",
        json={
            "title": title,
            "content": content,
            "state_id": state_id,
            "tags": tags,
        },
    )


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_create_draft_stores_tags_without_creating_snapshot(client):
    response = create_article(client, state_id=1, content="# Draft")

    assert response.status_code == 201
    article = response.json
    assert article["state_id"] == 1
    assert article["version_id"] is None
    assert article["tags"] == "be, fe"

    all_articles = client.get("/api/writer/article/all")
    assert all_articles.status_code == 200
    assert all_articles.json[0]["snapshots"] == []
    assert all_articles.json[0]["tags"] == "be, fe"


def test_create_published_article_creates_version_one(client):
    response = create_article(client, state_id=2, content="# Published")

    assert response.status_code == 201
    assert response.json["version_id"]

    articles = client.get("/api/writer/article").json
    assert len(articles) == 1
    assert articles[0]["content"] == "# Published"
    assert articles[0]["tags"] == "be, fe"

    all_articles = client.get("/api/writer/article/all").json
    assert all_articles[0]["snapshots"][0]["version_number"] == 1
    assert all_articles[0]["snapshots"][0]["content"] == "# Published"


def test_required_validation(client):
    assert client.post("/api/writer/article", json={"content": "x", "state_id": 1}).status_code == 400
    assert client.post("/api/writer/article", json={"title": "", "content": "x", "state_id": 1}).status_code == 400
    assert client.post("/api/writer/article", json={"title": "x", "state_id": 1}).status_code == 400
    assert client.post("/api/writer/article", json={"title": "x", "content": "x", "state_id": 3}).status_code == 400
    assert client.post("/api/writer/article", json={"title": "x", "content": "x", "state_id": 1, "tags": ["be"]}).status_code == 400


def test_duplicate_titles_receive_incremented_slugs(client):
    first = create_article(client, title="My Life")
    second = create_article(client, title="My Life")
    third = create_article(client, title="My Life")

    assert first.json["slug"] == "my_life"
    assert second.json["slug"] == "my_life_2"
    assert third.json["slug"] == "my_life_3"


def test_unpublish_preserves_snapshot_and_copies_editable_content(client):
    created = create_article(client, state_id=2, content="# Live")
    article_id = created.json["id"]

    response = client.post(f"/api/writer/article/{article_id}/unpublish")

    assert response.status_code == 200
    assert response.json["state_id"] == 3
    assert client.get("/api/writer/article").json == []
    article = client.get("/api/writer/article/all").json[0]
    assert len(article["snapshots"]) == 1
    assert article["snapshots"][0]["content"] == "# Live"


def test_edit_then_publish_creates_next_snapshot(client):
    created = create_article(client, state_id=2, content="# Version 1")
    article_id = created.json["id"]
    client.post(f"/api/writer/article/{article_id}/unpublish")

    edit = client.patch(
        f"/api/writer/article/{article_id}",
        json={"content": "# Version 2", "tags": "updated, docs"},
    )
    assert edit.status_code == 200
    assert edit.json["tags"] == "updated, docs"

    publish = client.post(f"/api/writer/article/{article_id}/publish")
    assert publish.status_code == 200
    assert publish.json["version_number"] == 2

    snapshots = client.get(f"/api/writer/article/all").json[0]["snapshots"]
    assert [snapshot["version_number"] for snapshot in snapshots] == [2, 1]
    assert snapshots[0]["content"] == "# Version 2"


def test_published_article_cannot_be_edited_directly(client):
    created = create_article(client, state_id=2)

    response = client.patch(
        f"/api/writer/article/{created.json['id']}",
        json={"content": "changed"},
    )

    assert response.status_code == 400


def test_latest_snapshot_cannot_be_deleted_but_older_snapshot_can(client):
    created = create_article(client, state_id=2, content="one")
    article_id = created.json["id"]
    client.post(f"/api/writer/article/{article_id}/unpublish")
    client.patch(f"/api/writer/article/{article_id}", json={"content": "two"})
    client.post(f"/api/writer/article/{article_id}/publish")

    snapshots = client.get("/api/writer/article/all").json[0]["snapshots"]
    latest_id = snapshots[0]["id"]
    older_id = snapshots[1]["id"]

    assert client.delete(f"/api/writer/article/snapshot/{latest_id}").status_code == 400
    delete_older = client.delete(f"/api/writer/article/snapshot/{older_id}")
    assert delete_older.status_code == 200
    assert len(client.get("/api/writer/article/all").json[0]["snapshots"]) == 1


def test_missing_article_and_snapshot_return_404(client):
    missing_id = "00000000-0000-0000-0000-000000000000"

    assert client.post(f"/api/writer/article/{missing_id}/unpublish").status_code == 404
    assert client.patch(f"/api/writer/article/{missing_id}", json={"content": "x"}).status_code == 404
    assert client.post(f"/api/writer/article/{missing_id}/publish").status_code == 404
    assert client.delete(f"/api/writer/article/snapshot/{missing_id}").status_code == 404
