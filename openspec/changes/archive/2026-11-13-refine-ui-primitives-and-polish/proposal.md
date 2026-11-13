# Proposal: refine-ui-primitives-and-polish

## Why

The `ui_components` rework (9 commits, PR to `main` pending) rebuilt the SPA on shadcn-vue/reka-ui patterns, but the follow-up audit in `component_map_and_gap_report.md` §5.2 shows four screens still drive hand-rolled control markup where installed-primitive equivalents would provide keyboard navigation and ARIA semantics for free, the research copilot lacks a session-delete affordance its API already supports, and the project has no written design source of truth — every future UI session re-derives tokens and conventions from code. This change executes the queued F1–F5 follow-ups plus a documentation-and-polish pass, before the follow-up queue ages past the PR that introduced it.

## What Changes

- **Author 6 missing UI primitives** in `frontend/src/components/ui/`: `toggle-group` (+ its `toggle` dep), `checkbox`, `switch`, `slider`, `sheet` — hand-authored from upstream shadcn-vue source (CLI crashes on Node 26), thin wrappers over reka-ui ^2.11.0 primitives already installed, each with its own `EGM.md` contract matching the existing ten packages.
- **F1** — `ExploreView.vue`: replace the hand-rolled domain/category strip and quick-filter chip buttons with `ToggleGroup` (single/multi as today); `setFilter` URL semantics preserved exactly.
- **F2** — `FilterSidebar.vue`: swap 4 native `<select>` → `Select`, checkboxes → `Checkbox`, strict fungal/fragrance exclusions → `Switch`, range → `Slider`, price tiers → `ToggleGroup`; wrap the sidebar in a `Sheet` on <lg widths.
- **F3** — `ProductDetailModal.vue`: replace the 10 hand-rolled tab-button references with the installed `Tabs` primitive (keyboard arrow nav + ARIA tab pattern come free).
- **F4** — `PersonaDrawer.vue`: swap 3 native checkboxes → `Checkbox`/`Switch`, skin-type preset buttons → `ToggleGroup`; keep instant-apply-on-preset and the `POST /api/personas` save.
- **F5** — `ResearchCopilot.vue`: add session delete affordance with toast confirm (backend API already supports it).
- **Design system documentation**: capture the durable product context and the established token/component system into `PRODUCT.md` and `frontend/DESIGN.md` (impeccable `init`/`document` mode), so future sessions read the written source of truth instead of re-deriving it.
- **Critique/audit/polish passes**: run impeccable `critique` + `audit` (heuristic UX scoring; a11y/perf/responsive checks) over the touched screens, fix findings within refinement scope, and finish with a `polish` pass including runtime keyboard-a11y verification (§5.3 residual closed by F3 + this pass).

## Capabilities

### New Capabilities
- `ui-primitives`: requirements the shared control library must satisfy — export surfaces, variant/size conventions, keyboard/ARIA behavior inherited from reka-ui, and per-package EGM contracts — for the six newly authored packages.
- `explore-filtering`: how the Explore screen's filter controls behave — domain/category strip, quick-filter chips, sidebar select/checkbox/switch/slider/price controls, mobile Sheet — and the invariant that filter state stays URL-owned with today's semantics.
- `product-detail`: how the product detail modal's tabbed sections behave — selectable tabs with keyboard arrow navigation and the ARIA tab pattern.
- `persona-controls`: how the persona drawer's controls behave — checkbox/switch bindings, skin-type preset ToggleGroup, instant-apply-on-preset, and persona save.
- `copilot-sessions`: how research copilot session lifecycle actions behave — specifically session deletion with an explicit confirmation step.

### Modified Capabilities
(none — `openspec/specs/` is empty; this is the first capability set)

## Impact

- **Code**: 6 new directories under `frontend/src/components/ui/` (+ EGM.md contracts); edits to `ExploreView.vue`, `FilterSidebar.vue`, `ProductDetailModal.vue`, `PersonaDrawer.vue` (all under `frontend/src/components/explore/`) and `frontend/src/components/research/ResearchCopilot.vue`; new `PRODUCT.md` (repo root) and `frontend/DESIGN.md`.
- **Dependencies**: none added — reka-ui ^2.11.0, Tailwind ^4.3.5, tw-animate-css already installed.
- **APIs/backend**: none changed (F5 consumes an existing delete endpoint).
- **Build/gates**: every pass must pass `npm run build`, `scripts/check.py`, `tests/check_ui_semantics.js`, and a `tests/ui_smoke.py` re-run with the backend up.
- **CI**: extends `.github/workflows/checks.yml` with a frontend job (`npm run build`, `tests/check_ui_semantics.js`); `ui_smoke.py` intentionally stays local-only (live dev backend + disposable dev DB).

## Out of Scope

- **F6 (claim-level inline citations)** — blocked on the backend stream carrying per-claim `evidence_id`s; spec'd separately once unblocked.
- **Frontend unit-test framework** — declared an explicit non-goal for this effort (§5.3).
- **Copilot session-composable extraction** — intentionally deferred (§5.3); F5 stays inline in `ResearchCopilot.vue`.
- **Visual redesign / identity change** — this is refinement: the established shadcn-vue token system, copy, and layout identities are preserved; "refinement preserves; redesign replaces".
- **`vue-flow` graph library** — deferred until interactive exploration is a stated requirement (§5.3, row 13).
- **Header badge 390px wrap** — cosmetic §5.3 residual; may be picked up opportunistically inside the polish pass but is not a deliverable of this change.
