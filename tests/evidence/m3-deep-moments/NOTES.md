# Group 3 — deep dealt moments: direction, picks, traces (pre-implementation)

Date: 2026-11-16 · branch: main @ eed1020 · change: add-ui-personality-and-motion
Direction source: impeccable `animate` playbook (motion thesis discipline) gated by tests/evidence/audience-brief.md — every pick cites a dimension number from that brief; agent taste is not a trace.

## Baselines (pre-change, committed here)

- `baseline-explore-1440.png` — persona-scored grid, Fit chips + verdict chips per card
- `baseline-detail-modal-1440.png` — dossier modal open (Oligo Hyaluronic Acid 5000 Toner): tabs, certifications, functional-actives wells, fit header (111 pts / 100% Fit)
- `baseline-copilot-1440.png` — copilot session view, welcome message, suggestion chips, composer

## Motion thesis per surface (impeccable: focal moment + continuity + feedback + budget)

Continuity and feedback are already owned by groups 1–2 (portal durations token-wired; `feedback` class on every primitive). The dealt moment is the focal entrance each deep surface has earned; supporting motion stays quiet. Budget: moments play once per data arrival (never on hover/scroll), compositor-only, composed strictly from the group-1 tokens (no raw values), no CLS.

## Picks (one per surface) — each with its user-need trace

### Explore — "the ledger writes the score" (match-score reveal)

- **The moment:** when scored results land (initial render or a persona/filter re-rank), each card's **Fit chip stamps in** (`enter-rise-sm`: opacity + 3px rise at `--duration-state`, `--ease-entry`) and the fit figure inside settles as a count-up in the mono face (tabular numerals already enforced) over `--duration-moment`. Cards themselves enter with `enter-rise-sm` and a capped sibling stagger (~30 ms per index, capped so the full grid completes well under ~800 ms).
- **Trace:** audience-brief dimension 3 (the deterministic-persona user must see the score as computed-from-persona, not stamped-from-nowhere — the count makes the computation legible) + PRODUCT promise 1. The tasks' own example: "Explore → personalized match-score reveal".
- **Bounds:** plays only on scored-data arrival; data text is never deferred by motion (dimension 1 reads through); first filter interaction yields immediately (task-beats-moment). Only the Fit chip and its figure animate — nothing else on the card moves.
- **Reduced motion:** chips and figures render final instantly (global kill), stagger collapses — state correct, zero decorative motion.

### Product detail — "the span proves the claim" (evidence-span highlight)

