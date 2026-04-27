"""Database helpers for local SQLite and Render Postgres."""
import json
import os
import re
import sqlite3
from contextlib import contextmanager


DEFAULT_TABLE_NAME = "benchmark_questions"
TABLE_NAME = os.environ.get("TABLE_NAME", DEFAULT_TABLE_NAME).strip() or DEFAULT_TABLE_NAME
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", TABLE_NAME):
    raise ValueError("TABLE_NAME must contain only letters, numbers, and underscores, and not start with a number")

SQLITE_DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_bench.db"),
)
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
IS_POSTGRES = bool(DATABASE_URL)

SQLITE_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    track                 TEXT    NOT NULL,
    title                 TEXT    NOT NULL,
    difficulty            TEXT    NOT NULL,
    domain                TEXT    NOT NULL,
    subdomain             TEXT,
    content               TEXT    NOT NULL,
    rubric_json           TEXT    NOT NULL,
    reference_answer      TEXT,
    source_type           TEXT    NOT NULL,
    source_detail         TEXT,
    author_name           TEXT    NOT NULL,
    author_institution    TEXT    NOT NULL,
    author_email          TEXT    NOT NULL,
    status                TEXT    NOT NULL DEFAULT 'pending',
    submitted_at          TEXT    NOT NULL,
    updated_at            TEXT    NOT NULL,
    reviewed_at           TEXT,
    reviewer_name         TEXT,
    reviewer_institution  TEXT,
    review_comment        TEXT,
    revision_reasons_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_status     ON {TABLE_NAME}(status);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_track      ON {TABLE_NAME}(track);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_domain     ON {TABLE_NAME}(domain);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_difficulty ON {TABLE_NAME}(difficulty);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_author     ON {TABLE_NAME}(author_name);
"""

POSTGRES_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id                    BIGSERIAL PRIMARY KEY,
    track                 TEXT    NOT NULL,
    title                 TEXT    NOT NULL,
    difficulty            TEXT    NOT NULL,
    domain                TEXT    NOT NULL,
    subdomain             TEXT,
    content               TEXT    NOT NULL,
    rubric_json           TEXT    NOT NULL,
    reference_answer      TEXT,
    source_type           TEXT    NOT NULL,
    source_detail         TEXT,
    author_name           TEXT    NOT NULL,
    author_institution    TEXT    NOT NULL DEFAULT '',
    author_email          TEXT    NOT NULL DEFAULT '',
    status                TEXT    NOT NULL DEFAULT 'pending',
    submitted_at          TEXT    NOT NULL,
    updated_at            TEXT    NOT NULL,
    reviewed_at           TEXT,
    reviewer_name         TEXT,
    reviewer_institution  TEXT,
    review_comment        TEXT,
    revision_reasons_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_status     ON {TABLE_NAME}(status);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_track      ON {TABLE_NAME}(track);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_domain     ON {TABLE_NAME}(domain);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_difficulty ON {TABLE_NAME}(difficulty);
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_author     ON {TABLE_NAME}(author_name);
"""


def _translate_query(query: str) -> str:
    if not IS_POSTGRES:
        return query
    return query.replace("?", "%s")


class ResultAdapter:
    def __init__(self, cursor, is_postgres: bool):
        self.cursor = cursor
        self.is_postgres = is_postgres
        self.lastrowid = getattr(cursor, "lastrowid", None)

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row) if self.is_postgres else row

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows] if self.is_postgres else rows


class ConnectionAdapter:
    def __init__(self, conn, is_postgres: bool):
        self.conn = conn
        self.is_postgres = is_postgres

    def execute(self, query: str, params=()):
        if self.is_postgres:
            cursor = self.conn.cursor()
            cursor.execute(_translate_query(query), params)
            return ResultAdapter(cursor, True)
        cursor = self.conn.execute(query, params)
        return ResultAdapter(cursor, False)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def _postgres_connect():
    import psycopg
    from psycopg.rows import dict_row

    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    if IS_POSTGRES:
        conn = _postgres_connect()
        try:
            with conn.cursor() as cur:
                for statement in [part.strip() for part in POSTGRES_SCHEMA.split(";") if part.strip()]:
                    cur.execute(statement)
            conn.commit()
        finally:
            conn.close()
        return

    with sqlite3.connect(SQLITE_DB_PATH) as conn:
        conn.executescript(SQLITE_SCHEMA)


@contextmanager
def get_db():
    if IS_POSTGRES:
        adapter = ConnectionAdapter(_postgres_connect(), True)
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        adapter = ConnectionAdapter(conn, False)

    try:
        yield adapter
        adapter.commit()
    except Exception:
        adapter.rollback()
        raise
    finally:
        adapter.close()


def row_to_dict(row) -> dict:
    d = dict(row)
    if d.get("rubric_json"):
        d["rubric"] = json.loads(d["rubric_json"])
    if d.get("revision_reasons_json"):
        d["revision_reasons"] = json.loads(d["revision_reasons_json"])
    else:
        d["revision_reasons"] = []
    d.pop("rubric_json", None)
    d.pop("revision_reasons_json", None)
    return d
