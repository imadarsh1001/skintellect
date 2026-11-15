# Tasks

Gate commands used throughout: `cd frontend && npm run build` (includes `vue-tsc -b`), repo-root `python scripts/check.py`, `node tests/check_ui_semantics.js`, `python tests/ui_smoke.py` (runs standalone; the venv has no pytest) — smoke test on a **local dev backend with a disposable dev DB**, never the default/real DB. Motion-bearing phases additionally verify **reduced-motion emulation** and the **compositor envelope** (transform/opacity only, no layout shift). Every phase starts with a pre-change baseline under `tests/evidence/<phase>/`; rendered checks at desktop + 390 px; evidence committed to git (size-capped JPEG + notes) so reviewers can diff before/after. The static suite is CI-enforced (`.github/workflows/checks.yml`); `ui_smoke.py` stays local-only. Prerequisite satisfied: `refine-ui-primitives-and-polish` archived 2026-11-13 and the Furrow retheme merged to `main` (`111ebf8`).

## 1. Motion foundation (tokens, keyframes, reduced-motion)

- [x] 1.1 Add semantic motion vocabulary to `@theme`: duration/easing tokens, keyframes, entry-animation utilities (with `@starting-style`), building on `tw-animate-css`; no component-local raw values. Verify: build green; tokens documented in DESIGN.md draft notes. *(Done 2026-11-16: `@theme static` block — 3 duration tiers, 3 easings, no overshoot; `enter-rise`/`enter-rise-sm` @starting-style utilities; no bespoke keyframes — tw-animate-css covers enter/exit, keyframes get added per dealt moment in groups 3–4. Tokens probed live in the page: `--duration-feedback`=150ms, `--ease-entry` resolves.)*
- [x] 1.2 Implement global reduced-motion handling (`prefers-reduced-motion`) that disables decorative animation while keeping state changes instant-correct. Verify: emulated reduced-motion walk shows zero decorative animation and correct instant state changes. *(Done: Furrow's blanket kill retained, extended with `scroll-behavior: auto`; emulated walk via headless Chromium `--force-prefers-reduced-motion` at 1440 + 390 — full render, instant states; captures in tests/evidence/m1-motion-foundation/.)*
- [x] 1.3 Group verification: gates + compositor check (no layout-property animation, no CLS from animations) + rendered check desktop + 390 px. *(Done: build/check.py/semantics/ui_smoke all green; no bespoke keyframes ship, so no layout-property animation exists; rendered captures desktop + 390 clean.)*
- [x] 1.4 Derive the **audience & voice brief** from README (Skintellect = explainable formulation intelligence; users: acne-prone/sensitive/ingredient-literate shoppers), the persona feature (skin types, goals, strict exclusions), and the Furrow PRODUCT.md/DESIGN.md (DESIGN.md at `974ae98`, including the "% Persona Fit" chips exception); record it in `tests/evidence/audience-brief.md`. *(Done: 5 user dimensions + voice guide + per-group gating recorded.)* Verify: brief names 3–5 concrete user dimensions and a voice guide (evidence-first, calm, zero hype); every later moment/state choice references it; the brief is folded into `frontend/DESIGN.md` during group 7.

## 2. Micro-interaction feedback language

- [x] 2.1 Define and implement the shared hover/press/focus feedback treatment on the primitive packages (button, toggle-group, card, input, select, checkbox, switch, slider, tabs) using the foundation tokens. Verify: same element class gives identical feedback on different screens; feedback ≤ ~200 ms. *(Done 2026-11-16: `feedback` utility — color/opacity/transform at `--duration-feedback`/`--ease-move`; applied to Button/Input/Checkbox/Switch/TabsTrigger/Toggle-via-toggleVariants/SelectTrigger + dialog/sheet portal durations token-anchored; box-shadow animated by the old toggle cva removed (envelope violation); Card/Slider deliberately unchanged — resting surface / layout-positioned thumb; Button's snapping press sink now animates.)*
- [x] 2.2 Verification: consistency walk across all 8 views (landing home `/` included; catalog at `/explore`) + gates + reduced-motion check (feedback still instant-correct without animation). *(Done: 8/8 routes compute identical 0.15s + move-bezier feedback with `feedback` present, zero overflow; all four gates green; reduced-motion capture in tests/evidence/m2-micro-interactions/.)*

## 3. Dealt moments — deep surfaces (Explore, product detail, Copilot)

- [x] 3.1 Capture pre-change baselines into `tests/evidence/m3-deep-moments/`; use impeccable `animate`/`delight` direction options and pick one composed moment per surface **grounded in the audience brief** — each candidate must trace to a user need or persona dimension (e.g. Explore → personalized match-score reveal; detail → evidence-span highlight; Copilot → agent deliberation), never agent taste. Verify: one moment per surface chosen, documented with its user-need trace, within the Furrow identity. *(Done 2026-11-16: picks presented to the user and approved; moment 2 re-dealt on a data-truth discovery — the dossier renders no attributed spans, so the span sweep moved to group 4's ResearchView (tasks 4.1's own candidate) and the modal received "the score follows you in" (same ledger material as Explore). Full record + rejected options in tests/evidence/m3-deep-moments/NOTES.md.)*
- [x] 3.2 Implement the three moments. Verify: task-beats-moment check (first task interaction yields immediately); reduced-motion fallback instant; no CLS; rendered walk desktop + 390 px. *(Done: lib/motion.ts composable; stagger tokens + utility; Explore chip stamp + count-up, modal header continuity count, copilot message/agent-row arrivals. Interactions unaffected; count-up short-circuits under reduced motion via matchMedia.)*
- [x] 3.3 Gates pass; moment-vs-baseline comparison confirms "recognizably the same product". *(Done: all four gates green; after-captures vs baselines in tests/evidence/m3-deep-moments/ — settled states pixel-equivalent; reduced-motion capture at 390.)*

## 4. Dealt moments — light surfaces (Study, Progress, Compare, Graph)

- [x] 4.1 Baselines into `tests/evidence/m4-light-moments/`; pick and implement one lighter moment per surface — including **ResearchView** (candidate: quote-explorer evidence reveal) — each traced to the audience brief like group 3. Verify: same checks as 3.2–3.3, scaled to light depth, user-need traces documented. *(Done 2026-11-16: the re-homed span sweep landed on ResearchView's synthesis selections + explorer observations; Study/Compare/Graph/Progress cards rise with capped stagger; Progress figures deliberately not counted (live-polling values — restraint documented). Gates green; 5 baseline/after pairs + reduced-motion capture in tests/evidence/m4-light-moments/.)*

## 5. Personality-rich async states

- [ ] 5.1 Baselines into `tests/evidence/m5-async-states/`; inventory every empty/loading/error condition across Explore grid + product detail modal, Research (evidence / review insights / alternatives fetches), Copilot, Compare, Study, Progress, Graph — map each to real trigger conditions. Verify: inventory complete — every async condition has an owner state.
- [ ] 5.2 Implement designed states: real product copy per the audience-brief voice guide (evidence-first, calm, explains *why*), shaped loading (skeleton or equivalent), Furrow-consistent accent. Verify: no blank regions, no generic spinners, copy review against spec `ui-feedback-states` voice rules and the brief.
- [ ] 5.3 Wire recovery actions on every error state to the actual cause (retry, clear filter, alternative route). Verify: each recovery demonstrated working (retry succeeds on backend recovery) without full-app refresh; gates pass.

## 6. Bounded polish pass

- [ ] 6.1 Run impeccable `critique` + `audit` over all touched surfaces; triage: CRITICAL/HIGH → fix here, rest → a deferred-backlog note committed under `tests/evidence/<phase>/` (trunk workflow: no PRs). Verify: triage table with a disposition for every finding.
- [ ] 6.2 Apply CRITICAL/HIGH fixes only; re-verify reduced-motion + compositor envelope for any motion fix. Verify: rendered demonstration per fix; deferred items listed, not applied.

## 7. Token audit and DESIGN.md (last)

- [ ] 7.1 Token audit: every new visual-expression value resolves to a semantic `@theme` token; update `frontend/DESIGN.md` with the motion/accent vocabulary and dealt-moment inventory in the same change. Verify: no raw hex/durations/keyframes in components; DESIGN.md documents every new token.
- [ ] 7.2 Final integration verification: full gate suite, reduced-motion + keyboard walk-through app-wide, before/after evidence retained under `tests/evidence/final/`. Verify: all gates green; spec scenarios demonstrated end-to-end; identity-preservation comparison against baselines clean.

## Workflow follow-up

- Phases land on `main` in tasks order as conventional commits (trunk workflow — no PRs); pull/rebase only if `main` moves underneath.
- After completion: `openspec sync specs`, archive this change via the openspec-archive-change workflow, re-run `openspec doctor`.
- Revision verification (recorded here so the sweep stays reproducible): grep the change directory for stale-workflow/identity terms — `phase PR`, `PR description`, landing-as-future-work phrasing, `7 views` — with zero hits; residual mentions of `refine-ui-primitives-and-polish` must refer only to the archived prerequisite.
- Deferred items from group 6 become candidates for a future change; dark mode remains a separate future change (the landing home already exists, delivered by the Furrow re-deal).
