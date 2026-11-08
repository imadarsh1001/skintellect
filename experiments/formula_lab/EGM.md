# Formula Lab

## Overview

Experimental standalone formula-analysis package (`experiments/formula_lab`). It
bundles the reverse-engineered scoring engine (`scoring.py` — Skintellect Match
0-100% and "Darmeto Points" dermatological fit score), the deep-analysis service
(`formulas.py` — per-ingredient classification, five skin-type compatibility
matrices, target-concern efficacy, and a mathematical audit trace), and the pydantic
request/response contracts shared by consumers (`models.py`). All outputs are
explicitly unvalidated heuristics computed offline from ingredient names.

## Interface

- `[scoring.py:parse_ingredients_input(raw_input)]` — normalizes a `list` (of strings
  or `{"name": ...}` dicts), a JSON-array string, or a comma/semicolon/newline
  separated string into a clean `List[str]`, stripping leading list numbering
  (`^\d+[\.\)]\s*`).
- `[scoring.py:analyze_ingredients(ing_names)]` — returns the
  `groups` dict of `src/skintellect/formulation/ingredient_facts.py:classify_ingredients`
  (keys include `brighteners`, `barrier`, `smoothers`, `irritants`, `cloggers`,
  `fungal_triggers`).
- `[scoring.py:predict_skintellect_match(ingredients, skin_type="combination", concerns=None, avoid_fungal_triggers=True, avoid_fragrance=True, avoid_alcohol=True)]` —
  returns `{"predicted_match_score", "status", "summary", "breakdown", "analysis"}`.
  Scoring: base 100; fungal triggers with `avoid_fungal_triggers=True` hard-cap the
  score into `[34, 45]` and return early; fragrance `-15`, drying alcohol `-10`,
  any pore cloggers `-5`, missing dark-spot brighteners `-4`, missing barrier lipids
  `-4`, salicylic acid/BHA with at most one barrier lipid `-6`; final clamp
  `max(20, min(100, score))`. Status thresholds: `>=95` "Excellent match",
  `>=85` "Great match", `>=75` "Good match", else "Fair match".
- `[scoring.py:calculate_darmeto_points(match_score, analysis, fungal_acne_safe=True, pore_clogger_free=True, oil_free=True, rating=None)]` —
  returns `{"darmeto_points", "tier", "baseline_match", "additions", "deductions"}`.
  Bonuses: brighteners `min(3*count, 9)`, barrier `min(2*count, 8)`, smoothers
  `min(2*count, 6)`, fungal-safe `+4`, clogger-free `+3`, oil-free `+2`,
  `rating >= 4.0` `+3`. Deductions: `4 * clogger_count`, `6 * irritant_count`.
  Final = `round(max(0, pts), 1)`; tiers: `>=120` Tier 1 Holy Grail, `>=105` Tier 2
  Highly Targeted Treatment, `>=90` Tier 3 Safe Everyday Base, else Tier 4
  Suboptimal / Potential Irritants.
- `[scoring.py:score_any_product(ingredients, skin_type="combination", rating=None)]` —
  unified entry point returning `{"skintellect_match", "darmeto_points",
  "actives_summary"}` (note the result key is `skintellect_match`).
- `[scoring.py:predict_skinsort_match]` — backward-compatibility alias of
  `predict_skintellect_match`.
- `[formulas.py:classify_single_ingredient(name)]` — classifies one ingredient against
  the cached catalog `ingredients` table and regex actives; matches the DB by exact
  lower-cased name or `normalize()` alias only, never by substring. A clogger is
  `is_pore_clogging` or `comedogenic >= 3` or a regex clogger hit; an irritant is
  `irritancy >= 2` or a regex irritant hit. Returns `{"name", "function",
  "comedogenic", "irritancy", "is_pore_clogging", "is_fungal_trigger",
  "fungal_trigger_note", "is_active", "category_badge", "safety_status", "benefits",
  "description"}`. Unresolved ingredients get `category_badge="Unresolved ingredient"`
  and `safety_status="unknown"`; resolved-but-unflagged ingredients get
  `safety_status="unflagged"`.
- `[formulas.py:compute_skin_type_compatibilities(analysis, ing_names, is_fungal_safe, is_fragrance_free, is_alcohol_free)]` —
  returns entries for `combination`, `oily`, `dry`, `sensitive`, `fungal_safe`, each
  `{"score", "status", "verdict", "reason"}`; score floors are 30, 25, 30, 20, and a
  hard 100/35 for `fungal_safe`, with a 100 ceiling on the others.
- `[formulas.py:compute_target_concern_efficacies(analysis)]` — returns
  `dark_spots`, `barrier`, `texture`, `redness` entries with
  `{"status", "score", "actives", "mechanism"}`.
- `[formulas.py:generate_mathematical_audit_log(persona, ing_names, analysis, match_score, match_status, match_breakdown, darmeto_res, is_fungal_safe, is_fragrance_free, is_alcohol_free)]` —
  returns a list of human-readable audit-trace strings (Phase 1 match score steps,
  Phase 2 Darmeto additions/deductions).
