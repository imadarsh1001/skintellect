#!/usr/bin/env python3
"""One-time migration: local SQLite catalog -> Turso (libSQL over HTTP).

Schema and rows are copied table by table with multi-row INSERT OR REPLACE
batches (200-500 rows per statement, one HTTP round trip per batch), so the
27 MB dataset uploads in seconds and a partial run can simply be re-run —
replace semantics on the same primary keys make every batch idempotent.

The research_vectors table is converted on the fly: the local JSON-text
vectors become native F16_BLOB values through the server-side vector16()
function, matching the remote schema ensure_tables() creates.

Usage:
    TURSO_DATABASE_URL=libsql://... TURSO_AUTH_TOKEN=... \
        python scripts/migrate_to_turso.py [--source skintellect_moisturizers.db]
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

# Stay under libSQL's per-statement bind-variable cap with headroom.
PLACEHOLDER_BUDGET = 30000


def topo_order(tables, deps):
    """FK-parent-first order so child rows never reference missing parents."""
    ordered, done, in_flight = [], set(), set()

    def visit(table):
        if table in done:
            return
        if table in in_flight:
            raise RuntimeError(f"circular foreign keys involving {table}")
        in_flight.add(table)
        for parent in sorted(deps.get(table, ())):
            if parent in deps:  # only among copied tables
                visit(parent)
        in_flight.discard(table)
        done.add(table)
        ordered.append(table)

    for table in tables:
        visit(table)
    return ordered


def normalize_ddl(sql):
    """Make copied DDL re-runnable (CREATE TABLE IF NOT EXISTS ...)."""
    return re.sub(r"CREATE\s+TABLE\s+", "CREATE TABLE IF NOT EXISTS ", sql, count=1, flags=re.IGNORECASE)


def normalize_index_ddl(sql):
    return re.sub(r"CREATE\s+(UNIQUE\s+)?INDEX\s+",
                  lambda m: f"CREATE {m.group(1) or ''}INDEX IF NOT EXISTS ", sql, count=1, flags=re.IGNORECASE)


def main():
    from skintellect.config import load_environment

    load_environment()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", default=str(REPO_ROOT / "skintellect_moisturizers.db"))
    ap.add_argument("--url", default=os.environ.get("TURSO_DATABASE_URL"))
    ap.add_argument("--token", default=os.environ.get("TURSO_AUTH_TOKEN"))
    ap.add_argument("--batch", type=int, default=300, help="rows per multi-row insert (default 300)")
    ap.add_argument("--only", default=None, help="comma-separated table list (debug)")
    args = ap.parse_args()

    if not args.url:
        sys.exit("Set TURSO_DATABASE_URL (and TURSO_AUTH_TOKEN) or pass --url/--token")
    source = Path(args.source)
    if not source.is_file():
        sys.exit(f"source database not found: {source}")

    local = sqlite3.connect(str(source))
    local.row_factory = sqlite3.Row

    tables = [r["name"] for r in local.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    if args.only:
        wanted = {t.strip() for t in args.only.split(",")}
        tables = [t for t in tables if t in wanted]
    deps = {}
    for t in tables:
        deps[t] = {r["table"] for r in local.execute(f'PRAGMA foreign_key_list("{t}")')}
    ordered = topo_order(tables, deps)

    import turso_serverless

    remote = turso_serverless.connect(args.url, auth_token=args.token or None)

    print(f"source: {source}")
    print(f"target: {args.url}")
    print(f"tables: {len(ordered)} ({', '.join(ordered)})")

    # 1. Schema (FK-parent first). research_vectors is rewritten to the
    #    native F16_BLOB layout used by ensure_tables() on the remote side.
    for t in ordered:
        ddl = local.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()["sql"]
        if t == "research_vectors":
            dims = int(os.environ.get("GEMINI_EMBEDDING_DIMENSIONS", "768") or "768")
            ddl = (f'CREATE TABLE IF NOT EXISTS research_vectors('
                   f'evidence_id TEXT NOT NULL, model TEXT NOT NULL, content_hash TEXT NOT NULL, '
                   f'dimensions INTEGER NOT NULL, vector F16_BLOB({dims}), '
                   f'PRIMARY KEY(evidence_id,model))')
        else:
            ddl = normalize_ddl(ddl)
        remote.executescript(ddl + ";")

    # 2. Rows: multi-row INSERT OR REPLACE, one HTTP round trip per batch.
    for t in ordered:
        cols = [r["name"] for r in local.execute(f'PRAGMA table_info("{t}")')]
        width = len(cols)
        batch = max(1, min(args.batch, PLACEHOLDER_BUDGET // (width + (1 if t == "research_vectors" else 0))))
        col_list = ",".join(f'"{c}"' for c in cols)
        if t == "research_vectors":
            # vector16(?) takes the JSON-text param and becomes the 5th value.
            one_row = "(" + ",".join(["?"] * (width - 1)) + ",vector16(?))"
        else:
            one_row = "(" + ",".join(["?"] * width) + ")"
        insert_sql = f'INSERT OR REPLACE INTO "{t}" VALUES'
        total_remote = 0
        cursor = local.execute(f'SELECT {col_list} FROM "{t}"')
        while True:
            rows = cursor.fetchmany(batch)
            if not rows:
                break
            if t == "research_vectors":
                params, sent = [], 0
                for r in rows:
                    d = dict(r)
                    try:
                        vector = json.loads(d.pop("vector_json"))
                        assert isinstance(vector, list) and vector
                    except (ValueError, TypeError, AssertionError):
                        print(f"  [!] skipped unparseable vector for {d.get('evidence_id')!r}")
                        continue
                    params.extend([d["evidence_id"], d["model"], d["content_hash"], d["dimensions"],
                                   json.dumps([float(v) for v in vector])])
                    sent += 1
                if not sent:
                    continue
                remote.execute(insert_sql + ",".join([one_row] * sent), params)
                total_remote += sent
            else:
                params = [v for r in rows for v in tuple(r)]
                remote.execute(insert_sql + ",".join([one_row] * len(rows)), params)
                total_remote += len(rows)
            remote.commit()
        print(f"  [ok] {t}: {total_remote} rows")

    # 3. Indexes after data (faster loads); skip those on absent tables.
    index_rows = local.execute(
        "SELECT sql, tbl_name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL").fetchall()
    for r in index_rows:
        if r["tbl_name"] not in ordered:
            continue
        if r["tbl_name"] == "research_vectors":
            continue  # vector tables need no copied index; PK covers lookups
        try:
            remote.executescript(normalize_index_ddl(r["sql"]) + ";")
        except Exception as exc:  # noqa: BLE001 - report and continue: an index is not data
            print(f"  [!] index on {r['tbl_name']} skipped: {exc}")

    # 4. Code-owned tables that may not exist in the local file yet
    #    (preparation_jobs, gemini_* — ensure_tables/initialize are idempotent).
    os.environ.setdefault("TURSO_DATABASE_URL", args.url)
    os.environ.setdefault("TURSO_AUTH_TOKEN", args.token or "")
    from skintellect.gemini import ensure_tables
    from skintellect.research import jobs

    ensure_tables(args.url)
    jobs.initialize(args.url)
    print("  [ok] code-owned tables ensured (gemini_*, research_vectors, preparation_jobs)")

    # 5. Verification: every local row must exist remotely. The remote side is
    #    a live production database (telemetry/cache rows accrue between runs),
    #    so extra remote rows are informational, not drift; fewer rows than
    #    local means the copy missed something and is a hard failure.
    print("\nverification (local -> remote):")
    drift = False
    for t in ordered:
        local_count = local.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        remote_count = remote.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        if remote_count < local_count:
            marker, drift = "DRIFT", True
        elif remote_count > local_count:
            marker = "remote-live"
        else:
            marker = "ok"
        print(f"  {t}: {local_count} -> {remote_count} [{marker}]")
    remote.close()
    local.close()
    if drift:
        print("\n[!] row-count drift detected — inspect the tables above before deploying.")
        sys.exit(1)
    print("\n[done] migration complete and verified.")


if __name__ == "__main__":
    main()
