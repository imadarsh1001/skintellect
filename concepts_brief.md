# Skintellect UI Redesign

* **Author:** Adarsh Patel
* **Date:** 2026-11-09

## Overview

Skintellect's web surface is currently three disconnected UIs speaking two design languages: a Vue 3 SPA (`frontend/`) that fakes routing with hash writes and `v-show` tab switching (`frontend/src/App.vue:200,214,331-519`), four always-server-rendered legacy pages (`/research`, `/study`, `/progress`) plus a 2,922-line legacy index fallback (`src/skintellect/web/templates/index.html`), and a Tailwind token system in the SPA versus `workspace.css` in the legacy pages. The concept under review replaces this with ONE Vue SPA on real `vue-router` routes (`/`, `/compare`, `/graph`, `/copilot`), upgrades the component platform from radix-vue 1.9.11 (dormant upstream) + Tailwind 3.4 to shadcn-vue on reka-ui 2.x + Tailwind v4, adopts upstream shadcn-vue AI Elements patterns for the research copilot (Message Scroller, Prompt Input, Suggestion, Sources, Inline Citation, Trace, plus Chat/Plan/Task/Reasoning/Tool), keeps custom code only for persona-scoped scoring display, formulation diffing, and claim-to-evidence binding, retires or folds in the legacy pages, fixes the backend SSE crash (`src/skintellect/gemini.py:57-63`), and wires data-starved screens (compare names, graph data, hero stats, pagination) to real APIs.

This brief was produced by six EGM brainstorm lenses (design, codebase-details, zoom-out, comprehension, implementation-readiness, structural) in `Mode: BRAINSTORM`. This harness cannot nest subagents, so the lenses were executed by direct sequential dispatch by the synthesizer rather than as independent stateless subagent instances; all findings below were verified against source on branch `ui_components` at `4459c15` (clean), including the code contracts `EGM.md` and `frontend/EGM.md`.

Critique first: the direction is defensible, but three findings must change how it is executed before drafting. (1) The streaming rebuild is pointless until the Gemini `run_budget` ContextVar crash is fixed, and the current silent client-side fallback means the team can ship without noticing streaming is dead. (2) The platform upgrade carries real migration cost with zero user-visible value by itself; its only justification is that upstream AI Elements requires current shadcn-vue, so it must be time-boxed and isolated or deferred. (3) The one UI regression gate that exists (`tests/check_ui_semantics.js`) tests the legacy `workspace.js`, not the SPA — the safety net this concept relies on is guarding code this concept deletes.

## Analysis

### 1. Route architecture and legacy disposition

The current routing is ambiguous by construction: `src/skintellect/api/app.py:56-95` serves the built SPA for `/`, `/compare`, `/graph` only when `dist/` exists (legacy template otherwise), always serves legacy templates for `/research`, `/study`, `/progress`, and the SPA's hash pseudo-routing (`App.vue:200-214`) reads paths `/research|/compare|/graph|/study` to pick tabs. The legacy workspace nav links to `/#copilot` (which works only because of the hash hack), and the SPA navbar links back to the legacy pages (`App.vue:246-260`). The zoom-out lens raises the strongest partial counter-argument here: the legacy `/research`, `/study`, and `/progress` pages are the ONLY working UIs for real backend features (structured evidence workflow, prepared demo + quality checks, preparation-job submit/cancel/poll), they are small (`research.js` 169 lines, `study.js` 165, `progress.js` 93), and folding them into the SPA during the same effort as the platform migration inflates the blast radius. The middle path adopted below: the SPA owns these routes only when SPA equivalents exist; templates stay in-tree as rollback until per-page parity is verified; deletion happens at a defined end state, not "eventually".

Two migration hazards were verified in code and must be handled explicitly. First, hash deep links: existing bookmarks and the workspace nav use `/#copilot`, `/#compare`, `/#graph`; vue-router must redirect these on first load or users silently lose context. Second, query-parameter carry-over: `/research` reads `?query=` and `?demo=1` (`src/skintellect/web/static/js/research.js:9-10`); whatever absorbs the research workflow must honor both parameters or prepared-demo links break.

