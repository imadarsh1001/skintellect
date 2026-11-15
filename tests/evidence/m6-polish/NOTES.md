# Group 6 — bounded polish pass: triage table

Date: 2026-11-16 · branch: main @ ebe4999 (post group 5) · change: add-ui-personality-and-motion
Method: impeccable `detect` (deterministic anti-pattern scan, 101 files, regex engine) + in-context design review against impeccable craft-floor and the audit playbook's five dimensions over every surface touched by groups 1–5. Bounded cap per tasks 6.2: CRITICAL/HIGH fixed here, the rest deferred — not applied.

## Detector result

**Zero anti-pattern findings** across `frontend/src` (`.css/.ts/.vue`; element rules undercount noted — rendered checks were done per group in m1–m5 evidence instead).

## Triage table — every finding has a disposition

| # | Source | Finding | Severity | Disposition |
|---|---|---|---|---|
| 1 | craft-floor motion | `enter-rise-sm` is one shared entry language across many surfaces — reads as uniformity | Nit | **Accepted trade-off**: the animate playbook's endorsed pattern — one material idea ("the ledger writes") carried through quiet supporting states; the per-surface moments (stamp+count, sweep, board convening) are the authored variation. No change. |
| 2 | audit A11y | Count-up text churns for ~450 ms; screen readers traversing mid-count may hear an intermediate value | Minor | **Deferred**: SR traversal typically lands after settle; the reduced-motion path renders the final value instantly. Candidate: aria-hidden the counting span + visually-hidden final value. |
| 3 | audit Performance | Up to 30 concurrent per-card rAF count loops on grid arrival | Minor | **Deferred**: ~26 frames each, text-content updates only; no frame drops observed in rendered checks. Candidate: one shared rAF driver for all counts. |
| 4 | audit Responsive | Fit-chip width jitters ~2 px while the figure counts 0→100 (text width change, not a compositor animation) | Minor | **Deferred**: sub-second, inside a flex row; semantics/SM gates green. Candidate: fixed-min-width tabular span. |
| 5 | audit Theming | New colors introduced by groups 1–5 | Pass | **None**: every value resolves to a semantic token (`--accent`, `--muted/40`, evidence family); detector's zero findings confirms. |
| 6 | craft-floor browser surfaces | Selection, caret, scrollbar, focus ring | Pass | **Already themed** by Furrow (`::selection`, `scrollbar-color`, `:focus-visible` global ring) — pre-existing, verified. |
| 7 | craft-floor copy | Copilot welcome message ("Hey there! … conquer today! 💪") is hype-adjacent vs the voice guide | Minor | **Deferred — out of motion scope**: it is agent chat content (backend-owned greeting), not state copy; a voice pass on agent copy belongs to a future content change. |
| 8 | group-2 note | `enter-rise`/`enter-rise-sm` emit pre-consumption (Tailwind scan nuance) | Nit | **Accepted**: sanctioned vocabulary, consumed by groups 3–4 anyway; evidence dirs excluded via `@source not`. |
| 9 | audit A11y | Skeletons are `aria-hidden` decorative pulses | Pass | **Correct as built. |

## 6.2 outcome

No CRITICAL/HIGH findings — nothing to apply under the bounded cap. No motion fix required re-verification of the reduced-motion/compositor envelope this group (the envelope held in every group's evidence: opacity/transform/color-steps only, no CLS, global kill + matchMedia paths).

Deferred items (#2, #3, #4, #7) are candidates for a future change per the tasks' workflow follow-up.
