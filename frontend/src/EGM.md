# src

## Overview
Vue 3 application source for the "Formulation Studio" SPA. Since the router introduction (redesign Stage 2), `vue-router` owns the workspace URLs and each route view owns its page state: `/` (ExploreView, URL-owned filters via `useExploreQuery`), `/compare` (CompareView), `/graph` (GraphView), `/copilot` (CopilotView). `App.vue` is the app shell — header/tabs, persona, compare tray, and the global detail modal — and passes shared state to views through `RouterView` slot props. Cross-feature state lives in small composables (`composables/usePersona`, `useCompareTray`, `useExploreQuery`); `main.ts` bootstraps the app and registers the router; `vite-env.d.ts` provides type shims.

## Local Interface & Invariants
- `main.ts` (`main.ts:1-6`): `createApp(App).use(router).mount('#app')`; imports the global stylesheet `./assets/index.css` (Tailwind v4 entry)
- `vite-env.d.ts` (`vite-env.d.ts:3-7`): ambient `declare module '*.vue'` shim plus `/// <reference types="vite/client" />`
- `router/index.ts`: routes `/` → ExploreView, `/compare` → CompareView, `/graph` → GraphView, `/copilot` → CopilotView, `/research` → redirect `/copilot`, catch-all → redirect `/`. `beforeEach` maps legacy hash deep links (`#copilot|#research|#chat` → `/copilot`, `#compare` → `/compare`, `#graph` → `/graph`) preserving query params
- `composables/useExploreQuery.ts`: the URL query string is the single source of truth for explore filters, sort, and page (`readQuery` maps `?search|domain|category|country|goal|price_tier|fungal_safe|fragrance_free|oil_free|pore_free|min_match|sort_by|page`; defaults in `DEFAULT_FILTERS`); exposes reactive `products/total/loading/error/activeFilterCount/filters/page/searchInput` and actions `setFilter` (pushes URL, resets page, serializes booleans as `'true'`), `setPage`, `resetFilters`, `reload`; the search input is debounced 300 ms (`refDebounced`) before it reaches the URL; every query change aborts the in-flight request via `AbortController` (aborted/superseded results are dropped, `DOMException` name `AbortError` ignored)
- `composables/usePersona.ts`: persona list + selection with persistence — writes `localStorage['skintellect_persona_id']` and reads it (plus legacy fallbacks `skintellect_active_persona_id`, `skinsort_active_persona_id`) on load; `saveCustom` posts via `savePersona` and re-selects
- `composables/useCompareTray.ts`: compare tray capped at 4 — `add` is optimistic then fetches `/api/products/{id}` (fetch-detail-on-add) when the payload lacks ingredient data, merging the detail response; persists tray ids under `localStorage['skintellect_compare_ids']` and restores by re-fetching details; `add` returns `'added'|'exists'|'limit'` (UI surfaces `limit` as a toast, not a blocking dialog)
- `App.vue` local symbols: `usePersona()` (`personas`, `currentPersona`, `selectPersona`, `saveCustomPersona` — save failure surfaces a `vue-sonner` toast), `useCompareTray()` (`comparedProducts`, `addToTray`, `removeFromCompare`, `clearTray`, `restoreTray`), `personaDrawerOpen`, detail-modal state (`selectedProduct`, `detailModalOpen`), `activeTab` derived from `route.name`, `toggleCompare`/`openCopilot` (ensure tray membership, navigate `/copilot`), `onTabSelect` (`router.push({ name })`)
- Rendering contract: header hosts persona button + legacy workspace anchors (`/research`, `/study`, `/progress` — Stage 5 folds these); tab bar is the shadcn `Tabs` component driven by `route.name`; `<RouterView v-slot>` passes `persona-id` and `compared-products` plus events (`toggle-compare`, `view-details`, `open-copilot`, `remove`, `clear-all`, `ask-copilot-compare`) to every route view; global overlays `PersonaDrawer` and `ProductDetailModal` and the `vue-sonner` `<Toaster>` are hosted here

## Subdirectories & Boundaries
- components: [./components/EGM.md](./components/EGM.md) - Vue component layer: `ui` primitive library plus the `compare`, `explore`, `graph`, `research` feature packages
- composables: [./composables](./composables) - focused stateful capabilities: `useExploreQuery` (URL-owned explore query), `usePersona` (persona + persistence), `useCompareTray` (tray + enrichment + persistence)
- lib: [./lib/EGM.md](./lib/EGM.md) - `api.ts` REST/SSE client (persona adapter, stats/connections), `types.ts` domain contracts, `utils.ts` (`cn` + `inciNames` ingredient-list helper)
- router: [./router/index.ts](./router/index.ts) - route table + legacy hash redirect map
- views: [./views](./views) - route components: `ExploreView` (domain/category strips, hero with live `/api/stats`, sidebar+grid, pagination, error/retry), `CompareView`, `GraphView`, `CopilotView` (thin wrappers delegating to feature components)

## Invariants
- The URL query on `/` is the authoritative explore state; views restore exactly from deep links, and every filter write goes through `useExploreQuery` actions (never mutate the returned `filters` object)
- Shared cross-feature state (persona, compare tray) is owned by `App.vue` via composables and flows down as props; views emit mutations up
- Comparison invariant: at most 4 products, enforced in `useCompareTray.add` (returns `'limit'`; UI toasts)
- Ingredient list invariant: display/diff code consumes ingredient names only through `utils.inciNames` — no API payload carries `names`; detail payloads carry `ingredients`
- Persona display values come from the API adapter in `api.ts` (`label` → `name`, `target_concerns` → `concerns`, `safety_exclusions` → `exclude_*`); `savePersona` maps back to the backend `PersonaCreate` contract
- No hardcoded catalog numbers are rendered: the hero stat row renders `/api/stats` values and hides when the fetch fails
- Router-owned workspaces mount/unmount on navigation (unlike the pre-router `v-show` tabs); any view-local state that must survive navigation lives in a composable with its own persistence

## Side Effects
- Network: `useExploreQuery` fetches `/api/products` on every query/persona change with `AbortController` cancellation; `usePersona` fetches `/api/personas` on load and posts on save; `useCompareTray` fetches `/api/products/{id}` per add/restore; `ExploreView` fetches `/api/stats` on mount
- Browser APIs: `history` writes via `vue-router` (path + query); `localStorage` keys `skintellect_persona_id` (read fallbacks: `skintellect_active_persona_id`, `skinsort_active_persona_id`) and `skintellect_compare_ids`; `window.scrollTo` on pagination
- Toasts: `vue-sonner` for comparison-limit and persona-save outcomes
- Styling: `main.ts:2` imports `./assets/index.css`, the Tailwind v4 entry consumed by all components

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