**Route disposition table:**

| Route / asset | Today | Proposed disposition |
| --- | --- | --- |
| `/` | SPA when `dist/` exists, else legacy index template | SPA explore route. Legacy index stays as fallback until Stage 5 parity, then deleted. |
| `/compare` | SPA when `dist/` exists, else legacy | SPA route; compare-tray persistence and ingredient-name fix are acceptance conditions. |
| `/graph` | SPA when `dist/` exists, else legacy; content is a hardcoded 11-node demo SVG | SPA route backed by `/api/products/{id}/connections` + `/api/ingredients`. If real data is not wired by Stage 3, the route renders an honest empty state and the demo SVG is deleted; no pan/zoom/drag without a stated requirement. |
| `/research` | Always legacy template | **Fold into the SPA as a structured evidence route** (author decision 2026-11-09): interpret → editable filters → results with evidence expanders → quote explorer, composed from the shared search/evidence patterns. `?query=` and `?demo=1` carry-over required. Template retained until parity, then deleted. |
| `/study` | Always legacy template | **Split fold-in** (author decision 2026-11-09): prepared demo becomes copilot starter suggestions; references library + quality checks become a small SPA route; dead "Read a label" tab retired. `?demo=1` carry-over required. Template retained until parity, then deleted. |
| `/progress` | Always legacy template | Fold into SPA as a `/progress` route — preparation jobs are real API features (`/api/research/jobs`, submit/cancel/5s-poll) with no SPA surface today. |
| Legacy index template (`index.html`, 2,922 lines) | Fallback for `/`, `/compare`, `/graph` when `dist/` missing | Keep in-tree as rollback lever through Stage 4; delete the four dead-feature sections and their JS call sites early (they 404 by documented drift, `src/EGM.md` boundary-drift note); delete the file at the defined end state. |
| `/docs` | FastAPI OpenAPI UI | Keep unchanged. It is backend surface, not part of the SPA consolidation. |

**Dead-feature disposition table** (all four post to routes that are not registered — documented 404 drift in `src/EGM.md` and `src/skintellect/api/EGM.md`):

| Dead feature | Calls | Disposition |
| --- | --- | --- |
| Routine Studio | `POST /api/routine/analyze` (unregistered) | Retire from the legacy UI. Do not port. The real logic lives in the `experiments/` read-only track; if it ever becomes a product feature it needs a new concept with a registered backend route. |
| Formula Lab | `POST /api/formula-lab/analyze` (unregistered) | Same as Routine Studio. |
| AI Board & CSI | `GET /api/agents/meta`, `POST /api/agents/board/deliberate`, `POST /api/agents/csi/investigate` (unregistered) | Same. Porting would mean building agent routers for experiments-grade scope the web UI has never had. |
| Label reader | `POST /research/label` (unregistered; `research/labels.py:read_label` exists unwired) | Retire the "Read a label" study tab. If label OCR is wanted in the product, wiring the backend is a separate, prerequisite concept — not part of this UI rebuild. |

### 2. Platform upgrade: radix-vue 1.9.11 + Tailwind 3.4 → reka-ui 2.x + Tailwind v4

The zoom-out lens must be answered head-on, because the do-nothing option is genuinely defensible:

