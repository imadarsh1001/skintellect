# Formulation (Formula Lab & Scoring Engine)

## Overview
Pure computation layer for formulation analysis: classifies ingredients into rule-based groups (brighteners, barrier hydrators, smoothers, irritants, fungal-acne triggers, pore cloggers), computes the reverse-engineered Skintellect Match score and Darmeto clinical fit points, and assembles the Formula Lab response (per-ingredient badges, skin-type compatibility matrix, concern efficacies, mathematical audit trace). Deterministic and offline; no network access.

## Interface
- `[ingredient_facts.py:classify_ingredients]` - core classifier; profiles `formula`, `catalog`, `recommendation`; returns `IngredientFacts(groups, provided_flags)`; raises `ValueError('unknown_ingredient_profile')` otherwise.
- `[ingredient_facts.py:normalize]` - NFKC/casefold normalization with `[ingredient_facts.py:ALIASES]` (aqua->water, fragrance/perfume->parfum, glycerine->glycerin); `[ingredient_facts.py:names_from_formula]`.
- `[ingredient_facts.py]` rule tables: `FUNGAL_ACNE_TRIGGERS`, `BRIGHTENERS`, `BARRIER_HYDRATORS`, `SMOOTHERS_TEXTURE`, `IRRITANTS_ALLERGENS`, `KNOWN_PORE_CLOGGERS`.
- `[formulas.py:analyze_formula_full]` - Formula Lab master orchestrator; `[formulas.py:classify_single_ingredient]` - per-ingredient badge/safety classification; `[formulas.py:compute_skin_type_compatibilities]` (combination, oily, dry, sensitive, fungal_safe), `[formulas.py:compute_target_concern_efficacies]` (dark_spots, barrier, texture, redness), `[formulas.py:generate_mathematical_audit_log]`, `[formulas.py:_get_ingredients_db]` (stamp-cached ingredients table).
- `[scoring.py:parse_ingredients_input]` - accepts list, JSON string, or comma/newline separated text; `[scoring.py:predict_skintellect_match]` - 0-100 match with breakdown; `[scoring.py:calculate_darmeto_points]` - 0-130+ clinical fit points with tier labels; `[scoring.py:score_product_for_persona]` - record-flag-based persona scoring (returns `(match_score, darmeto, reasons)`); `[scoring.py:score_any_product]` - unified entry point; `[scoring.py:predict_skinsort_match]` - backward-compatibility alias of `predict_skintellect_match`.
- `[models.py]` - FastAPI request/response contracts: `RoutineAnalyzeRequest`, `RoutineAnalyzeResponse` (defaults `rule_version="foundation-1"`, `evidence_status="unverified_heuristic"`), `FormulaLabRequest`, `FormulaLabResponse` (defaults `score_kind="unvalidated_heuristic"`, `assessment_status="unverified_formula"`), `ParsedIngredientDetail`, `SkinTypeCompatibility`, `ConcernEfficacy`, `ConflictItem`, `SynergyItem`.

## Invariants
- All scores are unvalidated heuristics by contract: `[models.py:FormulaLabResponse]` and `[models.py:RoutineAnalyzeResponse]` ship `unverified`/`heuristic` status strings, and `[formulas.py:analyze_formula_full]` overwrites every compatibility status with `"Unverified heuristic"` and every concern mechanism with a "Product efficacy is unverified" prefix.
- `[scoring.py:predict_skintellect_match]` fungal cliff: when fungal triggers exist and avoidance is requested, the score is capped via `max(34, 100 - penalty)` (penalty `min(55 + 2*triggers, 66)`), early-returning before other checks; otherwise the final score is clamped to `[20, 100]`.
- `[scoring.py:score_product_for_persona]` hard-caps fungal-unsafe products at `(40, 44.0)` when the persona excludes fungal triggers.
- `[scoring.py:calculate_darmeto_points]` bonuses are capped (`min(3*count, 9)` brighteners, `min(2*count, 8)` barrier, `min(2*count, 6)` smoothers, +4/+3/+2 safety flags, +3 for rating >= 4.0) and deductions are `4*cloggers` / `6*irritants`; tier boundaries are 120 / 105 / 90 points.
- `[ingredient_facts.py:classify_ingredients]` profile `recommendation` intentionally preserves legacy behavior: the `\bglycerin\b` hydrator pattern is removed, the `colloidal` misspelling (`collodial`) is preserved in smoother patterns, `\bgalactomyces\b` is added, and `pore_cloggers` is empty (flag data and comedogenic >= 3 substitute).
- `[formulas.py:classify_single_ingredient]` matches the database by exact lowercase name or normalized alias only (`ingredient_facts.normalize`), never by substring.
- `[formulas.py:_get_ingredients_db]` invalidates its module-global cache whenever `get_catalog().stamp` changes; a failed DB load yields an empty dict plus a printed warning, not an exception.

## Side Effects
- SQLite reads only (no writes): `ingredients` table cached in module globals via `[formulas.py:_get_ingredients_db]`; persona lookup through `skintellect.catalog.personas.get_all_personas` (`[formulas.py:analyze_formula_full]`).
- Import-time stdout reconfiguration to UTF-8 on Windows (`[scoring.py]` module header, `sys.stdout.reconfigure`).
- `[scoring.py]` `__main__` block prints a sample formulation evaluation demo; `[formulas.py]` prints nothing on import.
- No network calls and no file I/O in this package.

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
- Offline scoring can be exercised manually via `python -m skintellect score --ingredients "..."` (CLI owned by `skintellect.cli`).
