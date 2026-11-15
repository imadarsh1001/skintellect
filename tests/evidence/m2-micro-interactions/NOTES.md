# Group 2 — shared micro-interaction feedback (implementation + verification)

Date: 2026-11-16 · branch: main @ cdfb162 (post group 1) · change: add-ui-personality-and-motion

## The treatment (task 2.1)

One utility, `feedback`, defined in `frontend/src/assets/index.css` next to the motion tokens: transition-property = color, background-color, border-color, text-decoration-color, fill, stroke, opacity, transform; duration = `var(--duration-feedback)` (150 ms); easing = `var(--ease-move)`. Box-shadow deliberately excluded — the compositor envelope never animates shadows (moulded-key shadows are pre-rendered; the press moves via transform). The global `:focus-visible` tangerine ring stays instant by design (Floor 15/26a) — feedback tier does not apply to focus.

## Per-primitive dispositions

| Primitive | Before | After |
|---|---|---|
| Button | `transition-colors` (sink `active:translate-y-px` snapped — transform untransitioned) | `feedback` — sink now animates at 150 ms |
| Input | `transition-colors` | `feedback` |
| Checkbox (root) | `transition-colors` | `feedback`; indicator's `transition-none` kept (instant check drawing, deliberate) |
| Switch (root + thumb) | `transition-colors` + `transition-transform` | `feedback` on both (single class, covers thumb slide) |
| TabsTrigger | `transition-colors` | `feedback` |
| Toggle/ToggleGroupItem (via `toggleVariants`) | `transition-[color,box-shadow]` (envelope violation — animated box-shadow) + no press dim | `feedback active:opacity-80` — violation removed, press dim consistent with Button/Tabs |
| SelectTrigger | none (hover snapped) | `feedback` |
| Card | none | unchanged — resting surface; per-card hover animations are a Furrow don't |
| Slider | none | unchanged — reka positions the thumb with inline layout styles; transitioning position would violate the envelope |
| DialogContent | `duration-200` raw | `duration-(--duration-state)` (220 ms, state tier) |
| SheetContent | `ease-in-out` + raw `duration-300` closed / `duration-500` open | `ease-(--ease-move)` + both states at `duration-(--duration-state)` — the lingering 500 ms exit is gone; exits leave at the state tier |

## Verification (task 2.2)

- **Consistency walk (8/8 views)**: on every route (`/`, `/explore`, `/compare`, `/graph`, `/copilot`, `/research`, `/study`, `/progress`) the first interactive element computes `transition-duration: 0.15s` + `cubic-bezier(0.4, 0, 0.2, 1)` with the `feedback` class present — identical feedback everywhere, ≤ ~200 ms. No horizontal overflow on any route.
- **Gates**: build exit 0 · `check.py` exit 0 · `check_ui_semantics.js` exit 0 · `ui_smoke.py` exit 0 (5 ok groups, desktop + mobile, live backend).
- **Emission**: `.feedback{...}` + `transition-duration:var(--duration-state)` present in dist CSS; the dialog/sheet token utilities compile (`duration-(--duration-state)`, `ease-(--ease-move)` syntax verified in the bundle).
- **Reduced motion**: the group-1 global kill collapses every `feedback` transition to instant (0.01 ms) — capture `reduced-motion-explore-1440.png` (headless Chromium `--force-prefers-reduced-motion`) shows the grid fully rendered with instant states.
- **Scan hygiene**: evidence notes quote class names; `@source not "../../../tests/evidence"` added next to the existing `.taste-skill` exclusion so evidence markdown can never activate utilities. Note: `enter-rise` still emits pre-consumption (vocabulary utility; Tailwind scan nuance) — consumed by groups 3–5; re-checks in group 6 if it matters.

## Feedback stragglers outside primitive scope (recorded, not fixed here)

Raw `duration-*` in domain components (non-primitive): any remaining `duration-200/300/500` outside `components/ui/` ride their owning groups (5: async states; 6: polish pass). The 15 `animate-spin` loadings are group 5's shaped-loading targets.
