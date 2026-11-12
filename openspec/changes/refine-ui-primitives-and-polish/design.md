# Design

## Context

The SPA frontend (`frontend/`, Vue 3.5 + TS 5.7 + Vite 6 + Tailwind v4) already carries ten shadcn-vue-style primitive packages over reka-ui ^2.11.0 in `frontend/src/components/ui/` (`badge`, `button`, `card`, `collapsible`, `dialog`, `input`, `scroll-area`, `select`, `separator`, `tabs`), each an EGM-contracted Peanut. Explore query state is URL-owned via `frontend/src/composables/useExploreQuery.ts` (300 ms debounce, AbortController); persona state via `usePersona.ts`. The four screens in scope and their hand-rolled controls are documented in `component_map_and_gap_report.md` §5.2 (F1–F5). `vue-sonner` ^2.0.9 is installed and already used by `App.vue`, `ResearchCopilot.vue`, and `ProgressView.vue`. Work builds on the pending `ui_components` PR to `main`; it starts only after that PR merges (see `openspec/config.yaml` context).

## Goals / Non-Goals

**Goals:**
- Close the F1–F5 queue with primitives, not more hand-rolled markup, so keyboard/ARIA semantics are inherited rather than re-implemented.
- Preserve incumbent behavior byte-for-byte at the contract level: URL semantics, selection semantics, instant-apply-on-preset, `POST /api/personas` save.
- Produce a written design source of truth (`PRODUCT.md`, `frontend/DESIGN.md`) so future sessions stop re-deriving tokens and conventions from code.
- Verify behavior at runtime (keyboard walk-through, rendered result at desktop + 390 px), not only via build gates.

**Non-Goals:**
- Any visual redesign, new visual identity, or token changes (refinement preserves).
- F6 inline citations (backend-blocked), unit-test framework (declared non-goal), session-composable extraction (deferred), `vue-flow` (deferred).

## Decisions

1. **Author the six primitives by hand from upstream shadcn-vue source, not via the shadcn CLI.** The CLI crashes on Node 26, and this matches how the existing ten packages were delivered. Source: upstream `shadcn-vue` component source pinned to the reka-ui 2.11 API; the upstream commit/tag each package was copied from is recorded in its `EGM.md` so provenance stays verifiable later. Alternative considered — pinning an older Node just for the CLI — rejected as environment churn for six one-time copies.
2. **Refinement stance pinned by impeccable's Operate mode.** Read each pristine component's behavior before touching it; `reference/craft-floor.md` is read immediately before any UI edit; the incumbent look is preserved. ui-taste/`ui-ux-pro-max` serve only as secondary audit lenses and targeted queries. **Escalation protocol (grilled Q1):** design skills are advisory — any suggestion that touches Tailwind config, tokens, copy, layout identity, or components outside the five in-scope screens is recorded in the phase PR's deferred-triage table and never applied silently; changing any of those requires a new OpenSpec change with its own review. Alternative — treating this as a redesign with a new visual direction — rejected; it would invalidate the just-shipped PR.
3. **Migration order follows primitive dependencies, smallest risk first:** F3 (`tabs` already installed) → F1 (needs `toggle-group`) → F4 (needs `checkbox`/`switch`/`toggle-group`) → F2 (needs all five new primitives, largest surface) → F5 (standalone). Each pass lands on its own feature branch off `main` as a small PR the user merges via GitHub.
4. **F5 confirmation uses `vue-sonner`'s toast action** — the library is already installed and used in `ResearchCopilot.vue`; no new dependency. Delete affordance stays inline (or a `ui/dropdown-menu`-style entry) inside the existing session list; no composable extraction.
5. **Docs land last, describing the code that ships (grilled Q5):** `PRODUCT.md` (durable product context) and `frontend/DESIGN.md` (tokens, component inventory, conventions) are generated with impeccable `init`/`document` **after the polish pass**, from the final merged code, then hand-reviewed with a DESIGN.md-vs-code consistency check — they become the first thing future UI sessions read. (Originally docs preceded polish; that ordering let polish fixes silently invalidate them.)
6. **Verification stack per pass:** `npm run build` (already includes `vue-tsc -b`) + `scripts/check.py` + `tests/check_ui_semantics.js` + `tests/ui_smoke.py` — the smoke test runs against a **local dev backend with a disposable dev DB, never the default/real DB** (grilled Q3) — plus a rendered-result check in a real browser (desktop + 390 px) exercising the spec scenarios, including a keyboard-only walk-through. Every phase PR **starts** by committing a pre-change baseline (screenshots + incumbent-behavior notes) under `tests/evidence/<phase>/` (grilled Q2/Q6), so "semantics unchanged" is a diffable artifact, not a claim; evidence is committed to git (size-capped JPEG + notes) with the phase PR so reviewers can diff before/after (grilled R3-Q4). A pass is done when the spec scenarios are demonstrated, not when the build is green.
7. **Bounded polish pass (grilled Q4):** the final polish pass fixes only CRITICAL and HIGH findings from impeccable `critique`/`audit`, plus the §5.3 badge-wrap cosmetic if the user opts in; every other finding goes to the deferred backlog, not this change. "Polish" must not re-open screens beyond the five in scope.
8. **CI enforces the static gates (grilled R3-Q2):** `.github/workflows/checks.yml` currently runs only `scripts/check.py`; this change adds a frontend job running `npm run build` and `node tests/check_ui_semantics.js` per PR. `ui_smoke.py` stays local-only by design — it requires a live dev backend with a disposable dev DB, which CI does not host.

## Risks / Trade-offs

- [Hand-authored primitives drift from the reka-ui 2.11 API] → Copy from upstream source for the installed version; keep reka-ui usage identical to the upstream file; diff each package against its upstream counterpart during review.
- [URL/selection semantics regress in F1/F2] → Before each swap, capture the incumbent behavior (map `setFilter` calls and URL keys); `tests/check_ui_semantics.js` + `ui_smoke.py` assert the preserved semantics; spec scenarios pin "same result set for the same URL".
- [Sheet changes mobile UX] → The Sheet wraps the *existing* sidebar content only; desktop rendering is untouched; smoke test asserts filter state is shared between the two renderings.
- [Docs drift immediately after merge] → `DESIGN.md` generation happens after the bounded polish pass, on the final shipped code (decision 5), and `openspec` sync keeps specs authoritative.
- [Keyboard-a11y claims without evidence] → Runtime keyboard walk-through is an explicit task per pass with the browser open; findings are fixed before the pass's PR.

## Migration Plan

1. After the `ui_components` PR merges to `main`, pull `main` locally; if the PR changed during review, rebase the phase branches onto the updated `main` before starting (grilled Q6a).
2. Land phases in decision 3's order, each as `feat(ui): …` PRs referencing this change.
3. Run the bounded polish/critique/audit pass on final code; fix findings per decision 7.
4. Generate/review `PRODUCT.md` + `frontend/DESIGN.md` after the polish pass, on the final code (decision 5).
5. Rollback per phase = revert that phase's single PR; phases are independent by design.

## Open Questions

None blocking. Toast choice (decision 4), primitive sourcing (decision 1), and phase order (decision 3) were the only candidates, and all are resolved.
