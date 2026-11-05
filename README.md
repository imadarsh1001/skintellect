# Skintellect

**Formulation Studio** is a local cosmetic-product research app built with Python,
FastAPI, SQLite and a buildless Vue interface. It combines catalog search,
ingredient constraints, review excerpts and explainable ingredient alternatives.
It is a research prototype; its scores and ingredient flags are unvalidated heuristics.

## Start the app

On this workstation, run:

```powershell
.\run-research.cmd
```

The launcher starts the full app, including the catalog and formulation tools.
Open [the prepared study](http://127.0.0.1:8000/study) for the focused demonstration.
Use one server worker for preparation jobs.

For a new checkout with Python 3.12 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m skintellect web
```

On macOS/Linux, activate with `source .venv/bin/activate`. Supply an existing
catalog through `SKINTELLECT_DB_PATH`; the database is not included in the package.
For new local provider configuration, copy `.env.example` to `.env` and fill in
its settings. Preserve an existing `.env`. See [setup and configuration](docs/DEVELOPMENT.md).

| Page | Purpose |
| --- | --- |
| `/study` | Prepared three-product demonstration |
| `/research` | Ingredient-constrained questions and attributed evidence |
| `/progress` | Coverage, preparation jobs, cancellation and resume |
| `/` | Catalog, ingredients, personas, Formula Lab, routines and experimental agents |
| `/docs` | Interactive HTTP endpoint documentation |

## Implemented features

- Catalog and ingredient search, custom personas, and explainable formula scores.
- Required/excluded ingredient checks with explicit pass, fail and unknown results.
- Rule-based and optional Gemini review extraction with exact supporting text spans.
- Lexical and embedding retrieval, ingredient-overlap alternatives, and bounded research workflows.
- Resumable review/index preparation with budgets, usage history and recovery.
- Ingredient connections, attributed reference notes, read-only local MCP tools,
  and experimental ingredient-label image transcription.

`run-mcp.cmd` starts the independent MCP adapter; it does not start the web server.
Optional provider operations require configuration and can incur provider charges.
The deterministic parser and rule-based extraction are available without model calls.

## Coverage and limits

The supplied local snapshot contains **2,502 products**, **1,507 ingredients**,
**12,216 product-ingredient links**, and **4,062 reviews**. Only **576 products**
have recorded ingredient lists; **none** are human-verified complete formulas.
Hair, body and makeup contain 10 demonstration products combined. Seeds are excluded
from default search and recommendations; the catalog endpoint can display them
explicitly with `include_seeds=true`.

Model preparation covers a small sample, not the full catalog. The prepared
study demonstrates three products, 28 reviews and 31 indexed passages. Saved
validation and preparation counts are snapshots; check `/progress` for coverage.

Missing information does not prove ingredient absence. Ingredient overlap does
not prove equal concentrations or performance. Review anecdotes and configured
source names do not establish clinical validation or retrieved scientific evidence.
The app is intended for local single-user operation; public hosting is unfinished.

## Project map

| Location | Contents |
| --- | --- |
| [src/skintellect/](src/skintellect/) | Runtime modules and packaged web assets |
| [tests/](tests/) | Regressions, synthetic fixtures and integration smoke checks |
| [scripts/](scripts/README.md) | Checks, workspace audit and evaluation commands |
| [experiments/](experiments/README.md) | Advanced-study plans: LangGraph board, label transcription, Ingredient CSI and Formula Lab |
| [docs/](docs/README.md) | Current guides and clearly separated historical notes |
| [data/](data/README.md) | Raw snapshots and generated data exports |
| [reports/](reports/README.md) | Saved evaluations, validation and report exports |
| [backups/](backups/README.md) | Local restore points; not an application dependency |

The live database remains `skintellect_moisturizers.db` at the checkout root.
The workstation launchers currently use `.venv` for Python and `.runtime` for
fallback dependencies. Neither folder is application source.

## Verification

```powershell
python scripts/check.py
python -m scripts.check_query_parser
python -m scripts.audit_workspace
```

The main checks use disposable synthetic data and disable real provider calls.
The workspace audit checks source imports, page assets, links and read-only
SQLite integrity. Browser rendering and live-provider quality require separate checks.
See [development](docs/DEVELOPMENT.md), [module ownership](docs/SOURCE_LAYOUT.md)
and [saved validation reports](reports/README.md).