- `[formulas.py:analyze_formula_full(ingredients_text, persona_id="uap")]` — master
  orchestrator; resolves the persona via
  `src/skintellect/catalog/personas.py:get_all_personas` (falls back to the first
  persona) and returns the full analysis dict (`predicted_match_score`,
  `darmeto_points`, `tier`, `status`, `summary`, `audit_log`, group lists,
  `is_fungal_safe`-style flags, `total_ingredients`, `active_count`, `active_ratio`,
  `skin_compatibilities`, `concern_efficacies`, `ingredients_breakdown`,
  `persona_label`). It post-overrides every compatibility/concern entry's status and
  verdict/mechanism with unverified-heuristic wording.
- `[models.py]` pydantic contracts: `[models.py:RoutineAnalyzeRequest]`
  (`product_ids: List[int]`, `persona_id="uap"`), `[models.py:ConflictItem]`,
  `[models.py:SynergyItem]`, `[models.py:RoutineAnalyzeResponse]`
  (`rule_version="foundation-1"`, `evidence_status="unverified_heuristic"`,
  `products` typed as `src/skintellect/catalog/models.py:ProductSummary`),
  `[models.py:FormulaLabRequest]` (`ingredients_text`, `persona_id="uap"`),
  `[models.py:ParsedIngredientDetail]`, `[models.py:SkinTypeCompatibility]`,
  `[models.py:ConcernEfficacy]`, `[models.py:FormulaLabResponse]`
  (`score_kind="unvalidated_heuristic"`, `assessment_status="unverified_formula"`,
  default `limitations` list).

External dependencies (repository paths):
`src/skintellect/formulation/ingredient_facts.py` (`classify_ingredients`,
`normalize`), `src/skintellect/formulation/scoring.py` (re-exported here for
`experiments` consumers), `src/skintellect/catalog/store.py:get_catalog`,
`src/skintellect/database.py:database`, `src/skintellect/catalog/personas.py`,
`src/skintellect/catalog/models.py`.

## Invariants

- All scores are unverified heuristics and must stay labeled as such:
  `[models.py:FormulaLabResponse]` defaults `score_kind="unvalidated_heuristic"` and
  `assessment_status="unverified_formula"`; `[models.py:RoutineAnalyzeResponse]`
  defaults `rule_version="foundation-1"` and `evidence_status="unverified_heuristic"`;
  `[formulas.py:analyze_formula_full]` returns `tier="Heuristic score band"`,
  `status="unknown"`/`"heuristic_only"`, a summary stating the assessment is
  unvalidated, and an `audit_log` prefixed with "Legacy rule arithmetic follows;
  PASS means no rule match, not verified safety.".
- The boolean flags `is_fungal_safe`, `is_fragrance_free`, `is_alcohol_free`,
  `is_pore_clogger_free`, `is_oil_free` in `[formulas.py:analyze_formula_full]` are
  `False` when the property fails and `None` otherwise — never `True` — so absence of
  flags can never read as an affirmative safety claim.
- `[scoring.py:predict_skintellect_match]` early-returns on fungal triggers when
  `avoid_fungal_triggers=True`; the hard cliff result is capped to `[34, 45]` and no
  later rules are applied.
- `[formulas.py:classify_single_ingredient]` matches the DB by exact name or
  `normalize()` alias only; substring matches are explicitly avoided to prevent
  misidentification.
- `[formulas.py:_get_ingredients_db]` caches the `ingredients` table in module globals
  `_INGREDIENTS_DB`/`_INGREDIENTS_STAMP` keyed on
  `src/skintellect/catalog/store.py:get_catalog().stamp`; a changed stamp forces a
  reload, so catalog edits are reflected on the next analysis.
- `analyze_ingredients` is a thin delegate to
  `skintellect.formulation.ingredient_facts.classify_ingredients(...).groups`; the
  authoritative classification rules live there, not here.

## Side Effects

- Import-time stdout reconfiguration: `[scoring.py]` calls
  `sys.stdout.reconfigure(encoding="utf-8")` when the current encoding is not UTF-8
  (Windows console support); failures are swallowed.
- SQLite read: `[formulas.py:_get_ingredients_db]` opens a connection via
  `src/skintellect/database.py:database(get_catalog().path)` and runs a read-only
  `SELECT` over the `ingredients` table to build the cache; load failures print a
  warning to stdout and yield an empty cache.
- Module-global state: `_INGREDIENTS_DB` and `_INGREDIENTS_STAMP` persist across
  calls until the catalog stamp changes.
- stdout on direct execution: `[scoring.py:__main__]` prints a sample formulation
  evaluation banner when the module is run as a script.
- No network calls and no database writes; the package is fully offline.

## Verification

From the repository root:

```
python -m unittest experiments.test_experimental_features
```

`test_formula_lab_raw_text_analysis` exercises
`[formulas.py:analyze_formula_full]` (`AGENT_LLM_MODE=mock` is forced per-test; no key
or network needed). Repo-level smoke checks (`python -m experiments.smoke_agents`,
`python -m tests.smoke_api`) cover the agent/CSI tracks and the API surface. No pytest
is configured for this repository.
