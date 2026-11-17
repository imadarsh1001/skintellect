# explore

## Overview
Peanut package containing the product-catalog exploration feature: five `.vue` single-file components covering the filter sidebar, product grid/cards, detail modal, and persona selection drawer. All components are presentational except `ProductDetailModal.vue`, which fetches full product details from the backend API layer.

## Interface
- `FilterSidebar.vue`:
  - Two-way bindings (`FilterSidebar.vue:defineModel`, lines 15-27): `search`, `category`, `country`, `goal`, `priceTier`, `fungalSafe`, `fragranceFree`, `oilFree`, `poreFree`, `minMatch`, `sortBy` — 11 `defineModel` filters (no `defineProps`)
  - Emits (`FilterSidebar.vue:defineEmits`): `'reset'` only; the active-filter count lives in `useExploreQuery` (`activeFilterCount`), not in the sidebar
  - Static option lists (`FilterSidebar.vue:priceTiers`, `sortOptions`, `categories`, `countries`, `goals`); sort values: `composite_desc | match_desc | rating_desc | reviews_desc | price_asc | price_desc`
  - Renders reka/shadcn primitives: `Select`, `Switch`, `Slider` (`:min="0" :max="95" :step="5"`), `ToggleGroup` (price tiers), plus ui `Button`/`Input` (`FilterSidebar.vue:5-8,182-240`)
- `ProductGrid.vue`:
  - Props (`ProductGrid.vue:defineProps`): `products: Product[]`, `loading: boolean`, `comparedIds: number[]`
  - Emits (`ProductGrid.vue:defineEmits`): `'toggle-compare'`, `'open-copilot'`, `'view-details'` (each with `product: Product`, re-emitted from `ProductCard`), `'reset-filters'`
  - Three render states (`ProductGrid.vue:template`): skeleton grid of 6 pulse cards when `loading`; empty state with "Reset All Filters" when `products.length === 0`; else responsive 1/2/3-column grid of `ProductCard`
- `ProductCard.vue`:
  - Props (`ProductCard.vue:defineProps`): `product: Product`, `isCompared: boolean`
  - Emits (`ProductCard.vue:defineEmits`): `'toggle-compare'`, `'open-copilot'`, `'view-details'`
  - `getMatchScoreColor(score)` (`ProductCard.vue:getMatchScoreColor`, lines 31-35): score >= 90 → `verified` token `#246e3a`, >= 70 → `source` token `#215c78`, else `unknown` token `#4d4641`
  - Persona fit score counts up on arrival via `useCountUp` from `@/lib/motion` (`ProductCard.vue:5,41-42`)
  - Formula badge precedence (`ProductCard.vue:template`, lines 58-80): `formula_status === 'verified_complete'` → verified; `=== 'unverified'` → unknown; else negative "Missing Formula"
  - Safety strip flags require truthy integer: `fungal_acne_safe === 1`, `fragrance_free === 1`, `alcohol_free === 1` (lines 151, 157, 163); key actives truncated to `key_actives.slice(0, 3)`, INCI excerpt to `names.slice(0, 4)`
- `ProductDetailModal.vue`:
  - Props (`ProductDetailModal.vue:defineProps`): `open: boolean`, `product: Product | null`, `currentPersona: SkinPersona`, `isCompared: boolean`
  - Emits (`ProductDetailModal.vue:defineEmits`): `'update:open'`, `'open-copilot'`, `'toggle-compare'`, `'select-product'` (fired by `inspectAlternative`, `ProductDetailModal.vue:inspectAlternative`)
  - Local state (`ProductDetailModal.vue:57-62`): `activeTab` = `'safety' | 'ingredients' | 'dupes' | 'reviews' | 'raw'`, `loading`, `loadError` (retry affordance), `detailedProduct`, `ingredientSearch`, `reviewSkinFilter`, `imageState` (`'idle' | 'loading' | 'ok' | 'failed'` for the on-demand image proxy)
  - `loadDetails()` (`ProductDetailModal.vue:loadDetails`): seeds `detailedProduct` with a spread of the summary `product` prop, then awaits `fetchProduct(props.product.id, props.currentPersona.id)` from `@/lib/api`; on failure logs `console.warn('Failed to load full product details:', err)`, sets `loadError`, and keeps the seed
  - Product image loads on demand through the proxy `GET /api/products/{id}/image` with `imageState` loading/ok/failed handling (`ProductDetailModal.vue:88-96,182-192`)
  - Watches (`ProductDetailModal.vue:99-118`): on `open` becoming true, resets `activeTab='safety'`, `ingredientSearch=''`, `reviewSkinFilter='all'` and calls `loadDetails`; on `product.id` change while open, reloads
  - Computed: `filteredIngredients` (falls back to mapping `names` to `{ name, function: 'Skin Conditioning' }` entries, `ProductDetailModal.vue:filteredIngredients`), `dupesList` (`similar_products` falling back to `alternatives`), `filteredReviews` (filters by `reviewer_skin_type`), `reviewSkinCounts` (fixed buckets `all|sensitive|oily|dry|combination|normal`)
  - Template: ui Tabs primitives (`Tabs`/`TabsList`/`TabsTrigger`, `ProductDetailModal.vue:11,264-268`); Raw JSON tab renders `JSON.stringify(detailedProduct, null, 2)` labeled "FastAPI Verified Payload" (lines 663-664); footer anchors to `detailedProduct.url` with `target="_blank" rel="noopener noreferrer"` (lines 673-682)
