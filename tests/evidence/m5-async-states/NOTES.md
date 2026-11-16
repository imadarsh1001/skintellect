# Group 5 — personality-rich async states: inventory, fixes, verification

Date: 2026-11-16 · branch: main @ 6033ca4 (post group 4) · change: add-ui-personality-and-motion
Spec: specs/ui-feedback-states (designed states; real copy; shaped loading; recovery on every error).

## 5.1 Inventory — every async condition and its owner state

### Already designed (Furrow-quality, verified in shipped copy — untouched)

| Surface | Condition | Treatment |
|---|---|---|
| Explore grid | loading | shaped skeleton cards (ProductGrid `v-for i in 6`) |
| Explore grid | fetch error | designed negative banner, names the condition, **Retry wired to reload()** |
| Research results | empty (0 records) | "No records match these constraints. Try relaxing an exclusion or widening the category." |
| Research quotes | empty after filter | "No observations match both filters." |
| Research alternatives | empty | "No formula alternatives matched these constraints." |
| Study references | empty | "No reference notes are indexed yet." |
| Study retrieval | empty | "No retrieval evaluation has been recorded yet." |
| Progress operations | empty | "No operations recorded yet." |
| Compare tray | empty | designed state (scale icon + "No products selected for comparison" + how-to) |
| Graph tray | empty | designed state ("No products selected") |
| Graph connections | per-product error/empty | inline negative row / "No ingredient connections recorded" |
| Copilot streaming | in-flight | `streamingStage` real-work copy pulsing (which stage, not a spinner) |
| Dossier INCI search | empty | "No ingredients matching '{{ q }}'." |
| Dossier actives | empty wells | "No barrier lipids tagged" etc. |
| Landing stats | fetch failure | band leaves the page — never an invented number |
| Copilot send / progress submit | in-flight control | button-level Loader (micro feedback on the control itself — not a state spinner) |
| TaskPlan steps | in-flight step | per-step Loader beside the step name (real work marker) |
| Dossier photo | proxy failed | flask placeholder + name carries meaning (hide-on-error, no substitute glyph) |

### Gaps found and fixed in this group

1. **Study page load** — bare centered `Loader2` spinner → replaced with a shaped skeleton matching the study's eventual card layout (wide block + two tall cards), `aria-hidden`.
2. **Progress page load** — same bare spinner → shaped skeleton (two coverage-card wells + form well), `aria-hidden`.
3. **Progress error** — raw negative text with **no recovery** → Retry button wired to `load()` (the actual failing fetch).
4. **Research error** — raw text, no recovery; three async actions (`runInterpret` / `runSearch` / `runAssistant`) share one error ref → added `lastAction` tracking and a Retry that re-runs the exact failed action.
5. **Dossier modal fetch** — failed **silently** (console.warn only): body kept rendering partial cached data with no indication → added `loadError` state + designed error block ("The full dossier couldn't be loaded." — explains what still works: cached header; what doesn't: safety tabs — and offers Retry wired to `loadDetails()`).
6. **Dossier modal loading** — generic spinner → shaped skeleton matching the dossier sections (description well, cert-chip row, three actives wells).

## Verification

- Gates: build exit 0 · `check.py` exit 0 · semantics exit 0 · `ui_smoke.py` exit 0 (5 ok groups).
- **Recovery demonstrated live**: with the backend stopped, `error-progress-1440.png` (+ `error-study-1440.png`) captures the designed error states with their Retry actions rendering in place, page chrome intact. Study/Explore retries re-use their existing wired `load`/`reload`; Research retry re-runs the exact failed action (`retryLast`).
- No blank regions, no generic state spinners remain on any async surface (remaining Loaders are control-level in-flight markers, inventoried above).
- Copy review: every new string follows the voice guide — names the actual condition, states what still works, offers the next step, no hype, no filler.

## Correction (2026-11-16, EGM re-check round)

The inventory's "every async condition has an owner state" claim was false as originally written: the three ResearchView expansion drawers and the Graph connections panel loaded with bare spinner lines, and their error states had no recovery. Fixed in the re-check round: shaped mini-skeletons + Retry wired to `toggleEvidence`/`toggleReviews`/`toggleAlternatives`/`loadAll` on every nested state; this correction plus the fixes supersedes the inventory's completion claim.
