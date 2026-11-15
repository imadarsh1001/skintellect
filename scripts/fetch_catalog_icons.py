#!/usr/bin/env python
"""Fetch the catalog's scraped attribute icons locally.

Two icon families ship inside the raw catalog JSON, both hosted on
assets.skinsort.com and both small bounded vocabularies:

- ``key-actives``  — the ``icon`` key on ``key_actives_json`` entries
  (41 distinct SVGs), rendered on product cards and the comparison matrix.
- ``ingredients``  — the ``icon_url`` key inside each ingredient's
  ``icons`` list (product ``ingredients_json`` payloads and the
  ingredients data file; 53 distinct SVGs naming benefits like
  "Helps hydrate Dry Skin"), rendered in the product detail modal.

This script downloads every referenced SVG once into
``frontend/public/icons/<family>/<name>.svg`` so the UI serves local
copies instead of hotlinking a third-party host, and writes a
``manifest.json`` per family (name -> source URL + sha256) for
provenance.

Re-run any time the collector syncs new data: existing files are kept
unless ``--refresh`` is passed, so each run only fetches the delta.
Successful downloads are recorded even when siblings fail, so a re-run
retries only what failed. Exit codes: 0 ok, 1 download failures, 2
missing/empty source.

Usage:
    python scripts/fetch_catalog_icons.py [--source <json> ...] [--refresh]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = [
    ROOT / "data" / "raw" / "skinsort_moisturizers.json",
    ROOT / "data" / "raw" / "skinsort_ingredients.json",
]
ICON_ROOT = ROOT / "frontend" / "public" / "icons"

KEY_ACTIVE_RE = re.compile(r'"icon"\s*:\s*"(https://assets\.skinsort\.com[^"\\]+)"')
INGREDIENT_RE = re.compile(r'"icon_url"\s*:\s*"(https://assets\.skinsort\.com[^"\\]+)"')

# family name -> (URL regex, destination dir under frontend/public/icons)
KINDS: list[tuple[str, re.Pattern[str], Path]] = [
    ("key-actives", KEY_ACTIVE_RE, ICON_ROOT / "key-actives"),
    ("ingredients", INGREDIENT_RE, ICON_ROOT / "ingredients"),
]

# .../icons/v2/<name>-<hash>.svg -> <name>.svg
HASH_SUFFIX_RE = re.compile(r"-[0-9a-f]{8,}\.svg$")


def local_name(url: str) -> str:
    # This slug rule is mirrored in the frontend at
    # frontend/src/lib/utils.ts localIconPath(); change both together or
    # icons silently vanish.
    base = url.rsplit("/", 1)[-1]
    return HASH_SUFFIX_RE.sub(".svg", base)


def extract_urls(sources: list[Path], pattern: re.Pattern[str]) -> dict[str, str]:
    """name -> source URL for every match across the source files."""
    urls: dict[str, str] = {}
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            urls.setdefault(local_name(match.group(1)), match.group(1))
    return urls


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "skintellect-icon-fetch/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    if b"<svg" not in body[:400]:
        raise ValueError(f"not an SVG: {url} starts with {body[:60]!r}")
    return body


def fetch_family(kind: str, pattern: re.Pattern[str], dest: Path, sources: list[Path], refresh: bool) -> tuple[int, list[str]]:
    """Fetch one family; returns (fetched-count, failures)."""
    wanted = extract_urls(sources, pattern)
    if not wanted:
        return 0, [f"{kind}: no icon URLs found in sources"]

    dest.mkdir(parents=True, exist_ok=True)
    manifest_path = dest / "manifest.json"
    manifest: dict[str, dict] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    todo = {n: u for n, u in wanted.items() if refresh or n not in manifest or not (dest / n).exists()}
    skipped = len(wanted) - len(todo)
    print(f"[icons] {kind}: {len(wanted)} distinct referenced, fetching {len(todo)}, {skipped} already present")

    failures: list[str] = []
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, url): (name, url) for name, url in todo.items()}
        for future in concurrent.futures.as_completed(futures):
            name, url = futures[future]
            try:
                body = future.result()
            except Exception as exc:  # noqa: BLE001 - report every failure, keep fetching
                failures.append(f"{name}: {exc}")
                continue
            (dest / name).write_bytes(body)
            manifest[name] = {
                "source": url,
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
            }
    elapsed = time.perf_counter() - started

    if todo and len(failures) < len(todo):
        # Record every success (even a partial run) so a re-run retries only
        # what actually failed.
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    total = sum(entry["bytes"] for entry in manifest.values())
    print(f"[icons] {kind}: {len(manifest)} on disk, {total} bytes total, {elapsed:.1f}s this run")
    return len(todo) - len(failures), failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, action="append", default=[], help="raw catalog JSON to scan (default: the two data/raw files)")
    parser.add_argument("--refresh", action="store_true", help="re-download even if the file exists")
    args = parser.parse_args()
    sources = args.source or DEFAULT_SOURCES
    missing = [str(s) for s in sources if not s.exists()]
    if missing:
        print(f"[icons] source not found: {missing}", file=sys.stderr)
        print("[icons] the icons ship pre-fetched in frontend/public/icons/; "
              "run this against collector data files to refresh them.", file=sys.stderr)
        return 2

    all_failures: list[str] = []
    for kind, pattern, dest in KINDS:
        _, failures = fetch_family(kind, pattern, dest, sources, args.refresh)
        all_failures.extend(failures)

    if all_failures:
        for line in sorted(all_failures):
            print(f"[icons] FAILED {line}", file=sys.stderr)
        print(f"[icons] {len(all_failures)} download(s) failed; manifest not updated", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
