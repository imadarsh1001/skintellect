# Evidence Search scale-up plan

**Status: planned, not started (2026-11-19).** Green-light by opening an openspec change from this document (trunk workflow: big changes get an openspec plan first).

## Why

Evidence Search (`/research`) is the product's differentiating surface — answers backed by verbatim, hash-verified review quotes with evidence IDs — but it currently searches only the **3-product prepared demo cohort** (the page's own hint says so; GLOSSARY defines the prepared study as "a demonstration, not representative market coverage"). The differentiator becomes real only when the preparation pipeline has processed a meaningful slice of the catalog.

## What already exists (no new infrastructure needed)

- Bounded, resumable preparation jobs (`research/jobs.py`: single-worker queue, SSE progress, cancel, stale-worker reaping, interrupted-startup recovery) with `max_calls`/`max_seconds` budgets.
- Strict request contracts (`research/models.py`, `extra='forbid'`), review-extraction validation (exact-span quotes), passage index with stale-vector rejection.
- Edge caching on read-only GETs; BYOK gateway path for provider calls.

## Scope options

| Option | Shape | Cost character |
| --- | --- | --- |
| **A. Expanded cohort (recommended first step)** | ~50–100 products prepared (reviews + embeddings) | Bounded spend; proves result quality with real breadth |
| B. Full corpus | all ~2,502 products | Serious spend before knowing quote quality at scale |

Cost drivers per product: Gemini review extraction (per review batch, through the CF gateway BYOK) + passage embeddings + Turso writes. Turso row-read budget is 500M rows/month (see deploy memory for the metering history).

## Decision gates

1. Run Option A, measure **actual provider calls, wall-clock, and Turso writes per product** from the job snapshot.
2. Human-check quote quality/relevance on ~10 prepared products.
3. Only then decide the full-corpus go/no-go.

## Related deferred work (do not fold in)

- **F6 per-claim inline citations** — backend-blocked (`SourcesList` is the extension point when the backend emits per-claim evidence IDs); completes the citation UX independently of corpus size.
- Static catalog snapshot for cold starts — rejected until the row-read slope or real-user evidence demands it.
