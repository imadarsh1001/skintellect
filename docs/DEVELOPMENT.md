# Development and maintenance

Skintellect uses a `src/skintellect/` Python package, FastAPI, SQLite,
and a buildless Vue interface. See [source ownership](SOURCE_LAYOUT.md).

## Setup

Use Python 3.12 or newer. We recommend using **[uv](https://github.com/astral-sh/uv)** for fast, deterministic dependency management:

### Option A: Using `uv` (Recommended)

```powershell
# Create virtual environment and install dependencies
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"

# Configure environment
Copy-Item .env.example .env

# Start web interface
uv run skintellect web
```

### Option B: Using Standard Python `venv`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m skintellect web
```

Copy the environment example only for a new setup; preserve an existing `.env`.
Reinstall the editable package after migrating from the old root-level layout.
On macOS/Linux, activate with `source .venv/bin/activate`.

The Windows `run-research.cmd` launcher adds `src/` to
PYTHONPATH. The optional workstation `.runtime/` remains a dependency fallback.
Normal installations use a virtual environment and the editable install above.

The wheel includes templates, live JavaScript, CSS, Vue, and attributed reference
notes. It does not include a catalog, credentials, tests, or developer scripts.
Provide an existing database using `SKINTELLECT_DB_PATH`. `SKINTELLECT_HOME` optionally
selects the folder containing local configuration, exports and mutable data.
Without it, a source checkout uses its repository root; an installed wheel uses
the working directory. Static assets always resolve from the installed package.

## Commands

```powershell
python -m skintellect --help
python -m skintellect web
python -m uvicorn skintellect.api.app:app --host 127.0.0.1 --port 8000
python -m skintellect.research.preparation --help
python -m skintellect.research.study --help
python -m skintellect.ingestion.maintenance --help
python -m skintellect.ingestion.pubchem --help
```

The installed console command `skintellect` provides the master CLI entry point.
Legacy `skinsort*` commands, old `main.py`, `app.py`, `core.*`, `backend.*`, `crawler.*`,
`pipeline.*`, and root re-exports have been retired; update external callers.

Maintenance `audit`, `clean`, `seed` and `verify` are explicit subcommands.
Formula verification requires the product ID, `--source` and `--reviewer`.
Model upgrades preserve existing results and activate only validated coverage.


### Modern Frontend (Vite + Vue 3 SPA)

The repository includes a modern Vue 3 SPA under `frontend/` that compiles to `frontend/dist`:

```powershell
cd frontend
npm install
npm run build
cd ..
```

`api/app.py` serves `frontend/dist/index.html` as the default application when present, and falls back to the buildless templates under `web/templates/` if `frontend/dist` is not built.

## Package Management with `uv`

This repository uses PEP 621 metadata in `pyproject.toml` and is optimized for `uv`:

```powershell
# Add a new runtime dependency
uv add <package-name>

# Add a development / testing dependency
uv add --dev <package-name>

# Run verification suite in the managed environment
uv run python scripts/check.py

# Run Ruff code linter
uv run ruff check .

# Execute any skintellect CLI command directly
uv run skintellect stats
uv run skintellect recommend --category sunscreens --min-match 90
uv run skintellect score --ingredients "Water, Glycerin, Niacinamide, Ceramide NP"
```

## Checks

```powershell
python scripts/check.py
node tests/check_ui_semantics.js
python -m scripts.audit_workspace
python -m scripts.check_query_parser
```

The main checks run Ruff, create a disposable synthetic catalog, run regressions
and the agent smoke suite, then clean up that test catalog. They strip provider
settings and disable implicit `.env` loading. No live catalog or key is needed.
Asynchronous HTTP tests require local socket access in restricted environments.

The independent catalog HTTP smoke needs a running server and populated catalog:

```powershell
python -m tests.smoke_api
```

Use `python -m tests.run_legacy_direct` for the same catalog assertions without
HTTP transport. Run it against a disposable database copy when verifying a move.
`python -m tests.smoke_agents` runs board/CSI smoke checks alone.
The UI semantic checks do not establish browser rendering or interaction quality.

## Source rules

- HTTP modules validate inputs and translate errors; feature modules own behavior.
- Catalog loading and review parsing do not import the assistant workflow.
- Share scoring rules through `formulation/scoring.py`.
- Keep migrations and transaction handling in `database.py`; provider transport in
  `gemini.py`. Do not add generic repository, service or utility layers without need.
- Keep generated files in `reports/` or `data/exports/`, outside the package.
- Preserve the catalog and raw snapshots. Back up before changing stored data.
- Use explicit module imports; package `__init__.py` files do not re-export features.
- Keep the frontend buildless and retain validation, error handling and source attribution.

Preparation jobs run inside one API process. Use one worker. Authentication and
independent job infrastructure remain future work before public hosting.
GitHub Actions runs the same offline checks; hosted execution requires a push.

See [developer tools](../scripts/README.md) for evaluation effects and options,
and [maintenance](modules/data-maintenance.md) for stored-data commands.
