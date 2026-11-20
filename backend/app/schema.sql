-- NorthBeam Docs Studio database schema.
-- UUIDs are stored as TEXT and timestamps as ISO-8601 TEXT values because
-- SQLite does not provide native UUID or datetime types.

CREATE TABLE IF NOT EXISTS states (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    state_id TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    current_snapshot_id TEXT,
    creation_date TEXT NOT NULL,
    FOREIGN KEY (state_id) REFERENCES states (id),
    FOREIGN KEY (current_snapshot_id) REFERENCES article_versions (id)
);

CREATE TABLE IF NOT EXISTS article_versions (
    id TEXT PRIMARY KEY NOT NULL,
    article_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    creation_date TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
    UNIQUE (article_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_article_versions_article_id
    ON article_versions (article_id);

CREATE INDEX IF NOT EXISTS idx_articles_state_id
    ON articles (state_id);

-- Static article states.
INSERT OR IGNORE INTO states (id, name) VALUES
    (1, 'Draft'),
    (2, 'Published'),
    (3, 'UnPublished');
