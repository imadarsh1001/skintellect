# Tasks

Gate commands used throughout: `npm run build` (includes `vue-tsc -b`), `python scripts/check.py`, `node tests/check_ui_semantics.js`, `pytest tests/ui_smoke.py` — smoke test on a **local dev backend with a disposable dev DB**, never the default/real DB. Motion-bearing phases additionally verify **reduced-motion emulation** and the **compositor envelope** (transform/opacity only, no layout shift). Every phase starts with a pre-change baseline under `tests/evidence/<phase>/`; rendered checks at desktop + 390 px; evidence committed to git (size-capped JPEG + notes) so reviewers can diff before/after. Gates are CI-enforced for the static suite once the refinement change's frontend job lands; `ui_smoke.py` stays local-only. Prerequisite: `refine-ui-primitives-and-polish` merged.

## 1. Motion foundation (tokens, keyframes, reduced-motion)

- [ ] 1.1 Add semantic motion vocabulary to `@theme`: duration/easing tokens, keyframes, entry-animation utilities (with `@starting-style`), building on `tw-animate-css`; no component-local raw values. Verify: build green; tokens documented in DESIGN.md draft notes.
- [ ] 1.2 Implement global reduced-motion handling (`prefers-reduced-motion`) that disables decorative animation while keeping state changes instant-correct. Verify: emulated reduced-motion walk shows zero decorative animation and correct instant state changes.
- [ ] 1.3 Group verification: gates + compositor check (no layout-property animation, no CLS from animations) + rendered check desktop + 390 px.
- [ ] 1.4 Derive the **audience & voice brief** from README (Skintellect = explainable formulation intelligence; users: acne-prone/sensitive/ingredient-literate shoppers), the persona feature (skin types, goals, strict exclusions), and the PRODUCT.md/DESIGN.md the refinement change produced; record it in `tests/evidence/audience-brief.md`. Verify: brief names 3–5 concrete user dimensions and a voice guide (evidence-first, calm, zero hype); every later moment/state choice references it; the brief is folded into `frontend/DESIGN.md` during group 7.

## 2. Micro-interaction feedback language

- [ ] 2.1 Define and implement the shared hover/press/focus feedback treatment on the primitive packages (button, toggle-group, card, input, select, checkbox, switch, slider, tabs) using the foundation tokens. Verify: same element class gives identical feedback on different screens; feedback ≤ ~200 ms.
- [ ] 2.2 Verification: consistency walk across all 7 views + gates + reduced-motion check (feedback still instant-correct without animation).

## 3. Dealt moments — deep surfaces (Explore, product detail, Copilot)

- [ ] 3.1 Capture pre-change baselines into `tests/evidence/m3-deep-moments/`; use impeccable `animate`/`delight` direction options and pick one composed moment per surface **grounded in the audience brief** — each candidate must trace to a user need or persona dimension (e.g. Explore → personalized match-score reveal; detail → evidence-span highlight; Copilot → agent deliberation), never agent taste. Verify: one moment per surface chosen, documented with its user-need trace, within identity.
- [ ] 3.2 Implement the three moments. Verify: task-beats-moment check (first task interaction yields immediately); reduced-motion fallback instant; no CLS; rendered walk desktop + 390 px.
- [ ] 3.3 Gates pass; moment-vs-baseline comparison confirms "recognizably the same product".

## 4. Dealt moments — light surfaces (Study, Progress, Compare, Graph)

- [ ] 4.1 Baselines into `tests/evidence/m4-light-moments/`; pick and implement one lighter moment per surface — including **ResearchView** (candidate: quote-explorer evidence reveal) — each traced to the audience brief like group 3. Verify: same checks as 3.2–3.3, scaled to light depth, user-need traces documented.

## 5. Personality-rich async states

- [ ] 5.1 Baselines into `tests/evidence/m5-async-states/`; inventory every empty/loading/error condition across Explore grid + product detail modal, Research (evidence / review insights / alternatives fetches), Copilot, Compare, Study, Progress, Graph — map each to real trigger conditions. Verify: inventory complete — every async condition has an owner state.
- [ ] 5.2 Implement designed states: real product copy per the audience-brief voice guide (evidence-first, calm, explains *why*), shaped loading (skeleton or equivalent), identity-consistent accent. Verify: no blank regions, no generic spinners, copy review against spec `ui-feedback-states` voice rules and the brief.
- [ ] 5.3 Wire recovery actions on every error state to the actual cause (retry, clear filter, alternative route). Verify: each recovery demonstrated working (retry succeeds on backend recovery) without full-app refresh; gates pass.

## 6. Bounded polish pass

- [ ] 6.1 Run impeccable `critique` + `audit` over all touched surfaces; triage: CRITICAL/HIGH → fix here, rest → deferred backlog in the PR description. Verify: triage table with a disposition for every finding.
- [ ] 6.2 Apply CRITICAL/HIGH fixes only; re-verify reduced-motion + compositor envelope for any motion fix. Verify: rendered demonstration per fix; deferred items listed, not applied.

## 7. Token audit and DESIGN.md (last)

- [ ] 7.1 Token audit: every new visual-expression value resolves to a semantic `@theme` token; update `frontend/DESIGN.md` with the motion/accent vocabulary and dealt-moment inventory in the same change. Verify: no raw hex/durations/keyframes in components; DESIGN.md documents every new token.
- [ ] 7.2 Final integration verification: full gate suite, reduced-motion + keyboard walk-through app-wide, before/after evidence retained under `tests/evidence/final/`. Verify: all gates green; spec scenarios demonstrated end-to-end; identity-preservation comparison against baselines clean.

## Workflow follow-up

- Merge phase PRs in order (user merges via GitHub); rebase onto updated `main` if needed.
- After merge: `openspec sync specs`, archive this change via the openspec-archive-change workflow, re-run `openspec doctor`.
- Deferred items from group 6 become candidates for a future change; landing page and dark mode remain separate future changes.
