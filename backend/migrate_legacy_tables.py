"""Migrate legacy CGT/Protein tables into benchmark_questions."""

import argparse
import json

from db import IS_POSTGRES, TABLE_NAME, get_db, init_db


LEGACY_SOURCES = {
    "cgt": "cgt_questions",
    "protein": "protein_questions",
}


def migrate_track(conn, track: str, source_table: str, dry_run: bool = False):
    rows = conn.execute(f"SELECT * FROM {source_table}").fetchall()
    inserted = 0
    skipped = 0

    for row in rows:
        item = dict(row)
        exists = conn.execute(
            f"""
            SELECT id
            FROM {TABLE_NAME}
            WHERE track = ? AND title = ? AND author_name = ? AND submitted_at = ?
            LIMIT 1
            """,
            (
                track,
                item["title"],
                item["author_name"],
                item["submitted_at"],
            ),
        ).fetchone()
        if exists:
            skipped += 1
            continue

        inserted += 1
        if dry_run:
            continue

        conn.execute(
            f"""
            INSERT INTO {TABLE_NAME} (
                track,
                title, difficulty, domain, subdomain, content,
                rubric_json, reference_answer, source_type, source_detail,
                author_name, author_institution, author_email,
                status, submitted_at, updated_at, reviewed_at,
                reviewer_name, reviewer_institution, review_comment, revision_reasons_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                track,
                item["title"],
                item["difficulty"],
                item["domain"],
                item.get("subdomain"),
                item["content"],
                item["rubric_json"],
                item.get("reference_answer"),
                item["source_type"],
                item.get("source_detail"),
                item["author_name"],
                item.get("author_institution") or "",
                item.get("author_email") or "",
                item["status"],
                item["submitted_at"],
                item["updated_at"],
                item.get("reviewed_at"),
                item.get("reviewer_name"),
                item.get("reviewer_institution"),
                item.get("review_comment"),
                item.get("revision_reasons_json") or json.dumps([], ensure_ascii=False),
            ),
        )

    return {
        "track": track,
        "source_table": source_table,
        "source_rows": len(rows),
        "inserted": inserted,
        "skipped": skipped,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        choices=("cgt", "protein", "all"),
        default="cgt",
        help="Which legacy table to migrate",
    )
    parser.add_argument("--dry-run", action="store_true", help="Count only; do not insert")
    args = parser.parse_args()

    if not IS_POSTGRES:
        raise SystemExit("DATABASE_URL is not set. Run this script in the Render env or export DATABASE_URL first.")

    init_db()
    tracks = LEGACY_SOURCES.items() if args.source == "all" else [(args.source, LEGACY_SOURCES[args.source])]

    results = []
    with get_db() as conn:
        for track, source_table in tracks:
            results.append(migrate_track(conn, track, source_table, dry_run=args.dry_run))

    for result in results:
        print(result)


if __name__ == "__main__":
    main()
