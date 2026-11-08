# graph

## Overview
Peanut package containing `IngredientGraph.vue`: a self-contained ingredient co-occurrence network explorer with an interactive SVG graph view and an accessible searchable table view. The dataset is curated static data embedded in the component; it declares no props and no emits and performs no API calls.

## Interface
- `IngredientGraph.vue` (single file component, 258 lines); declares no props and no emits (self-contained)
- Local data model:
  - `GraphNode` interface (`IngredientGraph.vue:GraphNode`, lines 8-16): `id`, `name`, `category: 'barrier' | 'hydrator' | 'soother' | 'active' | 'excipient'`, `frequency`, `x`, `y`, `role_description`
  - `GraphLink` interface (`IngredientGraph.vue:GraphLink`, lines 18-22): `source`, `target`, `weight`
- Embedded dataset (`IngredientGraph.vue:nodes`, lines 25-37: 11 curated moisturizer ingredients; `IngredientGraph.vue:links`, lines 39-52: 12 weighted co-occurrence links, weights 2-5)
- Local state (`IngredientGraph.vue:54-56`): `selectedNode` (defaults to the first node, `ceramide-np`), `viewMode` = `'graph' | 'table'`, `searchQuery`
- Computed `filteredNodes` (`IngredientGraph.vue:filteredNodes`): case-insensitive substring filter over `name` and `role_description` (used only in table view)
- Helpers: `getCategoryColor(category)` (`IngredientGraph.vue:getCategoryColor`, lines 64-72: barrier `#12635a`, hydrator `#245ba9`, soother `#6843a8`, active `#0e6870`, excipient `#526277`) and `getNode(id)` (`IngredientGraph.vue:getNode`)
- Rendering contract (`IngredientGraph.vue:template`): graph view renders a static-position SVG (`viewBox="100 80 500 300"`, line 126) where links use `weight` as stroke width and clicking a node sets `selectedNode` (r 17 → 22 when selected); dossier card shows category, `frequency`%, `role_description`, and synergistic co-ingredients derived from links touching `selectedNode`; table view renders a searchable `<table>` with functional class chips colored by `getCategoryColor`

## Invariants
- The network dataset is static and curated in component source (`IngredientGraph.vue:nodes`/`links`, comment at line 24: "Curated high-fidelity moisturizer ingredient network"); positions `x`/`y` are fixed constants, there is no physics/force layout and no runtime data loading
- Every `link.source`/`link.target` must reference a node `id` present in `nodes`; `getNode` returns `undefined` for missing ids, which renders degenerate `<line>` coordinates rather than throwing
- `getCategoryColor` enumerates exactly the five `GraphNode['category']` values; adding a category without extending the switch yields `undefined` color
- No props/emits: the component cannot be parameterized from outside; `selectedNode`, `viewMode`, and `searchQuery` reset on unmount only

## Side Effects
- None (no network, storage, or console access)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
