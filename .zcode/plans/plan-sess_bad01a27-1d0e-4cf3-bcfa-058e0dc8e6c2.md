# Skintellect Full Visual Retheme — Hallmark-Dealt, Content-Preserving, Branch-Isolated

## Context

You asked for a complete visual retheme using the installed UI skills, hard constraint: **every route, link, form, field, handler, and piece of content survives; only the design system and composition change.** Per your decisions: full retheme sanctioned (supersedes the `openspec/config.yaml` refinement-preservation bullets), **5 evidence-verdict color meanings preserved** (hues re-deal), `add-ui-personality-and-motion` **parked** for post-retheme re-planning, scoring uses **both** `npx designlang` (extraction/WCAG) and hallmark `sloplint.mjs` (the real slop grader), kept-ledger built manually and upgraded into a re-runnable check.

Your four additions, incorporated:
1. **design-taste-frontend** ✓ (in VERIFY) — `gate.mjs` checker + copy-lint at 1440/390/320, **verification-only** per your original constraint (no kit/palette/fictional-contact adoption).
2. **Work on a new branch** — `redesign/hallmark-retheme` off `main`. CI runs on all pushes (`on: push` unfiltered in checks.yml), so the branch is CI-gated identically to main. Merged to main only after you review before/after; branch deleted after merge (per docs/workflow.md).
3. **EGM reviewers + tests** — new REVIEW phase (egm-design, egm-zoom-out, egm-codebase-details over the branch diff) + a **new repeatable check** `tests/check_ui_ledger.js` (local-only, like ui_smoke.py) comparing live DOM counts per route against the baseline ledger.
4. **Component reuse mandate** — composition changes reuse the 16 existing shadcn-vue/reka-ui primitive packages + Tailwind utilities + cva variants; **zero hand-rolled components**; missing primitive → port from upstream shadcn-vue source (established convention); custom CSS already covered by utilities gets removed with a file-level plan shown first.

**SETUP findings (already gathered; approving this plan = the "OK" your sequence requires):**
- Tailwind **v4**, tokens in `frontend/src/assets/index.css` (`@theme inline` + `:root`/`.dark`: 19 semantic colors + radius + 10-token evidence family); `frontend/components.json` → css path is that file; npm; no v3 `tailwind.config.js`.
- 7 routes: `/`, `/compare`, `/graph`, `/copilot`, `/research`, `/study`, `/progress` (+ catch-all redirect). 70 .vue files; 16 primitive packages under `frontend/src/components/ui/` (reka-ui ^2.11.0).
- Hardcoded colors: 15 occurrences in `ProductCard.vue` (×12, `getMatchScoreColor()`) + `ExploreView.vue` (×3) + `App.vue` `emerald-600` gradient. Emoji-as-control-icons in 5 files (FilterSidebar ×30, ExploreView ×14, ProductDetailModal ×10, ResearchCopilot ×4, App.vue ×1).
- Skills confirmed installed: hallmark v2.0.0, frontend-design (playbook w/ AI-tell clusters), design-taste-frontend 2.5.1, web-design-guidelines, impeccable v4.8.2; `npx designlang` npm tool. (`ui-taste` is NOT installed — memory corrected; not needed.)
- `.redesign/` doesn't exist yet; git tree clean (re-verified at execution start; if dirty, I stop and ask you to commit/stash — never do it myself).

## Phase sequence

### 0. SETUP — branch, sanction commits, dev servers
1. Create branch `redesign/hallmark-retheme` off `main`.
2. Docs commit on the branch: `openspec/config.yaml` — replace the two refinement-preservation bullets with the sanctioned retheme mandate ("full visual retheme authorized 2026-11-14; verdict MEANINGS preserved, hues re-dealt; token replacement limited to `frontend/src/assets/index.css`") + note `add-ui-personality-and-motion` is PARKED. Diff shown, nothing silently removed (deletion-safety rule). Memory updated (park status + ui-taste correction).
3. Verify clean tree. Start dev servers in background: Vite :5173 **and** uvicorn :8000 (`PYTHONPATH=src`, disposable dev DB per config rule) — pages fetch `/api` for real data in screenshots.

### 1. BASELINE (skills: designlang, hallmark sloplint, browser-use)
1. Screenshots: 7 routes × **1440 + 390** → `.redesign/before/` (viewport shots, not fullPage — fixed-element stitching bug). Extra states if capture allows: detail modal open, persona drawer open.
2. `npx designlang http://localhost:5173 --wait 3000` → `.redesign/before/designlang/`.
3. Slop-score baseline: `node <hallmark>/scripts/sloplint.mjs frontend/src --genre app --scope app --render --before --url http://localhost:5173/` → `.hallmark/before.json`.
4. **Ledger baseline:** per-route DOM inventory via browser-use — count `a[href]` links, form fields (`input/select/textarea`), interactive handlers (`button`, toggles, switches, tabs, sliders) → `.redesign/before/ledger.json`.
5. **Write `tests/check_ui_ledger.js`** (new file; Node 26 type-stripping pattern like check_ui_semantics.js; local-only — needs live servers, so NOT added to CI, same policy as ui_smoke.py).
6. Commit baselines on the branch.

