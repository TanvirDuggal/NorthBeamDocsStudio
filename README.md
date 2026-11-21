# Northbeam Docs Studio

A documentation application built with Vue 3, Python Flask,
and SQLite. Writers can manage drafts and version history;
public readers see only published content.

## Technology Stack

- Python
- Flask
- Vue 3
- SQLite

## Running the Application

Run the backend and frontend in two separate terminals.

### Start the Backend

Open a terminal in the `backend` folder, activate your Python
virtual environment if applicable, and run:

```bash
python run.py
```

### Start the Frontend

Open another terminal in the `frontend` folder and run:

```bash
npm run dev
```

## Running Tests

From the `backend` folder, with the virtual environment activated:

```bash
python -m pytest -q
```

### Open the Application

Open the local URL displayed by the frontend terminal in your
browser. Keep both terminals running while using the application.

To stop either server, press `Ctrl+C` in its terminal.


## Database Model

The application uses SQLite with three tables.

### states

Stores the fixed publication states of an article.

| Field | Description |
|---|---|
| id | State identifier: 1 = Draft, 2 = Published, 3 = UnPublished |
| name | State name |

### articles

Stores the article identity, editable draft, and publication state.

| Field | Description |
|---|---|
| id | Backend-generated article UUID |
| title | Article title, fixed after creation |
| state_id | Foreign key referencing states.id |
| slug | Lowercase, URL-friendly article identifier |
| current_snapshot_id | Reference to the current or last published snapshot |
| creation_date | Article creation timestamp |
| draft_content | Editable working content, including after publication |

### article_versions

Stores immutable content snapshots created when publishing.

| Field | Description |
|---|---|
| id | Backend-generated snapshot UUID |
| article_id | Foreign key referencing articles.id |
| version_number | Sequential snapshot number within the article |
| content | Content captured when published |
| creation_date | Snapshot creation timestamp |

### Design Rationale

Draft content is stored separately from published snapshots so writers
can edit without changing what readers see. Publishing creates a new
snapshot and updates the article's publication reference. Earlier
snapshots remain unchanged.

Publication status belongs to the article, not individual snapshots.
Unpublishing hides the article publicly while preserving its last
published snapshot reference.

## API Reference

Base URL:

```text
http://127.0.0.1:5000
```

For requests with a JSON body, use:

```text
Content-Type: application/json
```

### Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Check backend availability |
| POST | /api/writer/article | Create an article |
| GET | /api/writer/article | Return published articles for readers |
| GET | /api/writer/article/all | Return all articles and their snapshots |
| PATCH | /api/writer/article/{articleID} | Update a Draft or UnPublished article |
| POST | /api/writer/article/{articleID}/publish | Publish the draft as a new snapshot |
| POST | /api/writer/article/{articleID}/unpublish | Unpublish an article while preserving snapshots |
| DELETE | /api/writer/article/snapshot/{snapshotID} | Delete an eligible snapshot |

articleID and snapshotID are backend-generated UUIDs.

### Create Article

POST /api/writer/article

```json
{
  "title": "My Article",
  "content": "# My Article\n\nArticle content here.",
  "tags": "be, fe, api",
  "state_id": 1
}
```

State identifiers:

| Value | State |
|---|---|
| 1 | Draft |
| 2 | Published |
| 3 | UnPublished |

### Update Article

PATCH /api/writer/article/{articleID}

```json
{
  "content": "# Updated content",
  "tags": "be, updated"
}
```

The current implementation permits updates only when the article
is Draft or UnPublished.

### Publish Article

POST /api/writer/article/{articleID}/publish

No request body is required.

Creates the next numbered snapshot from the saved draft and
sets the article state to Published.

### Unpublish Article

POST /api/writer/article/{articleID}/unpublish

No request body is required.

Sets the article state to UnPublished and preserves its snapshots.

### Delete Snapshot

DELETE /api/writer/article/snapshot/{snapshotID}

No request body is required.

The latest snapshot cannot be deleted.

### GET Requests

GET requests do not require a body.

- GET /health checks backend availability.
- GET /api/writer/article returns published articles for readers.
- GET /api/writer/article/all returns all articles and their snapshots.


## Tradeoff

I chose SQLite to keep local setup simple and avoid requiring
a separate database server. This suits the assignment's small,
local scope, but SQLite serializes writes. If the application
needed to support significantly more concurrent writers,
I would evaluate PostgreSQL and test the transaction behavior
under that workload.

Given the time budget, I prioritized the core article lifecycle, data integrity, and automated tests. With more time, I would add an optional LLM writing assistant to review drafts and suggest improvements to grammar, clarity, tone, and structure. Writers would review and accept suggestions before applying them to the draft, with publishing remaining an explicit action. This would also require handling API failures, protecting draft privacy, and ensuring the application works without an LLM connection.