- `PersonaDrawer.vue`:
  - Props (`PersonaDrawer.vue:defineProps`): `open: boolean`, `currentPersona: SkinPersona`, `availablePersonas: SkinPersona[]`
  - Emits (`PersonaDrawer.vue:defineEmits`): `'update:open'`, `'select-persona'` (persona), `'save-custom-persona'` (persona)
  - Local state: `editedPersona = ref<SkinPersona>({ ...props.currentPersona })` (`PersonaDrawer.vue:editedPersona`)
  - Behavior (`PersonaDrawer.vue:selectExisting`, `onGoalsUpdate`, `applyCustom`): preset selection emits `select-persona` and closes; goal toggling goes through ui `ToggleGroup` + `onGoalsUpdate` (`PersonaDrawer.vue:40-42,111-116`; the old `toggleGoal` chip handler is gone); "Apply & Recalculate Matches" emits `save-custom-persona` with the edited copy and closes
  - Strict exclusions UI: skin-type `ToggleGroup` (lines 88-106) and a "Strict Ingredient Contraindications" section with three `Switch`es bound to `exclude_fungal_acne_triggers`/`exclude_fragrance`/`exclude_drying_alcohols` (lines 128-154)
  - Static contracts (`PersonaDrawer.vue:29-30`): `skinTypes` = `oily | dry | combination | sensitive | normal`; `commonGoals` = 6 labeled goals

## Invariants
- `FilterSidebar` is a two-way-bound component: its 11 filters are `defineModel` bindings (the sidebar writes model values directly, e.g. `minMatch.value = Number(v[0])`), `'reset'` is the only emit; `useExploreQuery` owns the authoritative state
- `ProductDetailModal` reloads via `loadDetails` whenever it opens or the product id changes; the modal shows the optimistic summary product first and only upgrades to fetched details, so rendering never blocks on the network
- `PersonaDrawer` snapshots `currentPersona` into `editedPersona` at setup (`PersonaDrawer.vue:32`) with no `watch` syncing later prop changes; edits are local until `save-custom-persona` is emitted
- `ProductGrid`/`ProductCard` never mutate `products`; compare/copilot/detail intents are all delegated upward through emits
- Empty-safety contract: `fungal_acne_safe`/`fragrance_free`/`alcohol_free` flags are compared against integer `1` in `ProductCard.vue` (lines 151, 157, 163) and `oil_free`/`silicone_free` the same way in `ProductDetailModal.vue` (lines 378, 384), matching the backend's SQLite boolean representation

## Side Effects
- `ProductDetailModal.vue:loadDetails`: performs an HTTP GET through `fetchProduct` (`@/lib/api`) every time the modal opens or the viewed product changes; the product image is fetched on demand through the proxy route with per-state handling
- `ProductDetailModal.vue:template` footer: opens an external product URL in a new tab (`target="_blank"`)
- `ProductDetailModal.vue:loadDetails` catch path: logs to the browser console (`console.warn`)
- `FilterSidebar`, `ProductGrid`, `ProductCard`, `PersonaDrawer`: none (no network, storage, or console access)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
