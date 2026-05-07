"""SQLite connection helpers and one-time schema initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS versions (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    data TEXT NOT NULL,
    rendered_markdown TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (document_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_versions_document
    ON versions(document_id, version_number DESC);
"""


def init_db(path: Path) -> None:
    """Create the SQLite file (if missing), enable WAL, and apply the schema."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(_SCHEMA)


def connect(path: Path) -> sqlite3.Connection:
    """Open a per-request connection. Caller closes it (or uses `with`)."""
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
