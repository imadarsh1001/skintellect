# explore

## Overview
Peanut package containing the product-catalog exploration feature: five `.vue` single-file components covering the filter sidebar, product grid/cards, detail modal, and persona selection drawer. All components are presentational except `ProductDetailModal.vue`, which fetches full product details from the backend API layer.

## Interface
- `FilterSidebar.vue`:
  - Props (`FilterSidebar.vue:defineProps`): `search: string`, `category: string`, `country: string`, `goal: string`, `priceTier: string`, `fungalSafe: boolean`, `fragranceFree: boolean`, `oilFree: boolean`, `poreFree: boolean`, `minMatch: number`, `sortBy: string`
  - Emits (`FilterSidebar.vue:defineEmits`): `update:<propName>` for each prop plus `'reset'`
  - Static option lists (`FilterSidebar.vue:priceTiers`, `sortOptions`, `categories`, `countries`, `goals`); sort values: `composite_desc | match_desc | rating_desc | reviews_desc | price_asc | price_desc`
  - `activeFilterCount` computed (`FilterSidebar.vue:activeFilterCount`, lines 85-98) counts non-default filter values
  - Renders native `<select>`, `<input type="checkbox">`, and `<input type="range" min="0" max="95" step="5">` elements plus ui `Button`/`Input`
- `ProductGrid.vue`:
  - Props (`ProductGrid.vue:defineProps`): `products: Product[]`, `loading: boolean`, `comparedIds: number[]`
  - Emits (`ProductGrid.vue:defineEmits`): `'toggle-compare'`, `'open-copilot'`, `'view-details'` (each with `product: Product`, re-emitted from `ProductCard`), `'reset-filters'`
  - Three render states (`ProductGrid.vue:template`): skeleton grid of 6 pulse cards when `loading`; empty state with "Reset All Filters" when `products.length === 0`; else responsive 1/2/3-column grid of `ProductCard`
- `ProductCard.vue`:
  - Props (`ProductCard.vue:defineProps`): `product: Product`, `isCompared: boolean`
  - Emits (`ProductCard.vue:defineEmits`): `'toggle-compare'`, `'open-copilot'`, `'view-details'`
  - `getMatchScoreColor(score)` (`ProductCard.vue:getMatchScoreColor`): score >= 90 → teal `#12635a`, >= 70 → blue `#245ba9`, else amber `#805309`
  - Formula badge precedence (`ProductCard.vue:template`, lines 44-68): `formula_status === 'verified_complete'` → verified; `=== 'unverified'` → unknown; else negative "Missing Formula"
  - Safety strip flags require truthy integer: `fungal_acne_safe === 1`, `fragrance_free === 1`, `alcohol_free === 1` (lines 128, 134, 140); key actives truncated to `key_actives.slice(0, 3)`, INCI excerpt to `names.slice(0, 4)`
- `ProductDetailModal.vue`:
  - Props (`ProductDetailModal.vue:defineProps`): `open: boolean`, `product: Product | null`, `currentPersona: SkinPersona`, `isCompared: boolean`
  - Emits (`ProductDetailModal.vue:defineEmits`): `'update:open'`, `'open-copilot'`, `'toggle-compare'`, `'select-product'` (fired by `inspectAlternative`, `ProductDetailModal.vue:inspectAlternative`)
  - Local state (`ProductDetailModal.vue:46-50`): `activeTab` = `'safety' | 'ingredients' | 'dupes' | 'reviews' | 'raw'`, `loading`, `detailedProduct`, `ingredientSearch`, `reviewSkinFilter`
  - `loadDetails()` (`ProductDetailModal.vue:loadDetails`): seeds `detailedProduct` with a spread of the summary `product` prop, then awaits `fetchProduct(props.product.id, props.currentPersona.id)` from `@/lib/api`; on failure logs `console.warn('Failed to load full product details:', err)` and keeps the seed
  - Watches (`ProductDetailModal.vue:66-85`): on `open` becoming true, resets `activeTab='safety'`, `ingredientSearch=''`, `reviewSkinFilter='all'` and calls `loadDetails`; on `product.id` change while open, reloads
  - Computed: `filteredIngredients` (falls back to mapping `names` to `{ name, function: 'Skin Conditioning' }` entries, `ProductDetailModal.vue:filteredIngredients`), `dupesList` (`similar_products` falling back to `alternatives`), `filteredReviews` (filters by `reviewer_skin_type`), `reviewSkinCounts` (fixed buckets `all|sensitive|oily|dry|combination|normal`)
  - Template: five hand-rolled tab buttons (not ui Tabs); Raw JSON tab renders `JSON.stringify(detailedProduct, null, 2)` labeled "FastAPI Verified Payload" (lines 578-580); footer anchors to `detailedProduct.url` with `target="_blank" rel="noopener noreferrer"` (lines 588-597)
- `PersonaDrawer.vue`:
  - Props (`PersonaDrawer.vue:defineProps`): `open: boolean`, `currentPersona: SkinPersona`, `availablePersonas: SkinPersona[]`
  - Emits (`PersonaDrawer.vue:defineEmits`): `'update:open'`, `'select-persona'` (persona), `'save-custom-persona'` (persona)
  - Local state: `editedPersona = ref<SkinPersona>({ ...props.currentPersona })` (`PersonaDrawer.vue:editedPersona`)
  - Behavior (`PersonaDrawer.vue:selectExisting`, `toggleGoal`, `applyCustom`): preset selection emits `select-persona` and closes; goal chips toggle membership in `editedPersona.goals`; "Apply & Recalculate Matches" emits `save-custom-persona` with the edited copy and closes
  - Static contracts (`PersonaDrawer.vue:28-29`): `skinTypes` = `oily | dry | combination | sensitive | normal`; `commonGoals` = 6 labeled goals

## Invariants
- `FilterSidebar` is fully controlled: every value change is emitted upward (`update:*`); it never mutates props and owns no filter state
- `ProductDetailModal` reloads via `loadDetails` whenever it opens or the product id changes; the modal shows the optimistic summary product first and only upgrades to fetched details, so rendering never blocks on the network
- `PersonaDrawer` snapshots `currentPersona` into `editedPersona` at setup (`PersonaDrawer.vue:31`) with no `watch` syncing later prop changes; edits are local until `save-custom-persona` is emitted
- `ProductGrid`/`ProductCard` never mutate `products`; compare/copilot/detail intents are all delegated upward through emits
- Empty-safety contract: `fungal_acne_safe`/`fragrance_free`/`alcohol_free` flags are compared against integer `1` in `ProductCard.vue` (lines 128, 134, 140) and `oil_free`/`silicone_free` the same way in `ProductDetailModal.vue` (lines 316, 322), matching the backend's SQLite boolean representation

## Side Effects
- `ProductDetailModal.vue:loadDetails`: performs an HTTP GET through `fetchProduct` (`@/lib/api`) every time the modal opens or the viewed product changes
- `ProductDetailModal.vue:template` footer: opens an external product URL in a new tab (`target="_blank"`)
- `ProductDetailModal.vue:loadDetails` catch path: logs to the browser console (`console.warn`)
- `FilterSidebar`, `ProductGrid`, `ProductCard`, `PersonaDrawer`: none (no network, storage, or console access)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