- **Cost ledger (verified):** port semantic tokens from `hsl(var(--…))` to Tailwind v4 CSS-first `@theme`; re-map the `evidence.*` token family (`tailwind.config.js:51-63`); replace `darkMode: ['class']` with the v4 custom-variant; swap `tailwindcss-animate` for `tw-animate-css`; re-pull all 10 primitives via the shadcn-vue CLI — which overwrites the two locally customized primitives (`Badge`/`Button` evidence variants, `ui/badge`, `ui/button`) unless customization is moved out of generated files first; pass `vue-tsc` strict across every generated file; and review dialogs/selects/collapsibles visually, because their `animate-in/out` and `animate-collapsible-*` classes are currently no-ops (`tailwindcss-animate` is installed but never registered, per `frontend/EGM.md` invariants) and will go live for the first time.
- **Benefit ledger:** maintained primitives (reka-ui 2.11 is active; radix-vue 1.9.x is dormant), and — the actual driver — native access to the shadcn-vue AI Elements catalog needed for the copilot rebuild. Nothing else in the concept requires the upgrade.
- **The honest counter-argument:** the one documented primitive defect (dead animate classes) has a one-line fix: register `tailwindcss-animate` in `tailwind.config.js:plugins`. If the team were willing to hand-build the six copilot patterns on the existing radix-vue wrappers, freezing on v3 wins on cost and risk. The zoom-out verdict rule adopted here: the upgrade is justified ONLY as the enabler of upstream AI Elements adoption that REPLACES hand-rolled equivalents; it must land as a standalone, no-feature-diff PR before any copilot work, inside an explicit time-box; if it breaks the gates or blows the box, cut AI Elements scope and freeze.
- **The counter to the counter:** the 1,078-line `ResearchCopilot.vue` hand-rolls exactly what AI Elements provides (todo list, trace debugger, suggestion chips, citation dialog) and shows the local cost of maintaining them. Reuse of upstream-maintained patterns IS the minimization the zoom-out lens asks for. Staying on a dormant dependency is not stability; it is a slow dead-end. On balance the upgrade passes, but only under the isolation and time-box conditions, and the brief must record that "freeze on v3" was a live option, not a strawman.

### 3. Copilot: mapping AI Elements patterns onto the current UI

Hard precondition (Blocker, design + codebase-details + implementation-readiness lenses agree): `POST /api/research/copilot/stream` returns 200 then crashes mid-stream with `ValueError: ContextVar Token was created in a different Context` at `src/skintellect/gemini.py:60` when the sync generator is consumed across async contexts by Starlette. Any streaming UI built before this fix is dead on arrival — and worse, `frontend/src/lib/api.ts:128-129` silently falls back to non-streaming on failure, so the UI looks alive while streaming is broken. The fix must land first, verified by a test that consumes the SSE stream across chunk boundaries, and the client must stop failing silently (see Observability below).

Mapping (each swap replaces, not supplements — no parallel implementations may merge):

| AI Element pattern | Replaces today | Contract that must be preserved |
| --- | --- | --- |
| Message Scroller | Hand-rolled messages container in `ResearchCopilot.vue`; fixes no-auto-scroll-to-newest | SSE event names `node_update` / `final_result`; non-streaming fallback in `api.ts` stays as a safety net, but must be observable |
| Prompt Input | `Input` + Send footer | Enter-to-send / Shift-Enter-newline conventions; disabled state while streaming |
| Suggestion | `getSuggestions()` regex-scraping the model's own markdown for chips | Suggestion content must come from structured backend fields, not client-side markdown scraping |
| Sources + Inline Citation | Citation badge row + hand-rolled Dialog fetching `/api/evidence/{id}` | Evidence lookup endpoint and claim-to-evidence binding stay intact |
| Trace / Plan / Task / Reasoning / Tool | Hand-rolled agent-trace Collapsible debugger + hand-rolled `todo_list` rendered from client-side intent classification | Persona-scoped context (`persona_id`, `product_ids`), session CRUD (`/api/research/copilot/sessions*`); the client-side regex intent classifier is deleted — routing is the backend's job |

Two additional requirements from the codebase-details lens: (a) the v-html markdown trust boundary is documented in `frontend/EGM.md` as "backend content is trusted"; swapping the message renderer must either keep that boundary with the contract updated, or add sanitization (DOMPurify) and flip the invariant — a recorded decision, not a default; (b) `copilot_sessions`/`copilot_messages` grow unboundedly with no retention policy; record a decision (accept for a local tool, or add retention).

### 4. Data-starved screens

