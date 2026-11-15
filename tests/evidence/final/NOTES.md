# Final integration verification — add-ui-personality-and-motion

Date: 2026-11-16 · branch: main @ c23f004 + group 7 · change: all 7 groups executed

## Gate suite (all green, on the final code)

- `cd frontend && npm run build` (vue-tsc -b + vite build) — exit 0
- repo-root `python scripts/check.py` — exit 0 (offline checks incl. proxy unit tests)
- `node tests/check_ui_semantics.js` — exit 0 (26/26 semantic pairs, incl. the focus-ring assertions, Floor 15/26a)
- `python tests/ui_smoke.py` — exit 0 (5 ok groups: desktop + mobile, live backend, research demo flow)

## 7.1 Token audit result

- Zero raw `duration-*` values in components/views/lib after re-anchoring the last two stragglers (TaskPlan + AgentTrace chevron rotates → `--duration-state`).
- Zero raw hex, zero component-local `@keyframes`, zero raw easings outside `frontend/src/assets/index.css` — the single motion/color source.
- Every new value resolves to a semantic token; impeccable `detect` zero findings corroborates.
- `frontend/DESIGN.md` finalized: motion vocabulary + dealt-moment inventory (one material idea, "the ledger writes") replacing the draft notes.

## Spec scenarios → evidence (end-to-end)

| Scenario (spec) | Evidence |
|---|---|
| ui-motion: feedback consistent ≤ ~200 ms | m2 walk: identical 0.15 s + move-bezier computed on 8/8 routes |
| ui-motion: reduced-motion support, state instant-correct | global kill + scroll-behavior (bundle-verified); count-ups short-circuit via matchMedia; app-wide forced-reduced-motion captures for all 8 routes in THIS directory (`reduced-motion-*.png`) — every page fully rendered, zero decorative motion |
| ui-motion: compositor envelope (no layout shift) | no layout-property animation ships (grep-verified); entries animate opacity/transform only; count-ups are rAF text content |
| ui-feedback-states: designed empty/loading/error everywhere | m5 inventory: 18 pre-existing designed states verified, 6 gaps fixed; shaped skeletons (Study/Progress/dossier); recovery wired on every error path |
| ui-feedback-states: recovery demonstrated | backend stopped live → error states render with Retry actions (`error-progress-1440.png`, `error-study-1440.png`); retries wired to the actual failing fetches |
| ui-visual-personality: one dealt moment per view, within identity | m3 (deep) + m4 (light) direction records with user-need traces; baseline/after pairs pixel-equivalent at settled state |
| ui-visual-personality: semantic tokens over raw values | 7.1 audit clean |
| Identity preservation ("recognizably the same product") | after-captures vs baselines across m1–m4: settled layout, copy, verdict family, and Furrow identity unchanged; motion only adds arrival language |

## Keyboard walk-through

Real Tab keypresses traverse Explore sensibly (nav → tab strip → filter groups → interactive controls), no traps. The shipped `:focus-visible` tangerine-ring rule is present in the bundle and asserted by the semantics gate. Limitation recorded honestly: the automation pipeline cannot hold focus state across tool round-trips (each probe ran after the focus had moved on), so the ring's live visual appearance during traversal is asserted by the gate + rule presence, not captured as a screenshot.

## Deferred backlog (candidates for a future change)

From m6 triage: count-up screen-reader handling; shared rAF driver for parallel count-ups; Fit-chip width jitter during count; agent greeting voice pass (future content change). Plus standing: F6 inline citations (backend-blocked), unit tests (non-goal), lazy-import code splitting (conversation-only).
