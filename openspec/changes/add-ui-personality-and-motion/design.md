# Design

## Context

Companion change `refine-ui-primitives-and-polish` lands first and delivers the primitive substrate (toggle-group, checkbox, switch, slider, sheet + existing ten), EGM contracts, DESIGN.md, and the verification stack. This change adds the personality axis the user asked for ("creative and interesting without AI slop") on top of that substrate. Established system: Vue 3.5 + TS + Vite 6 + Tailwind v4 (`@theme` CSS-first) + reka-ui ^2.11.0 + `tw-animate-css` (already installed, already producing `animate-*` classes). Grilled Round 2 settled: Operate-mode restraint with precise delight (Q1), whole SPA with traffic-proportional depth and no landing page (Q2), motion + states + dealt moments with no new deps (Q3), sequencing after the refinement change (Q4), token changes sanctioned inside this change with DESIGN.md updated in the same change (Q5).

## Goals / Non-Goals

**Goals:**
- A repeatable, reviewed expression system — motion tiers, feedback language, dealt moments, state personalities — not one-off flourishes.
- Anti-slop by construction: meaning-first motion, token discipline, moment caps, identity preservation.
- Full reduced-motion and performance compliance from the first phase, not retrofitted.

**Non-Goals:**
- Landing page, dark mode, new animation dependencies, new fonts, palette/layout identity replacement, backend changes.

## Decisions

1. **Operate-mode restraint (grilled R2-Q1):** data-dense screens stay quiet and scannable; personality enters as precision — micro-interactions, shaped loading, voiced empty/error states, exactly one dealt moment per view. Alternative — a bold visual-world redesign — rejected: that is where slop originates in product apps.
2. **Motion tiers:** interaction feedback ≤ ~200 ms; open/close and view-state transitions ≤ ~300 ms; dealt moments may choreograph longer but only in designated spots. Motion communicates (origin, state, continuity); zero purely decorative motion. All durations/easings live as `@theme` tokens.
3. **No new dependencies (grilled R2-Q3):** Tailwind v4 keyframes + `@starting-style`, `tw-animate-css`, reka-ui transitions cover the needed vocabulary. GSAP explicitly rejected for now.
4. **Tokens change here, documented here (grilled R2-Q5):** new accent/shadow/motion tokens are added to `@theme` in this change and `frontend/DESIGN.md` is updated in the same change with a token-audit task (no raw values in components). This is the sanctioned door the companion change's escalation protocol opened.
5. **Traffic-proportional depth (grilled R2-Q2):** Explore (incl. product detail modal), Copilot get composed moments; Research, Study, Progress, Compare, Graph get lighter ones (Research may be promoted to deep if its quote-explorer moment earns it during group 4). No public landing page in this change.
6. **Reduced motion and performance are phase gates, not afterthoughts:** every motion-bearing phase verifies `prefers-reduced-motion` emulation and the compositor-property envelope (transform/opacity only, no layout shift) before its PR.
7. **Skills remain advisory:** impeccable `animate`/`delight`/`bolder` generate direction options and `craft-floor.md` gates every edit; ui-taste anti-slop craft cross-checks; `design-taste-frontend` is not used here (no landing page). Escalation protocol and bounded-polish cap (CRITICAL/HIGH only) carry over from the companion change unchanged.
8. **Baselines and evidence carry over:** each phase commits pre-change captures under `tests/evidence/<phase>/`; personality is judged against the pre-change baseline so "recognizably the same product" (spec `ui-visual-personality`) is diffable.
9. **Direction is grounded in the product's audience and voice, never agent taste (user requirement, 2026-11-13):** before any moment or state is picked, an audience & voice brief is derived from README (Skintellect = explainable formulation intelligence; users: acne-prone/sensitive/ingredient-literate shoppers), the persona feature (skin types, goals, strict exclusions), and the PRODUCT.md/DESIGN.md the refinement change generated. Every dealt moment and every state copy must trace to a documented user need or persona dimension (e.g. Explore → personalized match-score reveal; detail → evidence-span highlight; Copilot → agent deliberation; empty filtered results → explain-the-exclusion guidance).

## Risks / Trade-offs

- [Motion causes jank or layout shift] → transform/opacity-only envelope, per-phase no-CLS check, `@starting-style` for entry animations.
- [Personality drifts into slop] → one-moment cap per view, meaning-first rule, ui-taste anti-slop cross-check, craft-floor before edits, reviewer walk against baseline.
- [Token sprawl / inconsistent vocabulary] → all expression values through `@theme` semantic tokens; token-audit task before merge; DESIGN.md updated in the same change.
- [Reduced-motion regressions] → emulation check is part of every motion-bearing phase's verification, not a final-pass item.
- [`@starting-style` unsupported in older browsers] → entry animations are enhancement-only; keyframe/transition fallbacks still render every state correctly without it.
- [Skills push beyond scope] → escalation protocol: out-of-scope suggestions go to the deferred-triage table; changing identity needs a new OpenSpec change.

## Migration Plan

1. Start only after `refine-ui-primitives-and-polish` merges to `main`; pull `main` locally (rebase contingency as in the companion change).
2. Land phases in the tasks' order (foundation → micro-interactions → deep moments → light moments → states → polish → docs), each as its own PR referencing this change.
3. Rollback per phase = revert that phase's single PR; the foundation phase is the only one others depend on.

## Open Questions

None blocking. Dark mode is explicitly deferred (non-goal), and "which dealt moment per view" is a per-phase design choice made during that phase, informed by impeccable direction options — it does not change specs or task breakdown.