- **Compare matrix names (the "0 ingredients" bug, observed in browser):** the matrix computes shared/unique ingredients from `p.names`, but products added from the grid come from the list endpoint, which omits names. The concept must pick one fix: extend the `/api/products` list payload with the fields the matrix needs (small payload cost at limit 36; benefits every consumer), or fetch `/api/products/{id}` on add-to-compare and store full objects in the tray (max 4, so at most 4 extra requests; keeps the list endpoint lean). Implementation-readiness lens: this is a design decision the brief must resolve, not leave to the implementer — recommendation is fetch-detail-on-add, because it also future-proofs the tray against any other detail-only field and touches no shared API contract.
- **Graph:** `IngredientGraph.vue` (258 lines) is entirely a hardcoded 11-node demo; the real `/api/products/{id}/connections` endpoint and the `IngredientGraphData` type in `lib/types.ts` are unused. Wire the route to real data or show an empty state; do not invest in pan/zoom/drag without a requirement.
- **Hero stats:** markup hardcodes 546 / 2,492 / 1,490+ (`App.vue:406-424`) versus `/api/stats` reality of 576 / 2,502. Requirement with general force: no numeric claim in markup that an API provides — this defect class is what hardcoded fallbacks (`analysis?.hydrators || ['Ceramides','Glycerin','Panthenol']`, `match_score || 95` in `ProductDetailModal.vue`) and stale stats share.
- **Pagination:** the backend already supports `page`/`limit`/`sort`/`filters` on `/api/products` (default limit 36 over 2,502 products) — zero backend work. The frontend must put page state in the URL and stop firing a request per keystroke: `App.vue` has 16 refs (0 computed, 2 watch) with 12 filter refs each triggering `loadData()` on every change, no debounce, no cancellation. One debounced query composable with in-flight `AbortController` cancellation is the fix; `@vueuse/core` is already installed (`useUrlSearchParams`, `refDebounced`).

### 5. State architecture

The structural lens identifies `App.vue` (551 lines, 16 refs, 0 computed, 2 watch) as the debt engine: it owns all state for four tabs, hash routing, filters, compare tray, persona, and copilot mounting. Adding vue-router and shadcn-vue on top without decomposition would create a second state layer over the same monolith. Requirement: route-scoped owners with one responsibility each — explore query composable (filters + page + cancellation), compare tray composable, persona composable, copilot session composable — with `App.vue` reduced to layout plus `router-view`. `defineModel` replaces the 11 prop/update pairs in `FilterSidebar.vue` (291 lines).

Persistence and migration were verified in code: the legacy app persists the persona to `localStorage` under `skintellect_active_persona_id` with a legacy `skinsort_active_persona_id` fallback (`src/skintellect/web/static/js/app.js:47,455`); the SPA persists nothing (compare tray is in-memory; reload loses it; persona selection is lost). The SPA composables must read the legacy key as a fallback and write the new key — an explicit migration, not a silent reset — and the compare tray must persist for the same reason. URL becomes state for filters, page, and tab (deep links restore exactly), which also resolves the `/#copilot` → `/copilot` bookmark migration via a router redirect rule.

### 6. First workflow: search → product detail → compare → inspect evidence

The zoom-out lens endorses this as the right first slice — it is the highest-traffic path, it forces the compare-name fix and URL state immediately, and it touches no copilot code (so the stream fix and platform upgrade can proceed independently). It must carry testable acceptance, each item mapping to an observed defect:

1. Desktop and mobile widths; the compare grid (`repeat(n, minmax(280px,1fr))`, no scroll wrapper ≈ 1,120 px minimum) gets horizontal scroll or responsive stacking.
2. Keyboard: modal focus trap, Esc to close, arrow-key tabs via `ui/tabs` (the hand-rolled tab buttons in `ProductDetailModal.vue` bypass these), enter-to-send in Prompt Input.
3. Loading, empty, and error states on every fetch: skeletons (exist in `ProductGrid`), zero-result state, API-down retryable message — and no silent fallback constants rendered as data.
4. Compare matrix shows real ingredient names for every add path (grid card, detail modal, copilot message action, deep link).
5. Evidence citation dialog opens from both the copilot and the detail view; `?query=` deep link into the merged search flow carries over.
6. Filtered + paged list state restores from URL exactly.
7. All gates green per stage: `npm run build` (vue-tsc strict), `python scripts/check.py` (includes the UI semantics check), and — before legacy retirement — a replacement for the semantics check, because `tests/check_ui_semantics.js` exercises the legacy `workspace.js` through a DOM shim and does not touch the SPA at all; retiring legacy pages destroys its subject. The gate must be re-pointed at SPA semantics (or replaced) in the same stage that deletes the legacy code.

