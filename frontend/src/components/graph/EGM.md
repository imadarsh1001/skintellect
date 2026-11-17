# graph

## Overview
Peanut package containing `IngredientGraph.vue`: a live-data ingredient-connections explorer over the compare tray. It takes the tray's `products` and fetches `GET /api/products/{id}/connections` (via `fetchConnections(id, 5)`) for each tray product, rendering per-product evidence panels ("graph" view) and a shared edge table ("table" view). There is no embedded dataset — all graph data comes from the backend.

## Interface
- `IngredientGraph.vue` (single file component, 264 lines); declares `defineProps<{ products: Product[] }>()` (`IngredientGraph.vue:18-20`) and no emits
- Local state (`IngredientGraph.vue:22-24`): `viewMode` = `'graph' | 'table'`, `connectionsByProduct` (per-tray-product `ProductConnections` payloads from `@/lib/types`), `loading`
- Data loading (`IngredientGraph.vue:29-52`): `loadAll()` calls `fetchConnections(id, 5)` (`frontend/src/lib/api.ts:143` → `GET /api/products/{id}/connections`) per tray product, on mount and on every compare-tray change
- Node styling (`IngredientGraph.vue:NODE_STYLES`, lines 67-71): node types `product | ingredient | reference` map to color/icon treatments
- Graph view (`IngredientGraph.vue:131-223`): per-product evidence `Card` panels — ingredient badges, related formulas/paths, reference nodes, and the backend `notice` when present
- Table view (`IngredientGraph.vue:226-261`): a flat edge table with `relation` and `evidence_id` columns across all tray products (not searchable — no query state exists)
- Rendering states (`IngredientGraph.vue:111-152`): loading skeleton while `loading`; empty state with `RouterLink to="/explore"` when the tray is empty; per-product error card with a Retry button; "related formulas" count badges

## Invariants
- All graph data is fetched at runtime from the backend; there is no embedded dataset and no static positions (the pre-rewrite static-SVG implementation is gone)
- Network failures are per-product: `loadAll()` records each product's `'error'` state and the view offers a Retry button (`IngredientGraph.vue:135-141`)
- The component renders from the compare tray only: an empty tray shows the empty state rather than fetching

## Side Effects
- Network: `fetchConnections(id, 5)` per compare-tray product, re-issued on mount and on every tray change; no storage or console access

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
