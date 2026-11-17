# components

## Overview
Vue 3 single-file component layer of the frontend, organized into the shared `ui` primitive library (shadcn-vue wrappers over reka-ui) and five feature packages (`ai`, `compare`, `explore`, `graph`, `research`) that compose those primitives; `ai` holds the reusable shadcn-vue AI Elements pattern components (ChatMessages/Message Scroller, PromptInput, SuggestionChip, SourcesList, TaskPlan, AgentTrace). This directory contains no direct source files; it is an architectural grouping only. All components communicate upward via emits and consume backend data exclusively through `@/lib/api`.

## Subdirectories & Boundaries
- ui: [./ui/EGM.md](./ui/EGM.md) - Shared shadcn-vue style primitive library: badge, button, card, checkbox, collapsible, dialog, input, scroll-area, select, separator, sheet, slider, switch, tabs, toggle, toggle-group (16 packages, no domain logic)
- ai: [./ai/EGM.md](./ai/EGM.md) - Reusable AI-pattern components: `ChatMessages`, `PromptInput`, `SuggestionChip`, `SourcesList`, `TaskPlan`, `AgentTrace`
- compare: [./compare/EGM.md](./compare/EGM.md) - `ProductComparisonMatrix.vue`: side-by-side INCI comparison matrix; purely presentational, all state changes delegated upward via emits
- explore: [./explore/EGM.md](./explore/EGM.md) - FilterSidebar, ProductGrid, ProductCard, ProductDetailModal, PersonaDrawer: catalog browsing; `ProductDetailModal` fetches data (via `fetchProduct` and the image proxy from `@/lib/api`)
- graph: [./graph/EGM.md](./graph/EGM.md) - `IngredientGraph.vue`: live-data connections explorer for the compare-tray products; takes a `products` prop and fetches `/api/products/{id}/connections` per tray product (graph/table view modes)
- research: [./research/EGM.md](./research/EGM.md) - `ResearchCopilot.vue`: streaming LangGraph copilot chat with sessions, HITL clarifications, citations, and agent-trace debugger; heaviest consumer of `@/lib/api`

## Cross-Package Invariants
- Feature components (`compare`, `explore`, `research`) declare mutations as emits (`remove`, `clear-all`, `toggle-compare`, `update:*`, `reset`) or `defineModel` two-way bindings (`explore/FilterSidebar` binds its 11 filters via `defineModel`) and never mutate their props; parents own filter/compare/persona state
- All backend access from this layer funnels through `@/lib/api` functions; no component constructs URLs or calls `fetch` directly
- UI primitives under `ui/` are strictly generic (no app-domain logic); domain meaning lives only in `compare`, `explore`, `graph`, and `research`
- Shared styling vocabulary: `cn` from `@/lib/utils` plus Tailwind theme tokens mapped in `src/assets/index.css` `@theme inline` (including the `evidence.*` token family; there is no `tailwind.config.js` — Tailwind v4 is CSS-first)

## Cross-Package Side Effects
- Network calls at this level occur in `explore/ProductDetailModal.vue` (`fetchProduct`, plus the on-demand image proxy), `graph/IngredientGraph.vue` (`fetchConnections` per tray product), and `research/ResearchCopilot.vue` (`streamCopilot`, `askCopilot`, `fetchCopilotSessions`, `createCopilotSession`, `fetchCopilotSession`, `deleteCopilotSession`, `fetchProduct`, `fetchEvidence`); `compare` is the only offline feature package
- Clipboard write in `research/ResearchCopilot.vue:copyMessage`; external-link anchors (`target="_blank"`) in `explore/ProductDetailModal.vue` and the copilot citation modal; `v-html` markdown rendering in `ResearchCopilot.vue` (line 506)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