## Goals vs. Non-Goals

### In-Scope Goals

- One Vue SPA on vue-router with routes `/`, `/compare`, `/graph`, `/copilot` (+ `/progress` fold-in; `/research` and `/study` per the open dispositions below), with hash-link and query-param migration.
- One-time, isolated, time-boxed platform upgrade: shadcn-vue on reka-ui 2.x + Tailwind v4, with evidence-variant customization extracted from generated files before any CLI re-pull.
- Copilot rebuilt on upstream AI Elements patterns, replacing (not joining) the hand-rolled equivalents; backend contracts (`node_update`/`final_result`, session CRUD, `persona_id`/`product_ids`, `/api/evidence/{id}`) preserved; product actions (view-details, toggle-compare) kept.
- Backend SSE crash fixed and verified first; stream failures made observable; silent fallback downgraded to an explicit, logged degraded mode.
- Data wiring: compare-tray names, `/api/stats` for hero, page-in-URL pagination with debounced/cancelled queries, real graph connections data or honest empty state.
- State decomposition into route-scoped composables; persona + compare-tray persistence with legacy-key migration.
- Staged, per-stage-revertible rollout with the `dist/`-presence switch in `app.py` as the rollback lever; legacy templates retained until parity, then deleted with a date.
- Retire the four dead features from the legacy UI (they 404 today); keep the experiments track where it lives.

### Out-of-Scope Non-Goals

- No porting of Routine Studio, Formula Lab, AI Board/CSI, or the label reader into the SPA, and no new backend routers for them.
- No backend changes beyond the SSE fix and any compare-payload decision — no scoring logic moves into the SPA, no new LLM features.
- No pan/zoom/drag or other speculative graph capabilities without a stated requirement.
- No design-language redesign of the evidence token system — the existing `evidence.*` semantics carry over as-is.
- No unit-test framework rollout in the frontend as part of this concept (recorded as a known, accepted thinness of the safety net, mitigated by gates and staging).
- No mobile-native or offline support; responsive correctness of existing surfaces only.

## Alternatives Weighed

- **Rejected — freeze on radix-vue 1.9.11 + Tailwind 3.4 (do nothing):** the one documented primitive defect (unregistered `tailwindcss-animate`) has a one-line fix, and the installed 10 primitives work. Would win on cost if the copilot were rebuilt by hand; rejected because the copilot rebuild is the core of the concept, upstream AI Elements requires current shadcn-vue, and staying on a dormant dependency accumulates the same drift that produced the current dual-UI mess. Recorded as a live option with its cutoff: if the isolated upgrade PR exceeds the time-box or cannot pass `vue-tsc` strict cleanly, defer it and cut AI Elements scope.
- **Rejected — hand-build copilot patterns on existing primitives:** Message Scroller, Prompt Input, Sources, Inline Citation, and Trace would duplicate upstream-maintained code; `ResearchCopilot.vue` at 1,078 lines is the measured cost of exactly this approach.
- **Rejected — big-bang rebuild in one PR:** mixes the backend fix, platform migration, router introduction, and feature slices; impossible to revert per-cause and unverifiable against `vue-tsc` + semantics gates. Replaced by staged PRs (below).
- **Rejected — keep legacy pages permanently as a parallel UI:** duplication rot is proven, not hypothetical — four dead features survived multiple contract audits as "documented 404 drift" inside the 2,922-line fallback; two design languages; navbar cross-links depend on a hash hack. Retained only as a temporary rollback lever with a deletion date.
- **Rejected — port the four dead features into the SPA:** their routes are unregistered (404 by design); their real logic lives in the read-only `experiments/` track. Porting means building agent/routine/formula/label backends that have never existed in the product surface — YAGNI, and outside this concept's boundary.
- **Rejected — patch in place (keep `App.vue` monolith, add router on top):** would leave 16 refs and hash pseudo-routing as the state core while adding a router layer; two state systems over the same owner is worse than either alone.
- **Rejected — drop SSE and go non-streaming only:** the non-streaming path works today, but progressive rendering is the copilot's core interaction; the crash is localized to `run_budget`'s ContextVar token lifecycle across contexts and the non-streaming fallback already exists as a net, so the fix is strictly better than amputation.
- **Rejected — extend the `/api/products` list payload for compare names (chosen alternative: fetch-detail-on-add):** touching the shared list contract to serve one consumer couples every caller to the matrix's needs; at max 4 tray items, per-add detail fetches are cheap and keep the tray resilient to any future detail-only field. (This is a decision with the rejected alternative recorded; see D4.)

