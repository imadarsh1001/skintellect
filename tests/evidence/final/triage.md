# Group 7 — polish pass triage (impeccable critique + audit + detector)

Sources: Assessment A = isolated design-review sub-agent over the five screens (source + rendered at 1440×900); Assessment B = `impeccable detect --json` over the touched files (result: **clean**, re-run after fixes: **clean**). Cap per task 7.1: P0/P1 fixed, P2/P3 deferred.

## Fixed (P1)

| # | Finding | Fix |
|---|---|---|
| 1 | Product card's primary target (title/header) was mouse-only `@click` divs — keyboard/SR users could never open the detail dossier (ProductCard.vue) | Title is now a real `<button>` (36/36 cards), Enter/Space activates; card-level click kept for mouse |
| 2 | Persona goal chips were non-semantic `Badge` divs with `@click` — keyboard-inoperable, invisible as toggles | Goals → `ToggleGroup type="multiple"` (BUTTON, `data-state`, keyboard via roving focus) |
| 3 | Three irreconcilable catalog counts ("576 Enriched Formulations · 2,502 Formulations · 2,492 matching") | Copy reconciled: "576 formulas with full INCI · 2,502 indexed formulations" — pagination's "matching" is now clearly the filtered subset |

## Deferred (P2/P3 — backlog, per the Q4 cap)

1. **P2** Identical-card default state: all 36 cards read "100% Fit / Verified INCI (Full)" under the default persona+sort — fit badge carries no signal (needs a sort/scaling design decision)
2. **P2** Detail-modal badge flood: 16 badges incl. 5 duplicates of the styled chips; "✓ Not Vegan" reads positive
3. **P2** Hardcoded hex score colors (`text-[#12635a] bg-[#e5f5f2]`) bypass evidence tokens
4. **P2** Emoji used as control icons across filters (mixes with lucide)
5. **P2** "just exploring" starter chip submits a literal non-sequitur query
6. **P3** Tech badges ("Deep Agents"/"LangGraph") in copilot header; "111 pts" unexplained; "(Full)" truncation-looking copy; copilot welcome voice
7. **P3** StudyView tabs lack tablist semantics; ProgressView uses raw native selects; top nav has no active-page indicator; pulsing "Cross-Domain Formulation Engine" decorative status

## Dispositions & false positives

- "Selected tab tabindex=-1" — reka's correct roving-focus pattern, not a defect.
- Quick-chip vs sidebar duplication (P1 #3 in the report): real UX critique, but resolving it is a design decision (which control is canonical) — deferred to a design discussion, not a mechanical polish fix.
- `/progress` redirect race observed once mid-stream — source router correct; not reproducible on clean loads.

## Final state

- Detector: clean on all six touched files (re-run post-fix)
- Gates: build ✓, `scripts/check.py` ✓, `tests/check_ui_semantics.js` ✓, `ui_smoke.py` 5/5 ✓
- Live verification: hero copy rendered reconciled; 36/36 title buttons; goals render as BUTTON toggles with correct `data-state` (evidence: `final-p1-fixes-1440.png`)
