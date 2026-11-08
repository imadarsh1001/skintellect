# compare

## Overview
Peanut package containing the product comparison feature: `ProductComparisonMatrix.vue`, a side-by-side INCI formulation matrix. Pure presentational component: derives all comparison data from its `products` prop and delegates every state change upward via events. No API calls.

## Interface
- `ProductComparisonMatrix.vue` (single file component, 200 lines)
- Props (`ProductComparisonMatrix.vue:defineProps`): `products: Product[]` (type from `@/lib/types`)
- Emits (`ProductComparisonMatrix.vue:defineEmits`):
  - `'remove'` with `productId: number` (fired from the per-card X button)
  - `'clear-all'` (fired from the "Clear Matrix" button)
  - `'ask-copilot-compare'` with `products: Product[]` (fired from "Analyze Comparison with Copilot" button)
- Derived data:
  - `sharedIngredients` computed (`ProductComparisonMatrix.vue:sharedIngredients`): case-insensitive intersection of every product's `names` list; empty unless `products.length >= 2`
  - `getUniqueIngredients(product)` (`ProductComparisonMatrix.vue:getUniqueIngredients`): case-insensitive difference of a product's `names` against all other compared products
- Rendering contract (`ProductComparisonMatrix.vue:template`): empty state when `products.length === 0`; otherwise a shared-ingredients banner (Badges with `variant="verified"`) and a CSS grid with `repeat(${products.length}, minmax(280px, 1fr))` columns of ui `Card`s showing brand, name, persona fit, formula provenance, key actives, unique ingredients, and total INCI count
- Persona fit badge precedence (`ProductComparisonMatrix.vue:template`, lines 124-144): `persona_match.match_status === 'match'` → `verified` badge with `persona_match.score`; `=== 'contraindicated'` → `negative` badge; else `match_score !== undefined` → `verified` with `match_score`; else `unknown`

## Invariants
- Comparison math is case-insensitive and derived only from the `names` arrays of the passed products (`sharedIngredients`, `getUniqueIngredients`); no backend recomputation
- The component never mutates `products`; removal and clearing are surfaced exclusively through the `remove`/`clear-all` emits
- Requires 2+ products for shared/unique ingredient computation to produce non-empty results (`sharedIngredients` guards on `products.length < 2`)
- Consumes only generic ui primitives (`@/components/ui/card`, `@/components/ui/badge`, `@/components/ui/button`); no direct network or storage access

## Side Effects
- None (all user intents are delegated upward via emits; Copilot analysis is triggered by the parent, not by this component)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
