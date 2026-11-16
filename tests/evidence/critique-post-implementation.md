# Post-implementation critique — add-ui-personality-and-motion (full two-assessment run)

Date: 2026-11-16 · main @ 5c0a9ea reviewed live (dev servers) · impeccable critique protocol: Assessment A (design review, isolated) + Assessment B (detector/browser evidence, isolated), synthesized here

## Assessment B — detector over the live routes (verbatim counts, fully-rendered state)

16 findings / 8 routes: cream-palette ×8 (one systemic decision — the Furrow manila ground, sanctioned identity, rejected as a finding), tiny-text ×3 + line-length 127ch + first-viewport-column-overflow on /explore (the theme's density posture, pre-existing waivers), low-contrast placeholders 3.4:1 on the two big textareas (WCAG fail → fixed), nested-cards ×1 on /copilot (existing composition), span-sweep `to` frame raw hex `#0000` (strict token-rule miss → fixed). Bundle probes: focus-ring token ✓, reduced-motion block ✓ (all three properties), `.feedback` tokens ✓, CSS 63 KB fine, **single 590 KB JS chunk** — the lazy-import/splitting candidate, now with a concrete number.

## Assessment A — design review (severity-ordered)

| # | Sev | Finding | Disposition |
|---|---|---|---|
| A1 | HIGH | **Explore card entry never played**: Card root's own `transition-colors` overrode `.enter-rise-sm`'s transition shorthand (cards popped, no rise); `.stagger-entry`'s delay persisted into hover — cards 9+ waited up to 240 ms for hover feedback. Live-verified by the assessor. | **FIXED**: entry + stagger moved to a wrapper div outside the card (`h-full` card inside) — wrapper runs opacity/transform, card's hover transition untouched. Live probe after fix: wrapper prop `opacity, transform`, card delay `0s`. |
| A2 | HIGH | **Score reveal without its trace** — the brief's own slop definition: Fit chips counted up with no reason attached (the contraindicated chip beside them had `:title`, the spotlighted chip didn't); demo persona made every card read "100% Fit", amplifying sameness | **FIXED**: persona-match chips now carry `:title="persona_match.explanation"` — live probe reads "100% compatible with Universal Adult Sensitive & Acne…". |
| A3 | MINOR | Copilot streaming's JS `scrollTo({behavior:'smooth'})` bypassed the reduced-motion CSS kill | **FIXED**: matchMedia gate → instant jump for reduced-motion users. |
| A4 | MINOR | StudyView quotes rendered in `font-serif` — a fourth face Furrow never declares, in a newly-motioned region | **FIXED**: body-face italic, matching ResearchView's spans. |
| A5 | MINOR | AgentTrace dead ternary gave bypassed events tangerine status dots (not a sanctioned fill; accent signaling nothing) | **FIXED**: bypassed → neutral `bg-input`. |
| B1 | MINOR | span-sweep `to` frame contained raw hex `#0000` | **FIXED**: `hsl(var(--accent) / 0)`. |
| B2 | MINOR | Placeholder contrast 3.4:1 on the copilot + research textareas (WCAG AA fail) | **FIXED**: `placeholder:text-foreground/70` (≈6:1 effective) on PromptInput + ResearchView textarea. |
| A6 | NIT | `enter-rise` (450 ms) + `--ease-exit` declared, never consumed by CSS | **Accepted**: declared vocabulary; the moment tier is real for the JS count-up. |
| A7 | NIT | Copilot welcome copy is hype-adjacent | **Documented waiver**: owner-verbatim chat copy (Hallmark F1/F2 record). |
| A8 | NIT | TaskPlan clock rotated 45° on hover — decorative flourish in a motioned surface | **FIXED**: rotation removed (zero decorative motion). |
| B3 | Nit | Single 590 KB JS chunk, no route splitting | **Deferred**: the lazy-import candidate with its first concrete number. |

## What the assessments held (kept honest)

span-sweep called "the best moment in the change — the product's own thesis animated"; rest-state discipline proven (baseline/after pixel-identical); states coverage scored 4/4 (shaped skeletons, explaining-and-recovering errors, voiced empties, degraded-mode observability); vocabulary judged specific to this product, not portable-generic; tangerine contract, mono-with-unit, and the feedback utility verified genuinely applied.

## Scores (Assessment A, before fixes)

Specificity 3 · Identity-consistency 3 · Restraint 3 · States-coverage 4.

## Verification of this round

All gates green after the fixes (build / check.py / semantics / smoke). Live probes: wrapper carries the entry transition (`opacity, transform`), card hover delay `0s`, chip titles render the persona explanation. Detector B2/B1 re-checkable in the next detect run.
