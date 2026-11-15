# Proposal: add-ui-personality-and-motion

## Why

The archived change `refine-ui-primitives-and-polish` (merged 2026-11-13) made the frontend correct, accessible, and non-sloppy (primitives, ARIA, URL-owned state). The sanctioned Furrow re-deal (merged 2026-11-15) then replaced the visual identity: warm manila ground, Red Hat Display/Text/Mono, tangerine fill-with-ink-never-type, moulded keys — the app now looks different while the Operate-mode contract stands (data screens stay quiet and scannable; personality enters as precise, purposeful delight). The user's goal for the frontend goes one axis further: it should feel **creative and interesting without AI slop**. This change adds that axis on the Furrow system — the primitives the refinement change authored are the substrate this motion attaches to.

## What Changes

- **Motion foundation**: semantic motion tokens, keyframes, and animation utilities added to Tailwind v4 `@theme` (building on the already-installed `tw-animate-css`), with `prefers-reduced-motion` support mandatory — **no new dependencies** (no GSAP; CSS keyframes + `@starting-style` + reka-ui transitions only).
- **Purposeful micro-interactions**: consistent hover/press/focus feedback on interactive elements, attached to the primitives the refinement change authored (`button`, `toggle-group`, `card`, etc.) and to Furrow's moulded-key treatment so every screen inherits it.
- **View transitions and "dealt moments"**: one intentional, distinctive moment per major view — depth proportional to traffic: deepest on **Explore (`/explore`), product detail modal, and Copilot**; light touch on Study, Progress, Compare, Graph, Research. The landing home's dealt moment was delivered by the Furrow re-deal and is kept as fixed reference — this change adds no second landing moment.
- **Personality-rich async states**: redesigned empty/loading/error states across async surfaces (Explore grid, Research fetches, Copilot, Compare, Study, Progress, Graph) with real copy and Furrow-consistent accent — no placeholder genericity; every error state offers a recovery action and reconciles with the existing toast system (pre-existing `vue-sonner` wiring, Furrow-light restyled) instead of bypassing it.
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

- **Code**: `frontend/src/assets`/CSS entry (`@theme` additions), the primitive packages (animation classes), all 8 views (incl. the landing home at `/`; catalog lives at `/explore`) and their components; `frontend/DESIGN.md` updated in this change against its Furrow baseline (`974ae98`, including the "% Persona Fit" chips exception).
- **Dependencies**: none added — Tailwind ^4.3.5, `tw-animate-css`, reka-ui ^2.11.0 already installed.
- **Backend/APIs**: none.
- **Gates**: same stack as the companion change (`npm run build` incl. `vue-tsc -b`, `scripts/check.py`, `tests/check_ui_semantics.js`, `tests/ui_smoke.py` on a dev backend + disposable dev DB), plus reduced-motion and motion-performance checks; per-phase baselines under `tests/evidence/<phase>/`.
- **Ordering**: prerequisites satisfied — `refine-ui-primitives-and-polish` is archived (2026-11-13) and the Furrow retheme is merged to `main` (`111ebf8`, 2026-11-15).

## Out of Scope

- **Re-dealing the landing home** — its moment and composition were delivered by the Furrow re-deal; this change keeps them as fixed reference.
- **Dark mode** — deferred; can be its own follow-up change if wanted.
- **New animation dependencies** (GSAP or similar) — rejected for now.
- **Further identity replacement** (new fonts, palette or layout changes beyond Furrow tokens) — the Furrow re-deal owns the current identity; this change adds personality within it, not another redesign.
- **Backend changes**, **F6 inline citations**, **unit-test framework** — unchanged from the companion change's exclusions.
