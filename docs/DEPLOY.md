# Deploying Skintellect (Vercel + Turso)

The production target is **all-in on Vercel**: the FastAPI app runs as a single
Python serverless function (maxDuration 300 s), the SPA is the static build,
and the catalog lives in a remote **Turso** (libSQL) database. Local
development needs none of this — with no Turso env vars set, everything falls
back to the checked-out SQLite file, unchanged.

## Architecture

| Piece | Local development | Production (Vercel) |
|---|---|---|
| Database | `skintellect_moisturizers.db` (SQLite file) | Turso over HTTP (`TURSO_DATABASE_URL`) |
| Driver | stdlib `sqlite3` | `turso_serverless` (pure Python, DB-API) |
| Vector storage | `research_vectors.vector_json` (JSON text) | `research_vectors.vector` (`F16_BLOB(768)`) |
| Vector ranking | in-Python dot product | server-side `vector_distance_cos` |
| Research jobs | `POST /api/research/jobs` → SSE stream (same both ways) | SSE stream, `max_seconds` clamped to 240 s |
| Image proxy cache | `data/cache/product-images` | `/tmp/skintellect/cache/product-images` (read-only FS fallback) |
| `.env` write-back (model settings) | writes `.env` | silent no-op (read-only FS) |

Connection selection lives in `skintellect.database.connect()`: when
`TURSO_DATABASE_URL` is set every catalog handle goes to Turso, else to the
local file. Offline tooling (`skintellect.cli`, `ingestion/*`, JSON exports)
always uses the local SQLite file.

## One-time setup

### 1. Create the Turso database

```bash
# Install the Turso CLI (https://docs.turso.tech/cli/introduction), then:
turso auth login
turso db create skintellect
turso db show skintellect --url          # → TURSO_DATABASE_URL
turso db tokens create skintellect       # → TURSO_AUTH_TOKEN
```

### 2. Migrate the catalog data

```bash
set TURSO_DATABASE_URL=libsql://skintellect-<org>.turso.io
set TURSO_AUTH_TOKEN=<token>
python scripts/migrate_to_turso.py
```

The script is idempotent (`INSERT OR REPLACE` on the same primary keys) —
re-run it any time the local catalog changes and to refresh embeddings.
It verifies row counts per table at the end and exits non-zero on drift.

### 3. Import the repo on Vercel

1. Push the branch to `main` (GitHub: `imadarsh1001/skintellect`).
2. At [vercel.com/new](https://vercel.com/new) import the repo; `vercel.json`
   supplies the build (`cd frontend && npm ci && npm run build`), the static
   output (`frontend/dist`), the function config (`api/index.py`,
   maxDuration 300), and the rewrites (`/health` and `/api/*` → the function,
   everything else → the SPA).
3. Set the environment variables in **Project → Settings → Environment
   Variables**:

   | Variable | Required | Notes |
   |---|---|---|
   | `TURSO_DATABASE_URL` | yes | `libsql://…` |
   | `TURSO_AUTH_TOKEN` | yes | least-privilege token for the db |
   | `GEMINI_API_KEY` | for LLM features | copilot/assistant/research degrade to heuristics without it (HTTP 503 on those endpoints) |
   | `CF_ACCOUNT_ID`, `CF_GATEWAY_ID`, `CF_AIG_TOKEN` | for LLM features | routes every Gemini request through the Cloudflare AI Gateway (`{account}/{gateway}/google-ai-studio`); see the shared `GATEWAY_RUNBOOK.md` |
   | `CF_GATEWAY_BYOK` | no | `1` only when the provider key is stored inside Cloudflare — the app then sends no provider credential |
   | `GEMINI_BACKEND` | no | `developer` is the serverless-friendly default (API-key auth); Vertex needs ambient ADC credentials that `/var/task` lacks |
   | `GEMINI_MODEL` | no | defaults `gemini-flash-latest` (Vertex argon requires `MODEL_ID`/`API_ENDPOINT` and global location) |
   | `GEMINI_EMBEDDING_DIMENSIONS` | no | defaults 768 — must match the migrated vectors |

4. Deploy. Smoke checks: `/health` returns JSON, `/explore` deep-link renders
   the catalog, `/progress` streams a job, `/copilot` streams a reply.

## Operational notes

- **Cold starts** skip migrations (`migrate()` checks
  `foundation_migrations` version 1) and reference re-ingestion (row-count
  check) — no remote DDL/DML replay per request.
- **Stale job rows**: a Vercel timeout or client disconnect can leave a job
  stuck in `running`; `POST /api/research/jobs` reaps jobs older than 305 s
  (`release_stale_jobs`) before queueing. SSE streams carry
  `Cache-Control: no-cache, no-transform` and `X-Accel-Buffering: no`.
- **The 240 s clamp** (`skintellect.research.jobs.MAX_STREAM_SECONDS`) keeps a
  60 s buffer under the 300 s function ceiling for final state commits and the
  terminal SSE event. The local file backend is subject to the same clamp.
- **Display cache**: `Catalog.stamp` treats remote data as static within a
  process lifetime (products/reviews change only via offline pipelines);
  serverless instances cache per instance.
- **CORS** is unchanged (same-origin: the function serves the SPA's `/api/*`
  via rewrites), and `data/raw` pipeline inputs are never needed at runtime.
