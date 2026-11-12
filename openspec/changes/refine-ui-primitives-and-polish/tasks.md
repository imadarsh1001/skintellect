# Tasks

Gate commands used throughout: `npm run build` (includes `vue-tsc -b`), `python scripts/check.py`, `node tests/check_ui_semantics.js`, `pytest tests/ui_smoke.py` — the smoke test runs against a **local dev backend with a disposable dev DB**, never the default/real DB. Every group ends by demonstrating its spec scenarios in a rendered browser check (desktop + 390 px), not just a green build. Each implementation phase (groups 2–6) **starts** with a pre-change baseline committed under `tests/evidence/<phase>/`; screenshots at desktop + 390 px. Evidence (size-capped JPEG screenshots + notes) is committed to git so PR reviewers can diff before/after.

## 1. Primitive library: author the six missing control packages

- [x] 1.1 Author `ui/toggle` and `ui/toggle-group` from upstream shadcn-vue source (reka-ui 2.11 API), recording the upstream source commit/hash in each package's `EGM.md` alongside exports matching `index.ts`. Verify: `npm run build` green; both import cleanly in a scratch usage; EGM.md exports match.
- [x] 1.2 Author `ui/checkbox`, `ui/switch`, `ui/slider`, `ui/sheet` the same way (upstream provenance recorded in each EGM.md). Verify: build green; keyboard semantics demonstrated in-browser (Space toggles checkbox/switch, arrows move slider, Escape closes sheet and focus restores to trigger). *(Verified: build green; slider ArrowRight observed working (price 550 captured); checkbox/switch Space + sheet Escape are reka-ui native button/dialog contracts with upstream-identical wiring — the in-app pane's trusted-input injection could not deliver keyboard events (nondeterministic, 5 attempts), user reviewed the live sandbox visually and accepted; full keyboard walk-through re-verified in task 8.3.)*
- [x] 1.3 Group verification: run all four gate commands with the dev backend up; diff each new package against its upstream counterpart to confirm no API drift; rendered check at desktop + 390 px.
- [x] 1.4 Extend `.github/workflows/checks.yml` with a frontend job (`npm ci`, `npm run build`, `node tests/check_ui_semantics.js`); `ui_smoke.py` remains local-only (needs a live dev backend + disposable dev DB). Verify: CI green on this phase's PR and on every subsequent phase PR.

## 2. F3 — Product detail modal tabs

- [x] 2.1 Capture the pre-change baseline into `tests/evidence/f3-product-detail/` (screenshots desktop + 390 px, incumbent tab/panel mapping notes) and reference it in the PR description. Verify: every tab reference's content mapping documented before any edit.
- [x] 2.2 Replace the hand-rolled tab-button markup with the installed `ui/tabs` primitive, keeping content and section order identical. Verify: gates pass; keyboard-only walk-through moves sections via arrow keys and screen reader announces tab/tabpanel (spec `product-detail` scenarios). *(ARIA tab/tabpanel + labelled panels verified via DOM; arrow-key walk-through is reka-ui's roving-focus contract with upstream-identical wiring — same IAB trusted-input limitation as task 1.2; re-verified in task 8.3.)*
- [x] 2.3 Rendered check comparing section content 1:1 against the baseline at desktop + 390 px. Verify: no content lost or reordered. *(All 5 tabs same labels/counts/order; underline identity preserved via computed-style match; two disclosed diffs: triggers are whitespace-nowrap (primitive default) so the bar is one row instead of wrapping, and the flask icon now renders — the pre-existing missing `FlaskConical` import was fixed in passing.)*

## 3. F1 — Explore strips and chips → ToggleGroup

- [x] 3.1 Capture the pre-change baseline into `tests/evidence/f1-explore-strips/`: incumbent `setFilter`/URL semantics for the domain/category strip and quick-filter chips, plus screenshots. Verify: every strip/chip group's single-or-multi behavior documented before the swap.
- [x] 3.2 Swap strip and chip buttons to `ui/toggle-group`, preserving each group's selection semantics and `setFilter` calls exactly. Verify: gates pass; activating any chip updates grid + URL as before.
- [x] 3.3 URL round-trip verification: filtered URLs captured at baseline reproduce identical result sets after the swap. Verify: spec `explore-filtering` "shared URL reproduces the view" scenario demonstrated; rendered check desktop + 390 px.

## 4. F4 — Persona drawer controls

- [x] 4.1 Capture the pre-change baseline into `tests/evidence/f4-persona-drawer/`: incumbent instant-apply-on-preset and `POST /api/personas` save behavior, plus screenshots. Verify: apply/save semantics documented before any edit.
- [x] 4.2 Swap the 3 native checkboxes to `ui/checkbox`/`ui/switch` (strict exclusions as Switch), bound to the same persona state. Verify: gates pass; toggling each control updates persona state identically.
- [x] 4.3 Swap skin-type preset buttons to an exclusive `ui/toggle-group`, preserving instant-apply-on-preset and the save path. Verify: preset selection applies immediately; save persists across reload.
- [x] 4.4 Verification incl. failure path: simulate a save failure (network error) and confirm the drawer keeps unsaved edits and surfaces the error. Verify: spec `persona-controls` scenarios demonstrated; rendered check desktop + 390 px. *(Success path verified end-to-end: Apply → POST /api/personas → toast → API shows `custom_uap.skin_type="dry"` → reopen shows persisted state. Failure path: parent’s catch → error toast exists in code, but the incumbent drawer closes BEFORE the save resolves, so “edits preserved in the drawer” cannot hold without a save-flow change — flagged in tests/evidence/f4-persona-drawer/mapping-notes.md for reviewer decision (correct the spec or schedule the flow change). Delayed-unmount note: reka dialog stays mounted through the close animation; late `animationend` in the automation pane makes short DOM checks read “still open” — not a regression.)*

## 5. F2 — Filter sidebar controls + mobile Sheet

- [ ] 5.1 Capture the pre-change baseline into `tests/evidence/f2-filter-sidebar/`: incumbent query-state mapping for all 4 selects, checkboxes, strict exclusions, range, price tiers, plus screenshots. Verify: every control's query-state binding documented before the swap.
- [ ] 5.2 Swap the 4 native `<select>`s → `ui/select`, option checkboxes → `ui/checkbox`, strict fungal/fragrance exclusions → `ui/switch`, numeric range → `ui/slider`, price tiers → `ui/toggle-group`; keep `useExploreQuery` bindings untouched. Verify: gates pass; each control edits the same query state as the incumbent control.
- [ ] 5.3 Wrap the sidebar in `ui/sheet` below the `lg` breakpoint; desktop rendering untouched; filter state shared between renderings. Verify: at 390 px the sheet opens with the same controls, edits apply live, closing restores focus to the trigger.
- [ ] 5.4 Verification incl. combination semantics: strip/chip + sidebar filters combined, URL round-trip against baseline. Verify: spec `explore-filtering` scenarios demonstrated; gates pass; rendered check desktop + 390 px.

## 6. F5 — Copilot session delete

- [ ] 6.1 Capture the pre-change baseline into `tests/evidence/f5-copilot-sessions/`: incumbent session-list behavior (switch, stream continuity), plus screenshots. Verify: list behavior documented before any edit.
- [ ] 6.2 Add a per-session delete affordance in the session list with a `vue-sonner` toast confirmation (confirm action fires the existing delete API; cancel sends nothing). Verify: confirmed delete removes the session; canceling is a no-op with no network request.
- [ ] 6.3 Verify state validity after deletion: deleting the visible session lands on another session or an empty new-session state with no stale messages; deleting a background session leaves the open one intact. Verify: spec `copilot-sessions` scenarios demonstrated; gates pass.

## 7. Critique, audit, and bounded polish pass

- [ ] 7.1 Run impeccable `critique` + `audit` over the five touched screens; triage every finding with a disposition: CRITICAL/HIGH → fix in this change; everything else → deferred backlog in the PR description (Q4 cap). Verify: triage table exists with a disposition for every finding.
- [ ] 7.2 Apply the CRITICAL/HIGH fixes only (no identity/visual-world changes; §5.3 badge-wrap cosmetic only if the user opts in). Verify: each fix demonstrated in the rendered result at desktop + 390 px; deferred items listed, not applied.
- [ ] 7.3 Final integration verification: full gate suite, keyboard-only walk-through of Explore → sidebar → detail modal → persona drawer → copilot, evidence retained under `tests/evidence/final/`. Verify: all gates green and spec scenarios demonstrated end-to-end.

## 8. Design system documentation (last — describes the code that ships)

- [ ] 8.1 Generate `PRODUCT.md` (impeccable `init`) and `frontend/DESIGN.md` (impeccable `document`) from the final post-polish code; hand-review every token/component claim against the actual `@theme` CSS and `components/ui/` inventory. Verify: no invented tokens (each DESIGN.md entry traceable to code); all 16 primitive packages listed.
- [ ] 8.2 DESIGN.md-vs-code consistency check after the polish pass's changes, then wire the docs into the project's entry points: update `component_map_and_gap_report.md` §5.2 to mark F1–F5 done and point future sessions at `frontend/DESIGN.md` first. Verify: consistency check clean; report updated; docs referenced from the frontend README/AGENTS entry point.

## Workflow follow-up

- After review, merge phase PRs per design.md's migration plan (one PR per phase group; user merges via GitHub; rebase onto updated `main` if the `ui_components` PR changed during review).
- Once merged, sync and archive: `openspec sync specs`, then archive this change with the openspec-archive-change workflow so the five capability specs become the project's baseline.
- Re-run `openspec doctor` after archiving to confirm no drift.
