> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Stage 1: Data Ingestion & Crawling (`crawler/`)

This package is responsible for fetching live catalog products, formulation ingredient lists, safety indicators, and user reviews from Skintellect (and future multi-category cosmetic sources).

## Components

| Script | Purpose |
| :--- | :--- |
| `crawler.py` (in `skintellect-collector`) | Full multi-category scraper with Cloudflare bypass headers, Hotwire Turbo stream decoding, and concurrent worker pools. |
| `queue_manager.py` (in `skintellect-collector`) | Prioritized SQLite queue background worker for resilient, throttled catalog ingestion without triggering rate limits. |

## Quick Execution
```bash
# Crawl specific categories
python -m skintellect crawl --categories "sunscreens,serums" --pages 2 --workers 2

# Run resilient queue background ingestion
python -m crawler.queue_manager
```
