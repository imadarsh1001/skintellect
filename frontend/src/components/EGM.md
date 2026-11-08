# components

## Overview
Vue 3 single-file component layer of the frontend, organized into the shared `ui` primitive library (shadcn-vue wrappers over radix-vue) and four feature packages (`compare`, `explore`, `graph`, `research`) that compose those primitives. This directory contains no direct source files; it is an architectural grouping only. All components communicate upward via emits and consume backend data exclusively through `@/lib/api`.

## Subdirectories & Boundaries
- ui: [./ui/EGM.md](./ui/EGM.md) - Shared shadcn-vue style primitive library: badge, button, card, collapsible, dialog, input, scroll-area, select, separator, tabs (radix-vue wrappers, no domain logic)
- compare: [./compare/EGM.md](./compare/EGM.md) - `ProductComparisonMatrix.vue`: side-by-side INCI comparison matrix; purely presentational, all state changes delegated upward via emits
- explore: [./explore/EGM.md](./explore/EGM.md) - FilterSidebar, ProductGrid, ProductCard, ProductDetailModal, PersonaDrawer: catalog browsing; only `ProductDetailModal` fetches data (via `fetchProduct` from `@/lib/api`)
- graph: [./graph/EGM.md](./graph/EGM.md) - `IngredientGraph.vue`: self-contained ingredient co-occurrence explorer with curated static dataset; no props, no emits, no API calls
- research: [./research/EGM.md](./research/EGM.md) - `ResearchCopilot.vue`: streaming LangGraph copilot chat with sessions, HITL clarifications, citations, and agent-trace debugger; heaviest consumer of `@/lib/api`

## Cross-Package Invariants
- Feature components (`compare`, `explore`, `research`) declare all mutations as emits (`remove`, `clear-all`, `toggle-compare`, `update:*`, `reset`) and never mutate their props; parents own filter/compare/persona state
- All backend access from this layer funnels through `@/lib/api` functions; no component constructs URLs or calls `fetch` directly
- UI primitives under `ui/` are strictly generic (no app-domain logic); domain meaning lives only in `compare`, `explore`, `graph`, and `research`
- Shared styling vocabulary: `cn` from `@/lib/utils` plus Tailwind theme tokens mapped in `frontend/tailwind.config.js:extend.colors` (including the `evidence.*` token family)

## Cross-Package Side Effects
- Network calls at this level occur only in `explore/ProductDetailModal.vue` (`fetchProduct`) and `research/ResearchCopilot.vue` (`streamCopilot`, `fetchCopilotSessions`, `createCopilotSession`, `fetchCopilotSession`, `fetchEvidence`); `compare` and `graph` are offline components
- Clipboard write in `research/ResearchCopilot.vue:copyMessage`; external-link anchors (`target="_blank"`) in `explore/ProductDetailModal.vue` and the copilot citation modal; `v-html` markdown rendering in `ResearchCopilot.vue` (line 599)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
