> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Preparation dashboard release (2.8.0)

Start `run-research.cmd` and open http://127.0.0.1:8000/progress. If a server was
already open before this update, stop that terminal with Ctrl+C and start it again.
The research page links to the dashboard. No credentials appear in the browser.

## Implemented

- Current-model review coverage checks input hashes and extraction versions. Empty
  text, per-product duplicates, and seeds are excluded from the eligible denominator.
- Current-model embedding coverage checks current source hashes and excludes stale
  or removed records. Counts differ from raw historical row counts by design.
- Review extraction and embedding jobs run outside the HTTP response, on the local
  server. Job state and completed batch counts are persisted in SQLite.
- One active preparation job is enforced by a database unique index. Jobs accept
  product scope, record limit, provider-attempt limit, and elapsed-time limit.
- Cancellation is cooperative between batches. A current request may finish. Budget
  exhaustion produces `paused`; provider failure produces `failed`; restarting the
  server marks unfinished jobs `interrupted`. Start another job to continue: the
  pipeline skips unchanged completed records. There is no automatic retry loop.
- Usage shows safe provider metadata and reported tokens, excluding cached replay
  tokens. It is not a monetary estimate; use Cloud billing for actual charges.
- Failures never expose exception bodies or keys. Original data tables are unchanged.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/research/progress` | Fresh coverage, jobs and safe usage metadata |
| POST | `/api/research/jobs` | Start `reviews` or `embed` preparation |
| POST | `/api/research/jobs/{id}/cancel` | Request cancellation |

Example job body:

```json
{"kind":"embed","limit":20,"product_id":10256,"max_calls":8,"max_seconds":120}
```

Limits: records 1–5000; attempts 1–1000; seconds 10–3600. Defaults are 20 records,
8 provider attempts, 120 seconds. Limits include retries and do not guarantee the
selected records will finish. Saved work survives cancellation and budget exhaustion.

## Validation and operating limits

69 tests pass, including nine job lifecycle/coverage/API tests and the existing
research HTTP contract tests. Legacy direct API assertions, Python compilation and
JavaScript syntax checks also pass. Live server and provider checks are recorded in
`reports/history/progress_release_validation.json`.

Run one server process/worker on one local machine. This is a local research tool;
the job API is not authenticated for shared/public hosting. Do not expose this server
publicly without authentication and a dedicated queue worker. Closing the server stops
jobs. The five-second refresh is polling, not streaming. Tokens update when a batch
finishes; there is no speculative ETA.

The feature implementation is usable with partial preparation coverage. Full-catalog
processing still requires running additional bounded jobs. Scientific reference
ingestion, manually verified formulas and held-out human annotations are data/research
tasks; this release does not fabricate them. KG, MCP, OCR and preference learning remain
optional future experiments rather than completed features.

Before this change, source and a consistent database snapshot were saved under
`backups/before_progress_20261022T212556Z/`.
