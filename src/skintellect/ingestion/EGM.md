# Ingestion (Catalog Maintenance & External Enrichment)

## Overview
Offline ingestion and maintenance utilities that populate and curate the SQLite catalog. `maintenance.py` is the operator bridge between the private collector's exported catalog JSON and the public formulation database (seeding, importing, cleaning, auditing, human formula verification). `pubchem.py` enriches recorded ingredients with NCBI PubChem chemical-registry data.

## Interface
- `[maintenance.py:import_catalog_json]` - import/update products and formulations from an exported catalog JSON; returns a summary dict (`total_processed`, `inserted`, `updated`, `new_ingredients`, `linked_ingredients`).
- `[maintenance.py:seed_multidomain]` - idempotent upsert of the 10 multi-domain benchmark products defined in `[maintenance.py:BENCHMARK_PRODUCTS]` (IDs 200001-200010; domains hair, body, makeup).
- `[maintenance.py:clean_database]` - canonicalize categories, routine steps, and missing numeric fields.
- `[maintenance.py:run_audit]` - read-only audit report (categories, field completeness, duplicates, ingredient and review counts).
- `[maintenance.py:verify_formula]` - record a human completeness verification for a non-seed product.
- `[maintenance.py:_ensure_columns]` - additive `ALTER TABLE` guards for `products.domain/target_area` and `ingredients.domains_json/sources_json/target_areas_json`.
- `[maintenance.py:main]` - CLI: `python -m skintellect.ingestion.maintenance {audit|clean|seed|verify|import}`.
- `[pubchem.py:PubChemConnector]` - PubChem PUG REST client (`fetch_compound`); `[pubchem.py:PUBCHEM_API_BASE]`.
- `[pubchem.py:enrich_top_actives]` - enriches the most-used ingredients' `sources_json` with `"pubchem"`; `[pubchem.py:main]` - CLI: `python -m skintellect.ingestion.pubchem --limit N`.

## Invariants
- `[maintenance.py:import_catalog_json]` upserts by `id`, falling back to a `slug` match; product column updates use `COALESCE` so absent JSON fields never blank existing values.
- `[maintenance.py:import_catalog_json]` preserves an existing `verified_complete` formula status: the `record_quality` upsert's `ON CONFLICT ... DO UPDATE` carries `WHERE formula_status != 'verified_complete'`.
- `[maintenance.py:verify_formula]` refuses seed products and empty ingredient lists (raises `ValueError`), and stamps `record_quality.verified_hash` with `skintellect.database.formula_hash` plus `verified_at` / `verified_source`.
- `[maintenance.py:BENCHMARK_PRODUCTS]` IDs 200001-200010 are exactly the seed IDs that `skintellect.database.migrate` flags `is_seed=1`; seeded benchmark formulas are upserted (update-if-exists), never duplicated.
- `[maintenance.py:clean_database]` canonicalization is fixed-policy: NULL/empty categories become `Moisturizers`, `Face Cleansers` merge into `Cleansers`, `routine_step` is overwritten from a category map, and missing `match_score`/`rating`/`review_count` default to 45 / 0.0 / 0.
- `[pubchem.py:PubChemConnector.fetch_compound]` never raises on provider failure - any exception returns `None` (callers must treat `None` as "unmatched"); results are cached per-instance by lowercased name.
- `[pubchem.py:enrich_top_actives]` only appends `"pubchem"` to `sources_json` when a compound is actually resolved.

## Side Effects
- Network: HTTPS GET to `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/...` (`[pubchem.py:PubChemConnector.fetch_compound]`) with User-Agent `FormulationStudio-PubChemClient/2.0 (Academic/Bioinformatics)` and `time.sleep(0.3)` pacing per ingredient (`[pubchem.py:enrich_top_actives]`).
- SQLite writes: `products`, `ingredients`, `product_ingredients`, `record_quality` (`[maintenance.py:import_catalog_json]`, `[maintenance.py:seed_multidomain]`, `[maintenance.py:verify_formula]`); `ingredients.sources_json` (`[pubchem.py:enrich_top_actives]`); schema changes via `ALTER TABLE` (`[maintenance.py:seed_multidomain]`, `[maintenance.py:_ensure_columns]`) and `init_db`/`migrate` calls inside `[maintenance.py:import_catalog_json]` and `[maintenance.py:verify_formula]`.
- File reads: catalog JSON path (`[maintenance.py:import_catalog_json]`); `.env` is read indirectly through `skintellect.config.DB_PATH`, never accepted as a CLI argument.
- stdout progress prints in all maintenance commands (`[maintenance.py:seed_multidomain]`, `[maintenance.py:clean_database]`, `[maintenance.py:run_audit]`, `[pubchem.py:enrich_top_actives]`).

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
- Seeding is exercised indirectly by `skintellect.database.migrate` (which imports `BENCHMARK_PRODUCTS` from this package); do not run `clean`/`import` against a production catalog casually - both mutate data in place.
