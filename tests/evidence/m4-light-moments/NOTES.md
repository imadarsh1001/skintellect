# Group 4 — light dealt moments (Study, Progress, Compare, Graph, Research)

Date: 2026-11-16 · branch: main @ b5e82b5 (post group 3) · change: add-ui-personality-and-motion

## Picks — light depth, same material idea ("the ledger writes"), each traced

| Surface | Moment | Trace |
|---|---|---|
| **Research** | **"the span proves the claim"** — the evidence-span sweep re-homed from group 3: synthesis-selection quotes and quote-explorer observation cards sweep once (tangerine-soft well → transparent, `--duration-state`, per-index stagger); observation cards also rise (`enter-rise-sm`) | dims 1+4, PRODUCT promise 3; the tasks' 4.1 candidate ("quote-explorer evidence reveal") — its original, honest home |
| **Study** | prepared evidence cards rise with stagger on render | dim 4 light |
| **Compare** | tray columns rise with stagger when the matrix renders | dim 3 (deterministic side-by-side assembling) |
| **Graph** | per-product evidence panels rise with stagger; edges/paths stay quiet (SVG layout, not compositor material) | dim 1 light |
| **Progress** | coverage cards + job form + active-job cards rise on load; **figures deliberately NOT counted** — progress counters are live-polling values, and a count-up per poll would fight real updates with noise | dim 4 light; restraint documented |

The one material idea carried across all surfaces: the ledger writes — entries arrive, settle, never bounce; nothing loops.

## Implementation

- `index.css`: `@keyframes span-sweep` (accent → transparent, color-steps only) + `@utility span-sweep` (token duration/easing/delay, `both` fill, radius-sm).
- ResearchView: sweep on synthesis-selection quotes + explorer observation quotes; observation cards rise staggered.
- StudyView / CompareMatrix / IngredientGraph / ProgressView: `enter-rise-sm stagger-entry` with per-index `--stagger-i`.

## Verification (scaled to light depth)

- Gates: build exit 0 · `check.py` exit 0 · semantics exit 0 · `ui_smoke.py` exit 0 (5 ok groups — includes the research demo flow, which exercises the sweep-bearing renders).
- After-captures vs baselines (5 pairs in this directory): settled states recognizable/identical; `after-research-1440.png` shows the ask-a-question landing — the sweep renders when an answer's synthesis mounts, which the smoke demo exercises; a visual sweep capture needs a live research query (left to user review).
- Reduced motion: `reduced-motion-research-390.png` (headless `--force-prefers-reduced-motion`) — full render; the sweep's `both` fill resolves instantly to the faded state; entries land without movement.
- No CLS: entries animate opacity/transform on existing layout boxes only.
