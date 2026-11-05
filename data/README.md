# Data Artifacts & Storage Contract

This directory documents the data contract and artifact schemas for the Skintellect Intelligence Engine.

## Architectural Boundary

To preserve a clean open-source separation between data collection and scientific intelligence:
- **Raw scraping dumps and crawlers** live exclusively in the private `skintellect-collector` repository.
- **The public repository** operates either against a local SQLite database (`skintellect_moisturizers.db`) or generates deterministic synthetic test fixtures on the fly via `tests/bootstrap_catalog.py`.

| Location | Role | Retention |
| --- | --- | --- |
| `skintellect_moisturizers.db` | Active local SQLite formulation database | Ignored by Git (local artifact) |
| `exports/` | Generated catalog, ingredient, review and persona JSON | Regeneratable output; ignored by Git |
| `src/skintellect/research/reference_sources.json` | Immutable attributed scientific literature references | Packaged in core Python distribution |

## Configuration Resolution

`skintellect.config` resolves the database path using the following precedence:
1. Environment variable `SKINTELLECT_DB_PATH` (or legacy `SKINSORT_DB_PATH`)
2. `skintellect_moisturizers.db` at project root
3. `data/skintellect_moisturizers.db` fallback

A missing explicit path fails rather than silently creating an empty uninitialized database.
Database binaries (`*.db`) and generated export caches are strictly excluded from version control.