## Key Decisions & Staging for Next Steps

Decisions carried into `/egm-draft`:

- **D1 — Streaming fix is Stage 0 and ships alone.** Fix `gemini.py:run_budget` ContextVar token lifecycle; add a cross-context stream-consumption test; verify no buffering layer sits between the FastAPI generator and the browser (middleware/proxy) for `text/event-stream`. No UI work merges before this.
- **D2 — Platform upgrade is a standalone, no-feature-diff PR with a time-box of one working day** (author decision 2026-11-09). Before any CLI re-pull, extract Badge/Button evidence variants into a customization layer outside generated files; after the swap, do a visual pass on dialogs/selects/collapsibles because animate classes go live for the first time. Cutoff: if it cannot pass `vue-tsc` + semantics gates inside the box, defer and freeze (AI Elements scope cut with it).
- **D3 — Router introduction is a no-visual-change PR:** routes `/`, `/compare`, `/graph`, `/copilot`, `/#…` → path redirects, filter/page/tab state into the URL, debounced cancelled query composable. Feature fixes come after, not with.
- **D4 — Compare names: fetch `/api/products/{id}` on add-to-compare** and store full objects in the tray; list endpoint payload unchanged.
- **D5 — Dispositions fixed per the tables in Analysis §1** (including: `/progress` folds in; `/research` folds into a structured evidence SPA route; `/study` split fold-in — demo→copilot suggestions, references/quality→small SPA route, label tab retired; dead features retired, not ported; legacy templates retained until parity, deleted at end state).
- **D6 — Trust boundary for copilot markdown: add DOMPurify** (author decision 2026-11-09): sanitize model-rendered markdown client-side and flip the documented invariant in `frontend/EGM.md` in the same stage as the renderer swap.
- **D7 — Per-pattern replace-or-delete rule** for every AI Element adoption; no hand-rolled and upstream implementations of the same concern may coexist after any stage.

Staging (each stage = one PR on `ui_components`, gates green, independently revertible; rollback lever for `/`, `/compare`, `/graph` is the `dist/`-presence switch in `app.py`):

1. **Stage 0:** D1 backend SSE fix + stream observability (client reason codes, session-to-run correlation in telemetry).
2. **Stage 1:** D2 platform upgrade (isolated).
3. **Stage 2:** D3 router + URL state (no visual change); delete the four dead-feature sections from the legacy template and their JS call sites in the same stage (they 404; deletion shrinks the fallback surface early).
4. **Stage 3:** data wiring — D4 compare names, `/api/stats` hero, pagination UI, graph real data or empty state; compare-tray + persona persistence with legacy-key migration; state decomposition into composables (D6/D7 not yet started).
5. **Stage 4:** copilot rebuild on AI Elements per the mapping table; trust-boundary decision implemented.
6. **Stage 5:** legacy fold-in/retirement — `/progress` (and `/research`, `/study` per resolved dispositions) move behind SPA routes; semantics-check replacement lands in the same PR as the first template deletion; legacy templates deleted at the defined end state, with the parity checklist (links, query params, localStorage keys) recorded per page.

Resolved by the author (2026-11-09, design review):

1. **`/research` disposition:** fold into the SPA as a structured evidence route (not a redirect into the copilot).
2. **`/study` disposition:** split fold-in — prepared demo becomes copilot starter suggestions; references library + quality checks become a small SPA route; dead label tab retired.
3. **Platform-upgrade time-box (D2):** one working day, then freeze-and-defer.
4. **Trust boundary (D6):** add DOMPurify; flip the documented invariant in `frontend/EGM.md`.
