# Proposal: add-ui-personality-and-motion

## Why

The companion change `refine-ui-primitives-and-polish` makes the frontend correct, accessible, and non-sloppy (primitives, ARIA, URL-owned state) but deliberately preserves the incumbent identity — by design it will still *feel* like the same app. The user's goal for the frontend goes one axis further: it should feel **creative and interesting without AI slop**. This change adds that axis under the Operate-mode contract (data screens stay quiet and scannable; personality enters as precise, purposeful delight), after the refinement change lands — the primitives it authors are the substrate this motion attaches to.

## What Changes

- **Motion foundation**: semantic motion tokens, keyframes, and animation utilities added to Tailwind v4 `@theme` (building on the already-installed `tw-animate-css`), with `prefers-reduced-motion` support mandatory — **no new dependencies** (no GSAP; CSS keyframes + `@starting-style` + reka-ui transitions only).
- **Purposeful micro-interactions**: consistent hover/press/focus feedback on interactive elements, attached to the newly authored primitives (`button`, `toggle-group`, `card`, etc.) so every screen inherits it.
- **View transitions and "dealt moments"**: one intentional, distinctive moment per major view — depth proportional to traffic: deepest on **Explore, product detail modal, and Copilot**; light touch on Study, Progress, Compare, Graph.
- **Personality-rich async states**: redesigned empty/loading/error states across async surfaces (Explore grid, Copilot, Compare, Study, Progress, Graph) with real copy and visual accent — no placeholder genericity; every error state offers a recovery action.
- **Token changes are sanctioned here**: new accent/shadow/motion tokens in `@theme`, documented in `frontend/DESIGN.md` updated **in this same change** so the written source of truth never drifts.
- Skills stay advisory: impeccable `animate`/`delight`/`bolder`/`craft-floor` generate and gate the direction; ui-taste anti-slop craft cross-checks.

## Capabilities

### New Capabilities
- `ui-motion`: how motion behaves app-wide — motion serves meaning (feedback, state change, spatial continuity), micro-interaction consistency, reduced-motion support, and performance constraints (transform/opacity only, no layout shift).
- `ui-feedback-states`: how empty, loading, and error states present on async surfaces — designed states with personality within the established identity, and recovery actions on errors.
- `ui-visual-personality`: how visual personality expresses without slop — exactly one dealt moment per major view that never disrupts task flow, semantic tokens over raw values, and personality staying within the established identity.

### Modified Capabilities
(none — new capability set; no overlap with the five capabilities introduced by `refine-ui-primitives-and-polish`)

## Impact

- **Code**: `frontend/src/assets`/CSS entry (`@theme` additions), the primitive packages (animation classes), all 7 views and their components; `frontend/DESIGN.md` updated in this change.
- **Dependencies**: none added — Tailwind ^4.3.5, `tw-animate-css`, reka-ui ^2.11.0 already installed.
- **Backend/APIs**: none.
- **Gates**: same stack as the companion change (`npm run build` incl. `vue-tsc -b`, `scripts/check.py`, `tests/check_ui_semantics.js`, `tests/ui_smoke.py` on a dev backend + disposable dev DB), plus reduced-motion and motion-performance checks; per-phase baselines under `tests/evidence/<phase>/`.
- **Ordering**: depends on `refine-ui-primitives-and-polish` being merged first.

## Out of Scope

- **Public landing/marketing page** — that is `design-taste-frontend` territory as its own future change.
- **Dark mode** — deferred; can be its own follow-up change if wanted.
- **New animation dependencies** (GSAP or similar) — rejected for now.
- **Bold visual-world replacement** (new fonts, new palette identity, layout re-architecture) — this change adds personality within the established identity, not a redesign.
- **Backend changes**, **F6 inline citations**, **unit-test framework** — unchanged from the companion change's exclusions.
