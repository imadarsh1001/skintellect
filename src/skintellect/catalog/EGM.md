# Catalog (Product, Ingredient, Persona & Recommendation Services)

## Overview
Read-side catalog services over the SQLite database: catalog resolution and display caching (`store.py`), paginated product queries with dynamic persona scoring (`products.py`), ingredient registry and dossiers (`ingredients.py`), persona persistence (`personas.py`), filter/recommendation SQL engine (`recommendations.py`), multi-domain taxonomy (`taxonomy.py`), and FastAPI schemas (`models.py`).

## Interface
- `[store.py:get_catalog]` - resolve the active `Catalog` (context-selected, explicit path, or `config.DB_PATH` default); `[store.py:catalog_scope]` - context-manager override; `[store.py:Catalog.records]` / `[store.py:Catalog.display_records]` - normalized records and enriched display cache; `[store.py:Catalog.stamp]` - DB + WAL mtime/size/header fingerprint; `[store.py:CATEGORIES]`, `[store.py:PRICE_RANGES]`.
- `[products.py:get_products]` - filter/sort/paginate with per-persona dynamic scoring; `[products.py:get_product_by_id]` - deep detail incl. dupes; `[products.py:get_catalog_stats]`; `[products.py:load_records]` - canonical record loader used across research modules.
- `[ingredients.py:get_ingredients]`, `[ingredients.py:get_ingredient_detail]`, `[ingredients.py:get_ingredient_functions]`, `[ingredients.py:_load_ingredients_cache]` - stamp-cached ingredient registry with badge/safety classification and product counts.
- `[personas.py:get_all_personas]`, `[personas.py:save_persona]`, `[personas.py:export_personas_json]`, `[personas.py:init_personas_db]`, `[personas.py:DEFAULT_PERSONAS]` (six personas; `uap` is default), `[personas.py:JSON_PATH]`.
- `[recommendations.py:get_recommendations]`, `[recommendations.py:search_products]`, `[recommendations.py:get_all_products_catalog]`, `[recommendations.py:resolve_routine_and_size]`, `[recommendations.py:analyze_product_ingredients]`.
- `[taxonomy.py:DOMAINS]` (skin, hair, body, makeup with target areas, categories, guardrails), `[taxonomy.py:SOURCES]` (skintellect, incidecoder, cosdna, cir, pubchem), `[taxonomy.py:get_all_domains]`, `[taxonomy.py:get_all_sources]`.
- `[models.py]` - pydantic schemas: `ProductSummary`, `ProductDetail`, `PaginatedProductsResponse`, `IngredientSummary`, `IngredientDetail`, `PaginatedIngredientsResponse`, `CatalogStats`, `PersonaModel`, `PersonaCreate`, `PersonaExclusions`, `IngredientFormulatingProduct`.

## Invariants
- `[store.py:Catalog._normalize]` computes `complete` only when the formula list is non-empty AND `record_quality.formula_status == 'verified_complete'` AND `verified_hash == formula_hash(formula)` AND `verified_source` and `verified_at` are present; otherwise the product stays `unverified`/`missing`.
- `[products.py:get_products]` excludes seed records unless `include_seeds=True`; unknown-score products are never silently treated as matching.
- `[products.py:get_product_by_id]` builds `persona_match` with `match_status` `contraindicated` / `unknown` / `match` and `is_match` requiring zero flags and score >= 60; `match_score < min_match` filters out records.
- `[products.py:get_catalog_stats]` returns the hardcoded constant `total_ingredients: 1490` (it does not count the `ingredients` table).
- `[ingredients.py:get_ingredients]` returns an empty list when `fungal_safe_only=True` - "absence of a heuristic trigger is not a verified safety assessment" (in-code comment).
- `[ingredients.py:get_ingredient_detail]` marks every entry of `source_profiles` as `verified: False, status: "configured_only"`; formulating products are limited to 24 non-seed records.
- `[personas.py:init_personas_db]` seeds `DEFAULT_PERSONAS` only when the `personas` table is empty; `[personas.py:save_persona]` assigns IDs `custom_<username>` with `is_default=0` and re-exports the JSON snapshot.
- `[recommendations.py:get_recommendations]` applies strict safety gates only when requested: `must_be_fragrance_free` rejects `fragrance_free == 0` and any irritant match; `max_pore_cloggers` (default 1) caps heuristic cloggers.
- `[recommendations.py:get_all_products_catalog]` computes similarity in Python (Jaccard percentage, threshold >= 15 when both formula sets have >= 3 names) and fabricates a pseudo-similarity band 70-95 for products with fewer than 3 recorded names.
- Cache lifetimes are per-catalog and validated by `[store.py:Catalog.stamp]`; stale caches cannot survive a DB file or WAL change.

## Side Effects
- SQLite reads: `products`, `record_quality`, `reviews` (`[store.py:Catalog._read]`); `ingredients`, `product_ingredients` (`[ingredients.py:_load_ingredients_cache]`, `[ingredients.py:get_ingredient_detail]`); direct `sqlite3.connect` queries in `[recommendations.py:get_recommendations]`, `[recommendations.py:search_products]`, `[recommendations.py:get_all_products_catalog]`.
- SQLite writes: `personas` table (`[personas.py:init_personas_db]`, `[personas.py:save_persona]`).
- File writes: `data/exports/skintellect_personas.json` (`[personas.py:export_personas_json]`).
- Module-global caches keyed by `[store.py:Catalog.stamp]`: `_INGREDIENTS_DB`-style caches in `[ingredients.py:_CACHE_STAMP]` and `[store.py:Catalog._display]`; in `recommendations.py` and `[store.py:get_catalog]` a process-wide default catalog.
- stdout: `[personas.py:export_personas_json]` and `__main__` block prints; UTF-8 stdout reconfigure at import in `[recommendations.py]`.
- No network calls in this package.

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
