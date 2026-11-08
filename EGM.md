# Skintellect Repository Blueprint

## System Overview

Explainable cosmetic formulation intelligence and product research platform (package `skintellect` v3.0.0). Architecture is a split frontend/backend over a single SQLite catalog:

- **Backend** — `src/skintellect`: FastAPI application ([api/app.py:app]) assembling typed routers over three service layers: `catalog` (read-side product/ingredient/persona services over SQLite), `research` (evidence-backed search, review ABSA, hybrid retrieval, preparation jobs), and `agents` (LangChain tools + LangGraph copilot workflow with deterministic fallback). Deterministic scoring lives in `formulation` (rule tables, Skintellect Match, Darmeto points); the pure domain layer is `core` (frozen dataclasses + persona-match policy, zero I/O). Offline catalog maintenance and PubChem enrichment live in `ingestion`.
- **LLM transport** — Gemini-only, funneled through [src/skintellect/gemini.py:GeminiClient] with schema-constrained temperature-0 generation, `run_budget` accounting, sha256-keyed response cache, and `GeminiUnavailable` failures; every other module consumes it indirectly.
- **Frontend** — two parallel UIs: (1) server-rendered HTML templates + plain-JS bundles in `src/skintellect/web/static/js` (text-only rendering contract), and (2) the Vue 3 + Vite + Tailwind SPA in `frontend` whose backend access funnels through `frontend/src/lib/api.ts` (SSE copilot streaming included).
- **Experiments** — `experiments`: opt-in study track (specialist board deliberation, ingredient CSI, label OCR, formula lab) that is LLM-optional, offline-capable (`AGENT_LLM_MODE=offline`), and read-only against the catalog.
- **Tooling** — `scripts`: developer gates and evaluation harnesses writing reports under `reports/`.

State ownership: the SQLite catalog (default `skintellect_moisturizers.db` via [src/skintellect/config.py:DB_PATH]) is the single source of truth; in-memory caches are stamp- or hash-invalidated against it. Human-maintained narrative docs live in [README.md](./README.md) and `docs/` — those READMEs are intentionally kept separate from these code-grounded `EGM.md` contracts.

## Subdirectories & System Boundaries

- [src](./src/EGM.md) - Source root holding the single `skintellect` application package (config, SQLite foundation, Gemini transport, CLI, and eight child packages).
- [frontend](./frontend/EGM.md) - Vue 3 + Vite + Tailwind SPA: build/tooling surface, `src/lib` API/SSE client, and feature/primitive component packages.
- [experiments](./experiments/EGM.md) - Opt-in advanced-study track: specialist board, ingredient CSI, label OCR, formula lab, plus CLI and offline smoke suite.
- [scripts](./scripts/EGM.md) - Developer checks and evaluation harnesses (offline gates, release evaluator, audit), excluded from the installed package.

Non-contract top-level directories (no source code; intentionally not documented with contracts): `docs/` (design/history documentation), `data/` (raw/exports data), `reports/` (generated evaluation and audit JSON), `tests/` (test-only suite + fixtures), `.github/` (CI workflow).

## Global Invariants