### 2. REDESIGN (skills: **hallmark redesign** FULL depth + **frontend-design** calibration)
1. Load hallmark `references/redesign.md`; run FULL depth.
2. Deal: `node <hallmark>/scripts/theme.mjs deal --genre app --prompt "Skintellect — evidence-first skincare formulation intelligence; calm, precise, operable"` → 3 themes; pick one; record Picks block (Shape/Theme/Chrome/Hero/Signature/Sections/Material/Sweep); log via `theme.mjs log`.
3. Calibrate Picks against **frontend-design**'s AI-tell clusters + your six (cream+terracotta serif #D97757, acid-green-on-black, SaaS-card kit, ALL-CAPS eyebrows, per-card hover animations, purple-to-blue gradients) — revise anything median before building; mirror test; log revisions. No extra stop (review is at PROVE IT).

### 3. IMPLEMENTATION (hallmark redesign rules govern)
- **One token file only:** `frontend/src/assets/index.css` — new `:root`/`.dark` values, `@theme inline` mapping, evidence hues re-dealt (meanings kept), radius/typography/shadow tokens. **Never** `tokens.css`/`base.css` — hallmark's `theme.mjs scaffold` emits exactly those; port into index.css, discard the files.
- Composition per hallmark rules: heroes, card systems, chrome (`App.vue` navbar), section layouts — routes, wiring, copy untouched.
- **Reuse mandate:** semantic classes (`bg-primary`, `text-muted-foreground`), existing primitives, cva variants; no raw values; no new hand-rolled components; EGM.md updated per touched package if variant surfaces change.
- Token-ize stragglers: ProductCard ×12, ExploreView ×3, App.vue gradient.
- Emoji control icons → lucide-vue-next (labels stay byte-identical; emoji inside chat/copy content untouched).
- reka behavior (focus rings, keyboard, 1-px borders): untouched.

### 4. VERIFY (skills: **design-taste-frontend** verification-only + **web-design-guidelines**)
1. `node <design-taste-frontend>/scripts/gate.mjs --start http://localhost:5173/ --kind app --category "formulation intelligence" --primary "explore formulations"` → checker + copy-lint at 1440/390/320. Verification only.
2. **web-design-guidelines** playbook (fresh Vercel fetch) over every changed file → fix every finding.
3. **New ledger gate:** `node tests/check_ui_ledger.js` → content-preservation counts must match baseline 100%.
4. Repo gates all green: `npm run build` · `python scripts/check.py` · `node tests/check_ui_semantics.js` · `pytest tests/ui_smoke.py` (disposable DB).
5. **3-strike rule:** any gate failing 3 consecutive fix attempts → stop and report.

### 5. REVIEW (new — EGM reviewer agents + design audit)
1. **impeccable** `critique` + `audit` over the changed surfaces (proven reviewer in this repo).
2. **EGM reviewer agents over the branch diff, run sequentially** (concurrency limit): **egm-design** (hostile design critic — coherence of the new system), **egm-zoom-out** (simplicity/YAGNI — anti-overengineering), **egm-codebase-details** (EGM.md/DESIGN.md accuracy vs. shipped code). Findings → fix on the branch or record in a deferred table with dispositions; nothing applied silently.

### 6. PROVE IT (skills: designlang + sloplint re-run)
1. Re-run `npx designlang` → `.redesign/after/`; re-run `sloplint.mjs` after-grade.
2. Re-run ledger inventory → final table: **"Kept 14/14 links · 5/5 fields · 9/9 handlers"** per route (also asserted by check_ui_ledger.js).
3. You see: before/after slop scores (both tools), side-by-side screenshots (7 routes × 2 widths), kept-ledger table, gate + review results.
4. Docs ship with the change: `frontend/DESIGN.md` regenerated for the new system (sanctioned overwrite, diff shown); PRODUCT.md/GLOSSARY.md unchanged (copy preserved).
5. **Merge:** you review before/after on the branch → merge to main (CI green required) → delete the branch. Motion re-plan for `add-ui-personality-and-motion` proposed separately on the new system.

## Standing constraints
- Never delete a route/component without a file-level plan shown first; expected deletions: NONE (components restyled, not removed) — only utility-covered custom CSS lines get removed, shown first.
- Never edit tests to pass checks (adding the NEW ledger check is allowed; existing tests untouched).
- Never invent content/prices/contacts; labels byte-identical where emoji→lucide swaps happen.
- Both servers must stay up for data-bearing screenshots; known risk: Node 26 vs. designlang/sloplint scripts (plain Node — low risk; shadcn CLI was the historical crasher).

## Verification (end-to-end)
All 4 repo gates green + `gate.mjs` PASS/OPEN + web-design-guidelines findings resolved + `check_ui_ledger.js` 100% retention + EGM/impeccable review dispositions recorded + slop scores before/after + side-by-side screenshots — all evidence committed on `redesign/hallmark-retheme`.