- **The moment:** when the dossier's attributed review content renders, each **exact supporting text span sweeps once** — background steps from the tangerine-soft well (`--accent`) to transparent at `--duration-state`, staged with a short beat between spans. The span itself is the product's proof-of-claim; the sweep points at it without adding chrome.
- **Trace:** dimensions 1 + 4 (the ingredient auditor and the evidence-demanding researcher both need "claim → its span" to be visible; a claim without its span is not shippable — PRODUCT promise 3). Tasks' example: "detail → evidence-span highlight".
- **Bounds:** color-steps only (sanctioned by DESIGN do's line "transform/opacity color-steps"); once per render, per span; no underline/box/badge added — the sweep is the only addition.
- **Reduced motion:** spans render with no sweep (background starts transparent); the spans' existing static styling carries the attribution legibly.

### Copilot — "the board convenes" (agent deliberation staging)

- **The moment:** as a deliberation answer streams in, each specialist step (Formulator → Safety Critic → Microbiome Analyst → Clinical Judge) arrives with `enter-rise-sm` at `--duration-state`, `--ease-entry` — the arrival rhythm makes the sequence of deliberation legible while it happens; the in-flight agent's state shows real work (group 5 will voice the in-flight copy).
- **Trace:** dimension 4 (deliberation must be *visible*, not summarized — PRODUCT promise 4: the copilot shows reasoning steps and sources). Tasks' example: "Copilot → agent deliberation".
- **Bounds:** per streamed step only; no per-token animation, no looping pulse; content stays at full ink (dimension 1 reads through); composer and session controls never animate.
- **Reduced motion:** steps appear instantly in stream order — the sequence stays legible through order, not motion.

## Rejected direction options (recorded per impeccable discipline)

- Explore: per-card hover lift — rejected (Furrow don't: per-card hover animations; dimension 2 needs an unstartling scan).
- Explore: full-grid fade-and-rise on every filter change — rejected (generic stagger is not a thesis; re-renders on every keystroke in search would be noise).
- Detail: certification badges cascade — rejected (badge decoration without a user need; the span sweep is the promise-keeping moment).
- Copilot: looping "thinking" shimmer on the composer — rejected (pure decoration; dimension 4 wants the reasoning visible, not the waiting dramatized).
- Any moment longer than the token tiers or outside opacity/transform/color-steps — rejected (envelope + identity).

## Checkpoint

Picks presented to the user before implementation (group 3.2) per the agreed review point.

## Implementation record + checkpoint decision (2026-11-16)

Picks were presented to the user; user approved with "go". During implementation, **moment 2 was re-dealt on a data-truth discovery**: the dossier modal renders NO attributed spans (no `span` markup anywhere in the dossier; its Reviews tab renders plain review text). Verbatim quote spans render only in ResearchView/StudyView/Copilot review groups — and tasks 4.1 already candidates the "quote-explorer evidence reveal" for ResearchView. Silently sweeping plain review text would fake the proof moment; adding span rendering to the dossier would be a content change outside a motion change's scope. Re-deal: the span sweep moves to group 4 (ResearchView, its original slot), and the modal's moment became **"the score follows you in"** — header Fit badge + composite points count up with the same ledger language as Explore's cards (one material idea across both surfaces; trace: dimension 3 + promise 1, continuity per impeccable's shared-material discipline). Recorded here as the sanctioned deviation from the presented pick; surfaced to the user in the turn report.

## Implemented (group 3.2)

- `lib/motion.ts`: `motionDurationMs` (parses `--duration-*` vars — handles "450ms"/".45s") + `useCountUp` (rAF, ease-out settle; `prefers-reduced-motion` renders final value instantly — the JS path the CSS kill cannot reach).
- `index.css`: `--duration-stagger` 30ms + `--stagger-cap` 240ms tokens; `stagger-entry` utility (`transition-delay: min(calc(var(--duration-stagger) * var(--stagger-i)), var(--stagger-cap))`).
- Explore: ProductCard Fit chips stamp (`enter-rise-sm`) + figures count up (`--duration-moment`); cards enter via ProductGrid with capped stagger.
- Detail modal: header Fit badge + "pts" figure count up per open (replays on loadDetails), pill block rises.
- Copilot: each message rises on mount (`enter-rise-sm` on the message root — keyed list, only new messages animate); AgentTrace dispatch-matrix rows rise with stagger (the board convening).
- Rejected options and their reasons: see the direction section above.

## Verification (group 3.3)

- Gates: build exit 0 (one TS fix in motion.ts watch callback) · `check.py` exit 0 · semantics exit 0 · `ui_smoke.py` exit 0 (5 ok groups incl. copilot demo tasks on a live backend).
- Moment-vs-baseline: after-captures (`after-explore-1440.png`, `after-detail-modal-1440.png`, `after-copilot-1440.png`) compared against baselines — recognizably the same product; settled states pixel-equivalent; the dossier additionally shows the proxy photo (pre-existing feature, unchanged).
- Task-beats-moment: filter/search interactions are unaffected by arrival motion (entry primitives + stagger ride mount only; `feedback` tier owns interactions) — first interaction yields immediately.
- Reduced motion: `useCountUp` short-circuits to final values via `matchMedia`; CSS kill collapses chip/card/step entries to instant; capture `reduced-motion-explore-390.png` — full render, zero decorative motion.
- Compositor envelope: entries animate opacity/transform only; count-ups are text-content rAF (no layout properties); no CLS observed across entry (skeleton → grid keeps card boxes).
