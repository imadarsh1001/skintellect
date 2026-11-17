# API (FastAPI Routers & Application Assembly)

## Overview
FastAPI application assembly and typed HTTP routers. `app.py` builds the app (lifespan startup, CORS, static mounts, HTML workspaces), `catalog.py` exposes product/ingredient/persona/taxonomy endpoints, `research.py` exposes the evidence-research and copilot endpoints, and `formulation.py` exposes the dupes endpoint. Routers delegate all logic to `catalog`, `research`, `agents`, and `formulation` packages.

## Interface
- `[app.py:app]` - FastAPI instance (title `APP_NAME + " API"`, version `APP_VERSION` from `skintellect.config`); lifespan runs `[app.py:lifespan]`: `migrate` + `[research.jobs:recover_interrupted]` + `[research.references:ingest_references]`.
- `[app.py:health_check]` - `GET /health`. `[app.py:serve_spa]` - catch-all `GET /{spa_path:path}` serves `frontend/dist/index.html` with `Cache-Control: no-cache` (it must never be served stale — hashed `/assets` are immutable) for every non-API path; unknown paths are the client router's job (its catch-all redirects to `/`). The route guards `api`/`api/...` paths to keep their JSON 404, and is registered after the API routers and `/health` so those match first (`/docs` too). Without a build it returns 503.
- `[catalog.py:router]` - `GET /api/products`, `GET /api/products/{product_id}`, `GET /api/products/{product_id}/image` (image proxy: SSRF host allowlist, disk cache), `GET /api/domains`, `GET /api/sources`, `GET /api/ingredients`, `GET /api/ingredients/meta/functions`, `GET /api/ingredients/{ingredient_id}`, `GET/POST /api/personas`, `GET /api/personas/{persona_id}`, `GET /api/stats`.
- `[research.py:router]` (prefix `/api`) - `GET /api/research/demo`, `GET /api/research/references`, `GET /api/products/{id}/connections`, `GET /api/research/progress`, `POST /api/research/jobs` (SSE stream), `POST /api/research/jobs/{job_id}/cancel`, `GET /api/research/status`, `POST /api/research/reviews/prepare`, `GET /api/quality`, `POST /api/search/interpret`, `POST /api/search`, `GET /api/products/{id}/review-insights`, `POST /api/alternatives`, `GET /api/evidence/{evidence_id}`, `GET /api/research/retrieve`, `POST /api/assistant/query`, `POST /api/research/copilot`, `POST /api/research/copilot/stream` (SSE), `POST /api/research/copilot/plan`, `GET/POST/DELETE /api/research/copilot/sessions[/...]`.
- `[formulation.py:find_dupes]` - `GET /api/dupes/{product_id}`.
- `[research.py:AssistantRequest]`, `[research.py:CopilotRequest]`, `[research.py:ScopedSearchRequest]`, `[research.py:PreparationRequest]` - request models (StrictModel or explicit bounds).

## Invariants
- Routers are thin: every endpoint delegates to catalog/research/agents functions and maps errors to HTTP codes; `[research.py:start_preparation]` maps `GeminiUnavailable` to 503 and `ValueError('preparation_already_active')` to 409 (other ValueErrors to 422).
- `[research.py]` guards product-scoped endpoints: `POST /api/research/reviews/prepare` and `GET /api/products/{id}/review-insights` return 404 unless `[evidence.py:evidence]` resolves `product:<id>`.
- `[catalog.py:list_sources]` always annotates registry entries with `status: "configured_registry", verified: False` - configured sources are never presented as verified evidence.
- `[catalog.py:create_persona]` maps `RuntimeError` from persona persistence to HTTP 500 without leaking the exception chain (`from None`).
- `[research.py:copilot_stream]` emits `text/event-stream` with `data: <json>` frames and a terminal `data: [DONE]` frame, with `Cache-Control: no-cache` / `X-Accel-Buffering: no` headers.
- `[research.py:start_preparation]` runs the job inline over SSE (`jobs.stream_job` worker thread) instead of detached `BackgroundTasks`: events `queued`/`started`/`progress`/`keepalive`/`done` as `data: <json>` frames, headers `Cache-Control: no-cache, no-transform` / `Connection: keep-alive` / `X-Accel-Buffering: no`; it clamps `max_seconds` to `[research/jobs.py:MAX_STREAM_SECONDS]` (240, a 60 s buffer under Vercel's 300 s function kill) and calls `jobs.release_stale_jobs` first to reap rows orphaned by a serverless timeout (stuck `running` for >305 s).
- CORS is restricted to `http://127.0.0.1:8000` and `http://localhost:8000` (`[app.py]` middleware configuration).
- Known drift (code-grounded): `[research/labels.py:read_label]` remains unwired — no route registers `/api/research/label` and the legacy label-tab caller was retired with the template UI (`893a020`); the handler is exercised only by `tests/test_release.py`. The routine-analyzer, formula-lab and agents-board callers (`app.js`/`api.js`/`study.js`) were retired with the template UI, so no frontend caller remains for those unregistered routes.

## Side Effects
- Startup (`[app.py:lifespan]`): schema migration (`skintellect.database.migrate` — version fast-path skips remote replay), interruption recovery (`jobs.recover_interrupted` — blanket locally, stale-only (>305 s) remotely since instances share the database), and ingestion of `reference_sources.json` into `source_documents` (skipped when already ingested).
- Per-request: inline SSE execution of preparation jobs (`[research.py:start_preparation]` -> `jobs.stream_job`; the worker thread commits final state even if the client disconnects), Gemini provider calls and their `gemini_runs` telemetry via the research services, SSE streaming responses.
- Static mounts: `/assets` from `frontend/dist/assets` when that directory exists, served by `[app.py:CachedStaticFiles]` with `Cache-Control: public, max-age=31536000, immutable` (content-hashed filenames are safe to cache forever). The legacy `/static` mount from `config.STATIC_DIR` was removed with the template UI in `893a020`; the constant no longer exists.
- File reads: the built SPA entry from `frontend/dist/index.html` on every workspace route (no TEMPLATES_DIR anymore).

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