- **Unverified-heuristic labeling**: all heuristic scores are explicitly labeled — [src/skintellect/formulation/models.py] `score_kind='unvalidated_heuristic'` / `evidence_status='unverified_heuristic'`, and evaluation outputs keep non-accuracy framing (`evaluation_kind='automated_engineering_checks_not_human_validated_accuracy'`, `human_reviewed=False` per [scripts/evaluate_release.py:evaluate]). No code path may present heuristic output as verified safety.
- **Single Gemini transport with budgets**: all LLM traffic originates in [src/skintellect/gemini.py:GeminiClient] (temperature-0, JSON-schema-constrained, `run_budget(max_calls, max_seconds)` enforced, retries only on 429/5xx, failures raise [src/skintellect/gemini.py:GeminiUnavailable] with redacted codes); per-feature budgets cap research (6 calls/120 s) and label OCR (2 calls/90 s).
- **One SQLite catalog, stamp-invalidated caches**: caches in `catalog/store.py`, `formulation/formulas.py:_get_ingredients_db`, and `research/passage_index.py` are invalidated by catalog stamp or payload hash; a record is `complete` only with non-empty formula + `verified_complete` + matching `formula_hash` + `verified_source/verified_at` ([catalog/store.py:Catalog._normalize]).
- **Seed isolation**: `is_seed=1` products are exactly benchmark IDs 200001–200010 ([database.py:migrate], [ingestion/maintenance.py:BENCHMARK_PRODUCTS]); normal catalog and search queries exclude seeds unless explicitly included.
- **Origin contract for both frontends**: `frontend/src/lib/api.ts` uses `BASE_URL=''` (same-origin) with the Vite dev proxy `/api → http://127.0.0.1:8000` ([frontend/vite.config.ts]); FastAPI CORS is limited to `127.0.0.1:8000`/`localhost:8000`; production requires a reverse proxy. The legacy static JS calls same-origin `/api/*` only.
- **Known boundary drift (documented 404s)**: legacy `web/static/js/app.js`/`api.js` (`/api/routine/analyze`, `/api/formula-lab/analyze`, `/api/agents/*`) and `study.js` (`/research/label`) target routes not registered in [src/skintellect/api/app.py]; [experiments/label_ocr/labels.py:read_label] exists unwired. Also `docs/DEVELOPMENT.md` references `python -m tests.smoke_agents`, but the module lives at `experiments/smoke_agents.py`.
- **SQLite integer booleans**: safety flags (`fungal_acne_safe`, `fragrance_free`, `alcohol_free`, `oil_free`, …) are stored/compared as integers 1/0 across backend and frontend ([catalog] queries, `frontend/src/components/explore` comparisons).
- **Frontend rendering trust boundaries differ by UI**: legacy static JS renders text-only via `textContent` with `safeLink` http/https-only; the Vue SPA renders backend markdown via `v-html` without sanitization ([frontend/src/components/research/ResearchCopilot.vue]) — backend content is trusted there.
- **Experiments stay read-only**: `experiments/*` never writes to the catalog database; smoke checks force `AGENT_LLM_MODE=offline` for determinism.
- **Human docs vs contracts**: existing `README.md` files (root and per-directory) are human-curated and intentionally not modified by EGM bootstrapping; `EGM.md` files are the code-grounded contracts.

## Global Side Effects

- **SQLite writes** (single catalog DB): foundation tables ([database.py:migrate]), `personas` ([catalog/personas.py:save_persona]), `review_aspects` ([research/review_store.py]), `research_vectors` ([research/passage_index.py]), `preparation_jobs` ([research/jobs.py]), `source_documents` ([research/references.py]), `gemini_runs`/`gemini_cache` telemetry ([gemini.py:ensure_tables]), `copilot_sessions`/`copilot_messages` ([agents/copilot.py]).
- **Network**: Gemini REST/SDK endpoints (generativelanguage/aiplatform) via [gemini.py:GeminiClient]; PubChem PUG REST (paced GETs) via [ingestion/pubchem.py:PubChemConnector]. No other outbound providers.
- **File writes**: `data/exports/*.json` (catalog/review exports, persona JSON export); `reports/latest/*.json` and `reports/history/` (evaluations, audits); `.env` edits via [config.py:set_embedding_model|set_absa_model].
- **Processes/ports**: uvicorn on `127.0.0.1:8000` ([cli.py:cmd_web]); Vite dev server on port 5173 with `/api` proxy; background preparation-job worker thread with cooperative cancellation.

## System Verification

- Aggregate offline gate (ruff + bootstrap catalog + unittest + UI semantics): `python scripts/check.py`
- API smoke (from repo root): `python -m tests.smoke_api`; legacy-catalog assertions: `python -m tests.run_legacy_direct`
- Agent/experiment smoke (note: `experiments/`, not `tests/`): `python -m experiments.smoke_agents`
- Frontend type/build gate (from `frontend/`): `npm run build`
- UI semantics check: `node tests/check_ui_semantics.js`
- Workspace audit (writes `reports/latest/workspace-audit.json`): `python scripts/audit_workspace.py`
