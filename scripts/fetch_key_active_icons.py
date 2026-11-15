#!/usr/bin/env python
"""Fetch the catalog's key-active attribute icons locally.

The scraped catalog stores ``key_actives_json`` entries as
``{"name": ..., "note": ..., "icon": "https://assets.skinsort.com/...svg"}``.
The icon set is a bounded vocabulary (41 distinct SVGs, not one per
product). This script downloads all of them once into
``frontend/public/icons/key-actives/<name>.svg`` so the UI renders local
copies instead of hotlinking a third-party host, and writes
``manifest.json`` (name -> source URL + sha256) for provenance.

Note: the raw JSON also carries an ``"icon_url"`` key on ingredient
records (53 distinct safety-attribute icons: alcohol, fragrance,
paraben, ...). Nothing in the UI renders those yet; if an ingredient-
icon feature lands, extend the extraction below to that key.

Re-run any time the collector syncs new actives: existing files are kept
unless ``--refresh`` is passed, so each run only fetches the delta.

Usage:
    python scripts/fetch_key_active_icons.py [--source <json>] [--refresh]
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
DEFAULT_SOURCE = ROOT / "data" / "raw" / "skinsort_moisturizers.json"
DEST = ROOT / "frontend" / "public" / "icons" / "key-actives"

# The key-active icon URLs appear under the "icon" key (plain JSON).
URL_RE = re.compile(r'"icon"\s*:\s*"(https://assets\.skinsort\.com[^"\\]+)"')
# .../icons/v2/<name>-<hash>.svg -> <name>.svg
HASH_SUFFIX_RE = re.compile(r"-[0-9a-f]{8,}\.svg$")


def local_name(url: str) -> str:
    """assets/.../jaha-40dd995b.svg -> jaha.svg"""
    base = url.rsplit("/", 1)[-1]
    return HASH_SUFFIX_RE.sub(".svg", base)


def extract_urls(source: Path) -> dict[str, str]:
    """name -> source URL for every key-active icon in the raw file."""
    text = source.read_text(encoding="utf-8")
    urls: dict[str, str] = {}
    for match in URL_RE.finditer(text):
        urls.setdefault(local_name(match.group(1)), match.group(1))
    return urls


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "skintellect-icon-fetch/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    if b"<svg" not in body[:400]:
        raise ValueError(f"not an SVG: {url} starts with {body[:60]!r}")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="raw catalog JSON to scan")
    parser.add_argument("--refresh", action="store_true", help="re-download even if the file exists")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"[icons] source not found: {args.source}", file=sys.stderr)
        print("[icons] the icons ship pre-fetched in frontend/public/icons/key-actives/; "
              "run this against a collector data file to refresh them.", file=sys.stderr)
        return 2

    wanted = extract_urls(args.source)
    if not wanted:
        print("[icons] no icon URLs found in source", file=sys.stderr)
        return 2
    print(f"[icons] {len(wanted)} distinct icons referenced by the catalog")

    DEST.mkdir(parents=True, exist_ok=True)
    manifest_path = DEST / "manifest.json"
    manifest: dict[str, dict] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    todo = {n: u for n, u in wanted.items() if args.refresh or n not in manifest or not (DEST / n).exists()}
    skipped = len(wanted) - len(todo)
    print(f"[icons] fetching {len(todo)}, {skipped} already present")

    started = time.perf_counter()
    failures: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, url): (name, url) for name, url in todo.items()}
        for future in concurrent.futures.as_completed(futures):
            name, url = futures[future]
            try:
                body = future.result()
            except Exception as exc:  # noqa: BLE001 - report every failure, keep fetching
                failures.append(f"{name}: {exc}")
                continue
            (DEST / name).write_bytes(body)
            manifest[name] = {
                "source": url,
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
            }
    elapsed = time.perf_counter() - started

    if failures:
        for line in sorted(failures):
            print(f"[icons] FAILED {line}", file=sys.stderr)
        print(f"[icons] {len(failures)} download(s) failed; manifest not updated", file=sys.stderr)
        return 1

    if todo:
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    total = sum(entry["bytes"] for entry in manifest.values())
    print(f"[icons] {len(manifest)} icons on disk, {total} bytes total, fetched in {elapsed:.1f}s")
    print(f"[icons] manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
