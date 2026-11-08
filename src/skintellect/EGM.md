# Skintellect (Application Package)

## Overview
The `skintellect` application package: configuration and environment loading (`config.py`), the SQLite foundation (`database.py`), the Gemini-only model transport (`gemini.py`), the unified CLI (`cli.py` / `__main__.py`), plus eight child packages covering ingestion, catalog services, formulation scoring, pure domain core, evidence research, agents, the FastAPI surface, and web assets. Entry point contract: `python -m skintellect` (`__main__.py`) and console script `skintellect = "skintellect.cli:main"` (`pyproject.toml`).

## Interface
- Local modules:
  - `[config.py:DB_PATH]` - resolved catalog database path (env override `SKINTELLECT_DB_PATH`/`SKINSORT_DB_PATH`, else the first existing candidate such as `skintellect_moisturizers.db`); `[config.py:load_environment]` - allowlisted `.env` loader (`GEMINI_*`, `RESEARCH_*`, `SKINTELLECT_*`, `SKINSORT_*`, `GOOGLE_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `API_ENDPOINT`, `MODEL_ID`, `GENERATE_CONTENT_API`, `AGENT_LLM_MODE`) using `os.environ.setdefault` (never overrides existing env, never executes values); `[config.py:llm_enabled]` - `RESEARCH_LLM_ENABLED=1` and `AGENT_LLM_MODE != 'offline'`; `[config.py:set_embedding_model]`, `[config.py:set_absa_model]` - guarded `.env` writers; `[config.py:resolve_database_path]`, `[config.py:STATIC_DIR]`, `[config.py:TEMPLATES_DIR]`, `[config.py:EXPORTS_DIR]`, `[config.py:PROJECT_ROOT]`, `[config.py:BASE_DIR]` (string alias of `PROJECT_ROOT`); package constants `APP_NAME` / `APP_DESCRIPTION` (feed the FastAPI title in `api/app.py`) and `APP_VERSION = "3.0.0"`.
  - `[database.py:database]` - context manager committing/rolling back and always closing the Windows file handle; `[database.py:migrate]` - additive metadata tables (`record_quality`, `ingredient_aliases`, `source_documents`, `review_aspects`, `rule_registry`, `foundation_migrations`) and seed flagging; `[database.py:init_db]` - base schema (`products`, `ingredients`, `product_ingredients`, `reviews`); `[database.py:formula_hash]`; `[database.py:audit]` - reproducible data-quality counters incl. `verified_complete` and `stale_verifications`; `[database.py:run_migrations]`; `[database.py:export_json]`, `[database.py:export_reviews_json]`; `[database.py:main]` - CLI `python -m skintellect.database {audit|schema|metadata}`.
  - `[gemini.py:GeminiClient]` - developer/Vertex transport (`structured`, `embed`, `status`, `endpoint`, `available`); `[gemini.py:run_budget]` - context-scoped call/time budget; `[gemini.py:ensure_tables]` - `gemini_cache`, `gemini_runs`, `research_vectors`, `embedding_query_cache`; `[gemini.py:GeminiUnavailable]` - redacted error codes; `[gemini.py:vertex_schema]`; `[gemini.py:API_ROOT]`.
  - `[cli.py:main]` - subcommands `stats`, `recommend`, `filter`, `report`, `export`, `score`, `clean`, `audit`, `web` (`cmd_stats`, `cmd_recommend`, `cmd_filter`, `cmd_report`, `cmd_export`, `cmd_score`, `cmd_clean`, `cmd_audit`, `cmd_web`); `[__main__.py]` - `python -m skintellect` -> `cli.main`.
- Child package contracts (all links verified to exist):
  - [agents](./agents/EGM.md) - LangGraph research workflow, intent routing, HITL clarification, copilot sessions.
  - [api](./api/EGM.md) - FastAPI app assembly and typed routers (catalog, research, dupes).
  - [catalog](./catalog/EGM.md) - catalog store/cache, product and ingredient services, personas, recommendations, taxonomy.
  - [core](./core/EGM.md) - pure domain entities and persona-match policies (no I/O).
  - [formulation](./formulation/EGM.md) - ingredient classification, match scoring, Darmeto points, Formula Lab analysis.
  - [ingestion](./ingestion/EGM.md) - catalog import/seed/clean/audit/verify CLI and PubChem enrichment.
  - [research](./research/EGM.md) - evidence-backed search, review ABSA (aspect-based sentiment analysis), hybrid retrieval, preparation jobs, references, labels.
  - [web](./web/EGM.md) - templates and static frontend assets boundary.

## Invariants
- Credentials only come from environment or allowlisted `.env` keys; `[config.py:load_environment]` never overrides pre-set environment variables and never accepts secrets as CLI arguments (also stated in `research/preparation.py` docstring).
- `[config.py:resolve_database_path]` fails with `FileNotFoundError` for an explicit override that does not name an existing file - SQLite never silently creates an empty catalog.
- `[gemini.py:GeminiClient]` validates every model name via `[gemini.py:safe_model]` (`[a-zA-Z0-9._-]{1,100}`), rejects non-default Vertex `API_ENDPOINT` values (`untrusted_api_endpoint`), enforces `argon_requires_global_location`, clamps timeout to <= 60s and attempts to <= 3, and raises only redacted `GeminiUnavailable` codes - provider bodies and credentials never reach callers or logs.
- `[gemini.py:run_budget]` is context-scoped (`ContextVar`); `[gemini.py:GeminiClient._request]` refuses calls once `max_calls` or the deadline is reached (`run_budget_exhausted`) and retries only HTTP 429/500/502/503/504 with capped exponential backoff.
- Generation is temperature-0 with JSON-schema-constrained output; responses failing the declared response model's `model_validate_json` raise `schema_validation_failed` and are retried/cached never; successful outputs are cached by sha256 of (backend, project, location, model, task, version, system, data, schema, image) in `gemini_cache` (`[gemini.py:GeminiClient.structured]`).
- `[database.py:migrate]` flags exactly the `[ingestion/maintenance.py:BENCHMARK_PRODUCTS]` IDs (200001-200010) as `is_seed=1`; `record_quality.formula_status` is CHECK-constrained to `missing`/`unverified`/`verified_complete`.
- Known CLI drift (code-grounded): `[cli.py:cmd_recommend]` calls `catalog/recommendations.py:get_recommendations` with keyword arguments it does not accept (`brand_country`, `min_match`, `limit`, `max_cloggers`, `require_fungal_safe`, `require_oil_free`, `require_fragrance_free`, `require_alcohol_free`), and `[cli.py:cmd_filter]` calls `catalog/recommendations.py:search_products` with (`brand_country`, `active_ingredient`, `max_cloggers`); invoking either subcommand raises `TypeError` until reconciled. `cmd_recommend` also prints `p['analysis']['soothers']` while the analysis groups are named `smoothers`.
- `[cli.py:cmd_web]` requires `uvicorn` and prints an install hint instead of raising when it is missing.

## Side Effects
- Import time: `[config.py]` adds `<PROJECT_ROOT>/.runtime` paths (optional dependency-fallback directory, see docs/DEVELOPMENT.md) to `sys.path` and runs `load_environment()`; `[database.py]` and `[gemini.py]` create/extend SQLite tables on first use (`migrate`, `init_db`, `ensure_tables`).
- SQLite writes: all foundation tables via `[database.py:migrate]`/`[database.py:init_db]`; Gemini telemetry rows in `gemini_runs` and response cache rows in `gemini_cache` (`[gemini.py:GeminiClient._record]`, `[gemini.py:GeminiClient.structured]`), embedding query cache in `embedding_query_cache` (`[gemini.py:GeminiClient.embed]`).
- Network: all Gemini REST/SDK traffic originates here (`generativelanguage.googleapis.com` or `aiplatform.googleapis.com`); children reach it only through `GeminiClient`.
- File writes: `data/exports/*.json` exports (`[database.py:export_json]`, `[database.py:export_reviews_json]`, `[cli.py:cmd_export]`), `.env` edits (`[config.py:set_embedding_model]`, `[config.py:set_absa_model]`), personas JSON (`[cli.py:cmd_report]` via `[catalog/personas.py:export_personas_json]`).
- Process: `[cli.py:cmd_web]` starts a uvicorn server bound to `--host`/`--port` (default `127.0.0.1:8000`); CLI commands reconfigure stdout to UTF-8 on Windows (`[cli.py]` header).
- `__init__.py` is a docstring-only namespace (`"""Skintellect application package."""`); it defines no export surface.

## Verification
- Python backend; no pytest configured. From the repository root run:

  ```
  python -m tests.smoke_api
  python -m tests.run_legacy_direct
  ```
- CLI smoke targets: `python -m skintellect stats`, `python -m skintellect score --ingredients "Water, Niacinamide, Glycerin"`; server target: `python -m skintellect web --port 8000`.
