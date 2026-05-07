"""SQLite-backed CRUD for documents and their versions."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from uuid import uuid4

from .db import connect
from .models import (
    DocumentDetail,
    DocumentRow,
    DocumentSummary,
    NdaFormValues,
    VersionRow,
)


class DocumentNotFound(Exception):
    pass


def _now_iso() -> str:
    # Microsecond precision keeps documents created in the same second
    # deterministically ordered by updated_at.
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _row_to_document(row: sqlite3.Row) -> DocumentRow:
    return DocumentRow(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_version(row: sqlite3.Row) -> VersionRow:
    return VersionRow(
        id=row["id"],
        document_id=row["document_id"],
        version_number=row["version_number"],
        data=NdaFormValues.model_validate_json(row["data"]),
        rendered_markdown=row["rendered_markdown"],
        created_at=row["created_at"],
    )


@contextmanager
def _transaction(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Open a connection, BEGIN IMMEDIATE, COMMIT on success, ROLLBACK on error."""
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except Exception:
        # Best-effort rollback; never let it mask the original exception.
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


@contextmanager
def _reader(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def create_document(
    db_path: Path, values: NdaFormValues, rendered_markdown: str
) -> tuple[str, str, int]:
    document_id = str(uuid4())
    version_id = str(uuid4())
    now = _now_iso()
    with _transaction(db_path) as conn:
        conn.execute(
            "INSERT INTO documents (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (document_id, values.title, now, now),
        )
        conn.execute(
            "INSERT INTO versions "
            "(id, document_id, version_number, data, rendered_markdown, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                version_id,
                document_id,
                1,
                values.model_dump_json(by_alias=True),
                rendered_markdown,
                now,
            ),
        )
    return document_id, version_id, 1


def add_version(
    db_path: Path,
    document_id: str,
    values: NdaFormValues,
    rendered_markdown: str,
) -> tuple[str, int]:
    """Append a new version. Race-safe: BEGIN IMMEDIATE serializes writers."""
    version_id = str(uuid4())
    now = _now_iso()
    with _transaction(db_path) as conn:
        row = conn.execute(
            "SELECT version_number FROM versions WHERE document_id = ? "
            "ORDER BY version_number DESC LIMIT 1",
            (document_id,),
        ).fetchone()
        if row is None:
            raise DocumentNotFound(document_id)
        version_number = row["version_number"] + 1
        conn.execute(
            "INSERT INTO versions "
            "(id, document_id, version_number, data, rendered_markdown, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                version_id,
                document_id,
                version_number,
                values.model_dump_json(by_alias=True),
                rendered_markdown,
                now,
            ),
        )
        conn.execute(
            "UPDATE documents SET title = ?, updated_at = ? WHERE id = ?",
            (values.title, now, document_id),
        )
    return version_id, version_number


def get_document(db_path: Path, document_id: str) -> DocumentRow | None:
    with _reader(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?", (document_id,)
        ).fetchone()
    return _row_to_document(row) if row else None


def list_documents(db_path: Path) -> list[DocumentSummary]:
    sql = """
        SELECT d.*, v.version_number AS latest_version_number,
               v.id AS latest_version_id
        FROM documents d
        JOIN versions v ON v.document_id = d.id
        WHERE v.version_number = (
            SELECT MAX(version_number) FROM versions WHERE document_id = d.id
        )
        ORDER BY d.updated_at DESC
    """
    with _reader(db_path) as conn:
        rows = conn.execute(sql).fetchall()
    return [
        DocumentSummary(
            id=r["id"],
            title=r["title"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            latest_version_number=r["latest_version_number"],
            latest_version_id=r["latest_version_id"],
        )
        for r in rows
    ]


def get_latest_version(db_path: Path, document_id: str) -> VersionRow | None:
    with _reader(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM versions WHERE document_id = ? "
            "ORDER BY version_number DESC LIMIT 1",
            (document_id,),
        ).fetchone()
    return _row_to_version(row) if row else None


def list_versions(db_path: Path, document_id: str) -> list[VersionRow]:
    with _reader(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM versions WHERE document_id = ? "
            "ORDER BY version_number DESC",
            (document_id,),
        ).fetchall()
    return [_row_to_version(r) for r in rows]


def get_version(
    db_path: Path, document_id: str, version_id: str
) -> VersionRow | None:
    with _reader(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM versions WHERE document_id = ? AND id = ?",
            (document_id, version_id),
        ).fetchone()
    return _row_to_version(row) if row else None


def get_document_detail(db_path: Path, document_id: str) -> DocumentDetail | None:
    document = get_document(db_path, document_id)
    if document is None:
        return None
    latest = get_latest_version(db_path, document_id)
    if latest is None:
        return None
    return DocumentDetail(document=document, latest_version=latest)
