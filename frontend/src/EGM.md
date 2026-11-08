# src

## Overview
Vue 3 application source for the "Formulation Studio" SPA. `App.vue` is the single root state owner: it holds all filter, persona, comparison, tab, and modal state, loads catalog/persona data through `@/lib/api`, and wires the four feature workspaces (explore, compare, graph, copilot) mounted under `components/`. `main.ts` bootstraps the app; `vite-env.d.ts` provides type shims.

## Local Interface & Invariants
- `main.ts` (`main.ts:1-5`): creates and mounts the Vue app — `createApp(App).mount('#app')`; imports the global stylesheet `./assets/index.css` (Tailwind entry) and `./App.vue`
- `vite-env.d.ts` (`vite-env.d.ts:3-7`): ambient `declare module '*.vue'` shim plus `/// <reference types="vite/client" />`
- `App.vue` local symbols:
  - Tabs state `activeTab` (`App.vue:activeTab`, line 31): `'explore' | 'compare' | 'graph' | 'copilot'`, default `'explore'`
  - Catalog state (`App.vue:32-35`): `products`, `loading`, `totalProducts`, `comparedProducts` (comparison set capped at 4)
  - Persona state (`App.vue:38-50`): `personas`, `currentPersona` seeded with a hardcoded default persona `id: 'uap'` ("Universal Adult Sensitive & Acne", lines 39-49), `personaDrawerOpen`
  - Filter state (`App.vue:57-68`): `search`, `selectedDomain` (`all|skin|hair|body|makeup` buttons, template lines 336-370), `selectedCategory`, `selectedCountry`, `selectedGoal`, `priceTier`, `fungalSafe`, `fragranceFree`, `oilFree`, `poreFree`, `minMatch`, `sortBy` (default `'composite_desc'`)
  - `loadData()` (`App.vue:loadData`, lines 70-106): `Promise.all([fetchProducts(...), fetchPersonas()])` with all filters and `persona_id: currentPersona.value.id`; adopts the server persona with `id === 'uap'` when the current persona is still the default; `console.error('Failed to load initial catalog data', err)` on failure
  - Filter watcher (`App.vue:109-124`): any of the 12 filter refs changing triggers `loadData()`
  - `resetFilters()` (`App.vue:resetFilters`, lines 126-139), `quickFilter(type)` (`App.vue:quickFilter`, lines 141-151)
  - `handleSelectPersona(p)` (`App.vue:153-156`): swaps persona and reloads
  - `handleSaveCustomPersona(p)` (`App.vue:handleSaveCustomPersona`, lines 158-166): persists via `savePersona`; on failure logs `console.warn('Persona persisted in session state', e)` and continues with session-only persona
  - `toggleCompare(prod)` (`App.vue:toggleCompare`, lines 168-179): id-based toggle; rejects a 5th product with `alert('You can compare up to 4 formulations simultaneously.')`
  - `viewDetails(prod)` (`App.vue:181-184`), `openCopilot(prod)` (`App.vue:openCopilot`, lines 186-191: adds product to the comparison set if absent, then switches to the copilot tab), `handleCopilotCompare(prods)` (`App.vue:193-195`: switches tab; the passed products argument is not used)
  - Deep-link routing in `onMounted` (`App.vue:197-210`): URL path containing `research` or hash `#copilot|#research|#chat` → copilot tab; `compare` → compare; `graph` → graph; `study` → explore
  - Hash writer (`App.vue:212-216`): on `activeTab` change, sets `window.location.hash = tab` when on the root path
- Rendering contract (`App.vue:template`): four workspace sections rendered with `v-show` (lines 331, 504, 514, 519) — all child components stay mounted across tab switches; static header nav anchors to `/research`, `/study`, `/progress` (lines 245-265); global overlays `PersonaDrawer` (lines 530-537) and `ProductDetailModal` (lines 540-549) are hosted here, as are the FilterSidebar filter wiring (lines 465-489) and ResearchCopilot `active-product-ids`/`persona-id` props (lines 520-522)

## Subdirectories & Boundaries
- components: [./components/EGM.md](./components/EGM.md) - Vue component layer: `ui` primitive library plus the `compare`, `explore`, `graph`, `research` feature packages
- lib: [./lib/EGM.md](./lib/EGM.md) - `api.ts` REST/SSE client, `types.ts` domain contracts, `utils.ts` (`cn` Tailwind merge helper)

## Invariants
- `App.vue` is the single source of truth for cross-feature state; feature components under `components/` are controlled and delegate all mutations back via emits (see [./components/EGM.md](./components/EGM.md))
- All network access flows through `@/lib/api`; `App.vue` calls only `fetchProducts`, `fetchPersonas`, `savePersona` (`App.vue:4`)
- Comparison invariant: `comparedProducts` holds at most 4 `Product`s, enforced in `toggleCompare` with a blocking `alert`
- Persona invariant: `currentPersona.id` defaults to `'uap'` and is replaced by a server persona with the same id when `fetchPersonas` returns one; custom personas remain session-only if `savePersona` fails
- The four workspace sections use `v-show`, so switching tabs never remounts feature components nor resets their internal state

## Side Effects
- Network: `fetchProducts`/`fetchPersonas` on mount and on every filter or persona change (`App.vue:loadData`); `savePersona` on custom persona save
- Browser APIs: `window.location.hash` writes (`App.vue:214`), `window.location.pathname`/`hash` reads for deep-link routing (`App.vue:199-209`), blocking `alert()` on comparison overflow (`App.vue:174`)
- Console: `console.error` in `loadData` (line 102), `console.warn` in `handleSaveCustomPersona` (line 163)
- Styling: `main.ts:2` imports `./assets/index.css`, the Tailwind entry that registers the theme variables consumed by all components

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
