# Core (Pure Domain Entities & Policies)

## Overview
Framework-free domain layer: frozen/mutable dataclass entities for products, ingredients, personas, reviews, aspect observations, and scientific references, plus deterministic persona-matching policies. Explicitly zero framework or database dependencies (`entities.py` module docstring); models provide natural-language explanations while code enforces constraints (`policies.py` module docstring).

## Interface
- `__init__.py` defines the public export surface (`__all__`): entities `ProductEntity`, `IngredientEntity`, `SkinPersonaEntity`, `PersonaExclusionsEntity`, `ReviewEntity`, `AspectObservationEntity`, `ScientificReferenceEntity`; policies `PersonaMatchResult`, `evaluate_persona_match`, `normalize_ingredient_name`.
- `[entities.py:ProductEntity]` - catalog record with `formula_status` (`verified`, `unverified`, `missing`), `is_seed`, ingredient lists.
- `[entities.py:IngredientEntity]` - ingredient with safety attributes (`comedogenic`, `irritancy`, `is_pore_clogging`, `is_fungal_trigger`, `is_active`, `safety_class`).
- `[entities.py:SkinPersonaEntity]` / `[entities.py:PersonaExclusionsEntity]` - persona with `skin_type`, `sensitivity`, `target_concerns`, and exclusion flags.
- `[entities.py:ReviewEntity]` / `[entities.py:AspectObservationEntity]` - review plus frozen aspect observation (`aspect`, `sentiment`, `negated`, `quote_span`, `start`, `end`, `is_discovered`).
- `[entities.py:ScientificReferenceEntity]` - frozen reference with `evidence_level` (e.g. `clinical_trial`, `in_vitro`, `review`, `regulatory`).
- `[policies.py:evaluate_persona_match]` - deterministic product-vs-persona evaluation returning `[policies.py:PersonaMatchResult]` (`match_percentage`, `is_eligible`, `status`, `contributing_reasons`, `flagged_concerns`, `unknown_factors`, `coverage_score`).
- `[policies.py:normalize_ingredient_name]` - lowercase/whitespace normalization stripping `*`, `^`, dagger, and quote markers.
- `[policies.py]` canonical sets: `COMMON_FUNGAL_TRIGGERS`, `COMMON_DRYING_ALCOHOLS`, `COMMON_FRAGRANCES`.

## Invariants
- `[entities.py:ScientificReferenceEntity]`, `[entities.py:IngredientEntity]`, and `[entities.py:AspectObservationEntity]` are `@dataclass(frozen=True)` - immutable after construction.
- No module in `core/` imports frameworks, SQLite, Gemini, or catalog code (`[entities.py]` imports only `dataclasses`/`typing`; `[policies.py]` imports only `skintellect.core.entities`).
- `[policies.py:evaluate_persona_match]` returns `status="partial_unknown"` with `match_percentage=50` and `coverage_score=0.0` when the product formula is missing or empty - incomplete data is never scored as a match or a failure.
- `[policies.py:evaluate_persona_match]` penalty policy: fungal triggers -30, fragrances -25, drying alcohols -20, custom excluded ingredients -40 each (substring match on normalized names); barrier/actives bonuses capped at +10 (dry/oily) and +5 (sensitive); final score clamped to `[0, 100]`.
- `[policies.py:evaluate_persona_match]` eligibility rule: a product is eligible when it has no flagged concerns or its final score is >= 60 (`is_eligible = len(concerns) == 0 or final_score >= 60`).
- These entities/policies are currently a standalone domain contract: no production module outside `core/` imports `skintellect.core` (only `tests/test_agents_and_core.py` consumes it, verified by import search across `src/` and `tests/`).

## Side Effects
- None. No I/O, no network, no database access, no global mutable state; all functions are pure and deterministic.

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
