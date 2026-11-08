# API (FastAPI Routers & Application Assembly)

## Overview
FastAPI application assembly and typed HTTP routers. `app.py` builds the app (lifespan startup, CORS, static mounts, HTML workspaces), `catalog.py` exposes product/ingredient/persona/taxonomy endpoints, `research.py` exposes the evidence-research and copilot endpoints, and `formulation.py` exposes the dupes endpoint. Routers delegate all logic to `catalog`, `research`, `agents`, and `formulation` packages.

## Interface
- `[app.py:app]` - FastAPI instance (title `APP_NAME + " API"`, version `APP_VERSION` from `skintellect.config`); lifespan runs `[app.py:lifespan]`: `migrate` + `[research.jobs:recover_interrupted]` + `[research.references:ingest_references]`.
- `[app.py:health_check]` - `GET /health`; workspace pages `GET /progress`, `GET /study`, `GET /research`, `GET /compare`, `GET /graph`, `GET /` (serve `templates/index.html` or `frontend/dist/index.html` when present).
- `[catalog.py:router]` - `GET /api/products`, `GET /api/products/{product_id}`, `GET /api/domains`, `GET /api/sources`, `GET /api/ingredients`, `GET /api/ingredients/meta/functions`, `GET /api/ingredients/{ingredient_id}`, `GET/POST /api/personas`, `GET /api/personas/{persona_id}`, `GET /api/stats`.
- `[research.py:router]` (prefix `/api`) - `GET /api/research/demo`, `GET /api/research/references`, `GET /api/products/{id}/connections`, `GET /api/research/progress`, `POST /api/research/jobs` (202), `POST /api/research/jobs/{job_id}/cancel`, `GET /api/research/status`, `POST /api/research/reviews/prepare`, `GET /api/quality`, `POST /api/search/interpret`, `POST /api/search`, `GET /api/products/{id}/review-insights`, `POST /api/alternatives`, `GET /api/evidence/{evidence_id}`, `GET /api/research/retrieve`, `POST /api/assistant/query`, `POST /api/research/copilot`, `POST /api/research/copilot/stream` (SSE), `POST /api/research/copilot/plan`, `GET/POST/DELETE /api/research/copilot/sessions[/...]`.
- `[formulation.py:find_dupes]` - `GET /api/dupes/{product_id}`.
- `[research.py:AssistantRequest]`, `[research.py:CopilotRequest]`, `[research.py:ScopedSearchRequest]`, `[research.py:PreparationRequest]` - request models (StrictModel or explicit bounds).

## Invariants
- Routers are thin: every endpoint delegates to catalog/research/agents functions and maps errors to HTTP codes; `[research.py:start_preparation]` maps `GeminiUnavailable` to 503 and `ValueError('preparation_already_active')` to 409 (other ValueErrors to 422).
- `[research.py]` guards product-scoped endpoints: `POST /api/research/reviews/prepare` and `GET /api/products/{id}/review-insights` return 404 unless `[evidence.py:evidence]` resolves `product:<id>`.
- `[catalog.py:list_sources]` always annotates registry entries with `status: "configured_registry", verified: False` - configured sources are never presented as verified evidence.
- `[catalog.py:create_persona]` maps `RuntimeError` from persona persistence to HTTP 500 without leaking the exception chain (`from None`).
- `[research.py:copilot_stream]` emits `text/event-stream` with `data: <json>` frames and a terminal `data: [DONE]` frame, with `Cache-Control: no-cache` / `X-Accel-Buffering: no` headers.
- CORS is restricted to `http://127.0.0.1:8000` and `http://localhost:8000` (`[app.py]` middleware configuration).
- Known frontend/backend boundary gaps (documented, unresolved in code): `[app.js:API.analyzeRoutine]` posts to `/api/routine/analyze` and `[app.js:API.analyzeFormula]` to `/api/formula-lab/analyze`, and `[api.js:API.deliberateBoard]`/`[api.js:API.investigateCsi]` call `/api/agents/*`, but the routers included in `[app.py]` define none of those routes; `[study.js:label-form]` posts `/research/label` although no route is registered in `[research.py:router]` (the handler `research/labels.py:read_label` exists unwired). These requests 404 against the current app.

## Side Effects
- Startup (`[app.py:lifespan]`): schema migration (`skintellect.database.migrate`), interruption recovery marking queued/running jobs `interrupted`, and ingestion of `reference_sources.json` into `source_documents`.
- Per-request: background task execution of preparation jobs (`[research.py:start_preparation]` -> `jobs.execute`), Gemini provider calls and their `gemini_runs` telemetry via the research services, SSE streaming responses.
- Static mounts: `/static` from `config.STATIC_DIR`; `/assets` from `frontend/dist/assets` when that directory exists (`[app.py]`).
- File reads: workspace HTML templates from `TEMPLATES_DIR` (`[app.py:progress_workspace]`, `[app.py:research_workspace]`, `[app.py:serve_index]`).

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
