# src (Source Root)

## Overview
Intermediate source root of the repository. It contains a single child package, `skintellect`, which holds the entire application (configuration, SQLite foundation, Gemini transport, CLI, FastAPI surface, catalog/research/formulation services, and agents; the retired web-template tree was removed in Stage 5). No direct source files live at this level.

## Subdirectories & Boundaries
- skintellect: [./skintellect/EGM.md](./skintellect/EGM.md) - the application package; its contract indexes the local modules (`config.py`, `database.py`, `gemini.py`, `cli.py`) and the seven child contracts (agents, api, catalog, core, formulation, ingestion, research; the legacy `web` template tree was retired in Stage 5 — the UI is the frontend/ SPA).

## Invariants
- Packaging: `pyproject.toml` at the repository root sets `tool.setuptools.packages.find` with `where = ["src"]` and `include = ["skintellect*"]`, and maps the console script `skintellect = "skintellect.cli:main"`.
- Runtime layout constants resolve relative to this tree: `config.PACKAGE_ROOT = src/skintellect`, `PROJECT_ROOT =` the checkout containing `pyproject.toml` (or `SKINTELLECT_HOME`/`SKINSORT_HOME`). The retired `STATIC_DIR`/`TEMPLATES_DIR` constants are gone; the SPA lives in `frontend/`.

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
