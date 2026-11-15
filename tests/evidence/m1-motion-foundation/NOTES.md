# Group 1 baseline — motion foundation (pre-change state)

Date: 2026-11-16 · branch: main @ 111ebf8 · change: add-ui-personality-and-motion (revised, 177f06c)

## What exists before group 1

- `frontend/src/assets/index.css` (291 lines): Furrow color/radius/shadow/font/evidence tokens in `:root` + `@theme inline`; `key-moulded` @utility; **no motion tokens, no `--duration-*`/`--ease-*` names, no `@keyframes` of the project's own**.
- `@import "tw-animate-css"` (line 16) — supplies `animate-in/out`, `fade-in-*`, `slide-in-from-*`, `animate-collapsible-up/down` consumed by primitives and dialogs.
- A blanket `prefers-reduced-motion: reduce` kill already exists (index.css lines 195–203): animation/transition durations forced to 0.01ms — decorative motion instant-off, state changes instant-correct. Group 1 extends (scroll-behavior) rather than replaces it.
- Loading states: `animate-spin` ×15 across surfaces (group 5's shaped-loading targets). `animate-pulse` ×2.

## Raw-motion inventory (grep over frontend/src, pre-change)

| Pattern | Count | Disposition |
|---|---|---|
| `transition-colors` | 28 | kept — color transitions ride the new duration/easing tokens from group 2 |
| `transition-transform` | 6 | kept — compositor-safe |
| `transition-opacity` | 3 | kept — compositor-safe |
| `duration-200` | 3 | to be re-anchored on the `--duration-feedback` token (group 2 touch) |
| `duration-300` / `duration-500` | 1 / 1 | to be re-anchored on `--duration-state` / `--duration-moment` |
| `transition-none` | 1 | kept (deliberate instant path) |
| `animate-spin` | 15 | group 5 replaces with shaped loading; until then unchanged |
| `animate-in` / `animate-out` | 5 / 5 | dialog/sheet/toast enter-exit via tw-animate-css — kept, durations re-anchored group 2+ |
| `animate-collapsible-up/down` | 1 / 1 | reka collapsible — kept |
| `animate-pulse` | 2 | group 5 candidates |

30 files total touch `transition-*`/`animate-*`.

## Reduced-motion pre-check

Blanket kill covers `animation-duration`, `animation-iteration-count`, `transition-duration`. Missing pre-change: `scroll-behavior` (smooth-scroll paths would still animate) — added by group 1.

## Compositor envelope pre-check

No keyframes of the project's own exist, so no layout-property animation ships pre-change. All `transition-*` classes in the inventory animate color/opacity/transform/box-shadow only (box-shadow transitions are NOT compositor-only — the moulded-key press in group 2 must transition `transform` + pre-rendered shadow layers, not animate box-shadow; recorded here as the envelope rule group 2 implements against).

## Rendered pre-state

Group 1 adds no visual change (tokens/utilities are defined but unconsumed until group 2). Rendered verification for this group therefore checks *no regression* at desktop + 390 px (captures in this directory) rather than a visual delta.

## Group 1 verification results (2026-11-16)

- Gates: `npm run build` exit 0 (after `@theme static` fix) · `python scripts/check.py` exit 0 · `node tests/check_ui_semantics.js` exit 0 · `python tests/ui_smoke.py` exit 0 (desktop + mobile check groups, live backend).
- Token emission: all six vars present in `dist/assets/*.css` (`--duration-feedback` .15s / `--duration-state` .22s / `--duration-moment` .45s, three easings). `@theme static` chosen over plain `@theme` because v4 tree-shakes unused theme keys and hand-written CSS in groups 2–5 must resolve them.
- Live probe (IAB, landing): `--duration-feedback` = 150ms, `--ease-entry` = cubic-bezier(0.22,1,0.36,1) resolve on `:root`; a moulded key's computed `transitionDuration` = 0.15s (Tailwind's `transition-colors` default) — unaffected by the new block, confirming no regression.
- Entry utilities compile (`enter-rise`/`enter-rise-sm` parse; not yet in dist — they emit on first consumption in group 2; @starting-style emission gets verified then).
- Compositor envelope: group 1 ships zero bespoke keyframes and zero animated layout properties; box-shadow rule recorded in NOTES for group 2's moulded-key press.
- Reduced-motion: bundle contains the kill rule (`animation-duration:0.01ms !important`, `transition-duration:0.01ms !important`, `scroll-behavior:auto !important` on all selectors); emulated walk (headless Chromium `--force-prefers-reduced-motion`) at 1440 and 390 renders the app fully with live data and instant states — captures `reduced-motion-landing-1440.png`, `reduced-motion-explore-390.png`; no-regression captures `no-regression-landing-1440.png`, `no-regression-explore-390.png`.
