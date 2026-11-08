# src (Source Root)

## Overview
Intermediate source root of the repository. It contains a single child package, `skintellect`, which holds the entire application (configuration, SQLite foundation, Gemini transport, CLI, FastAPI surface, catalog/research/formulation services, agents, and web assets). No direct source files live at this level.

## Subdirectories & Boundaries
- skintellect: [./skintellect/EGM.md](./skintellect/EGM.md) - the application package; its contract indexes the local modules (`config.py`, `database.py`, `gemini.py`, `cli.py`) and the eight child contracts (agents, api, catalog, core, formulation, ingestion, research, web).

## Invariants
- Packaging: `pyproject.toml` at the repository root sets `tool.setuptools.packages.find` with `where = ["src"]` and `include = ["skintellect*"]`, and maps the console script `skintellect = "skintellect.cli:main"`.
- Runtime layout constants resolve relative to this tree: `config.PACKAGE_ROOT = src/skintellect`, `STATIC_DIR = <package>/web/static`, `TEMPLATES_DIR = <package>/web/templates`, `PROJECT_ROOT =` the checkout containing `pyproject.toml` (or `SKINTELLECT_HOME`/`SKINSORT_HOME`).

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
