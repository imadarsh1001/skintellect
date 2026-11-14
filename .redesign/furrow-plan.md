# Furrow Re-deal + Landing Home — execution plan (branch: redesign/furrow)

> Contract for this branch. Approved 2026-11-15. Execute top-to-bottom; every phase ends with gates green and a commit.

## Context

The Console (graphite) retheme is complete on the parent branch `redesign/hallmark-retheme` (898a7ba) but the user wants **lighter** and a **real home page**. Decision: re-deal to the sanctioned **Furrow** theme (warm manila paper, near-black ink rules, Red Hat fonts, moulded keys, tangerine signal, green "in-date"; ledger voice: "never a number without its unit" — Skintellect's exact domain) and build a **new landing home at `/`** (catalog moves to `/explore`). Branching OFF the Console branch inherits the theme-agnostic structural fixes (emoji→lucide, sentence case, hit targets, focus language, ledger script, EGM accuracy). The Console phase stays in history; merge happens only after user review.

## Phase 1 — Furrow re-deal (tokens + fonts)

1. **Named-theme deal** (`theme: Furrow (by request)`, genre modern-minimal, posture committed). New Picks block (`.redesign/furrow-picks.md`); log via `theme.mjs log`. Theme spec: `C:\Users\adars\.agents\skills\hallmark\references\themes\furrow.md` (tokens, type, surfaces, range, controls, motion, voice, do-nots, build hint).
2. **Fonts:** swap `@fontsource/host-grotesk*` + `@fontsource/atkinson-hyperlegible-mono` → `@fontsource/red-hat-display` (600), `@fontsource/red-hat-text` (400/500), `@fontsource/red-hat-mono` (400/500). Remove the old packages. Red Hat Mono figures = mono-as-material (dates, times, tag numbers, doses, batches) — never on labels/chips/heads.
3. **Tokens (single file `frontend/src/assets/index.css`, same HSL-triplet + hex format the semantics test reads):**
   - Ground steps: manila `--background` (96% L, hue 85), `--card` 99.5%, `--muted` 92%; ink near-black hue 60; rule 88%.
   - **Tangerine** `--primary` oklch(70% 0.19 40) with ink text (`--primary-foreground` = ink — Furrow rule: *never tangerine as type, always a fill with ink on it*); `--ring` = focus tangerine 60%.
   - **Green** family maps to **verified** (in-date = green is Furrow's own semantic — perfect for "verified complete").
   - Evidence pairs re-dealt for light manila: verified = green/green-soft (`oklch(48% 0.11 150)` / `oklch(92% 0.04 150)`); source = slate/water-blue pair (`--color-water` oklch(60% 0.05 232)); unknown = neutral manila-grey; **negative = a NEW red pair dealt in Furrow's vocabulary** (theme has no red — document in Picks as the product's own 5-verdict extension, manila-tinted hues); mixed = violet pair. All pairs ≥4.5:1 — `tests/check_ui_semantics.js` enforces (test reads HSL triplets + hex evidence literals from the css file text — keep that format).
   - Radius: card 10px (`--radius` 0.625rem), entry 14px (xl), controls/pill 6px (sm), chips 6px; **Furrow allows shadows**: `--shadow-card`/`--shadow-lift` ONLY under floating things (menu/dialog/notebook card), never on resting surfaces.
   - Posture **committed**: tangerine carries surface via bands (the field band, `--color-accent-soft` wells).
4. **Baselines re-recorded AFTER the Phase-2 route move, BEFORE restyle edits:** screenshots + `sloplint --render --before` (8 routes) + `check_ui_ledger.js --record`. The route move is an intentional sanctioned wiring change — disclosed in the commit.

## Phase 2 — Landing home at / (new route, real content only)

1. **Router** (`frontend/src/router/index.ts`): `/` → new `HomeView.vue` (landing); `/explore` → `ExploreView.vue`; legacy hash redirects keep working; catch-all unchanged. `App.vue` tabs/nav links point Catalog at `/explore`; persona/compare-tray composables stay global.
2. **`src/views/HomeView.vue`** — landing composed per Furrow's Range, **README/PRODUCT.md-anchored facts only**:
   - Hero: what it is (one sentence from PRODUCT.md) + real stats (2,502 indexed formulations / 576 with full INCI / 1,490 dossiers — live API, same source Explore uses) + CTAs: "Explore formulations" (→ /explore) and GitHub (real repo URL).
   - "The book as an index" ruled record preview: 3 real formulation rows (live API) under an ink rule.
   - Feature cards (notebook-card style, `--radius-entry`, 1px ink ring): the 4 surfaces (Evidence Workspace, Study, Compare, Copilot) as real links with one-line real descriptions from PRODUCT.md.
   - Hero posture per Furrow "Field Record, Map hero" → use the **ruled ledger hero** (no generated survey map on the landing — that aesthetic belongs to the Graph page; no invented decoration).
   - No testimonials, no invented metrics (hard constraint).
3. **Header/nav** (App.vue): Furrow chrome — manila bar, moulded-key buttons (6px radius, 48px primary tangerine + outlined secondary), tabs per theme; nav one line 56–80px, nowrap links. Keep the global `:focus-visible` outline language; keep 44px touch targets.

## Phase 3 — Sweep, reviews, proof

1. `HALLMARK_PUPPETEER="$(npm root -g)/puppeteer-core" node <hallmark>/scripts/sloplint.mjs frontend/src --genre modern-minimal --scope app --render --kept` across 8 routes (/ + 7); fix FAIL / waive REFLEX on the stamp; `compare.html` delivered.
2. `gate.mjs` (design-taste-frontend, verification-only — run from repo ROOT) + `impeccable detect` + `check_ui_ledger.js` + `check_ui_semantics.js` + `scripts/check.py` + `npm run build` + `ui_smoke.py` (plain script; backend with `SKINTELLECT_DB_PATH=.dev-db/skintellect-dev.db`). If ui_smoke's catalog checks reference `/`, updating the URL constant = disclosed test maintenance for the sanctioned route move, never silent.
3. **EGM review trio sequentially** (egm-design → egm-zoom-out → egm-codebase-details) over the Furrow diff; CRITICAL/HIGH fixed, rest dispositioned.
4. `DESIGN.md` regenerated for Furrow (frontmatter + tangerine/green contract, ledger voice, moulded keys, shadow rules); GLOSSARY verdict color words synced.
5. PROVE IT report: before/after scores, kept-ledger table, side-by-side (`.hallmark/compare.html` + `.redesign/furrow-after/` captures).

## Operational gotchas (learned in the Console session — do not re-learn)

- Run `gate.mjs`/`sloplint.mjs` from repo ROOT only — the taste gate writes `.taste-skill/` into its cwd; inside `frontend/` it pollutes Tailwind's scan root. If `frontend/.taste-skill/` reappears, delete it.
- Restart Vite after token-file changes (stale-server HMR trap: css edits may not hot-apply).
- sloplint gate-50 needs an UNLAYERED `overflow-wrap` rule (its parser skips @layer); gate-64 guard reads `--font-outlier`; `copy: verbatim` stamp; waiver/answer lines must be standalone `/* Hallmark · waive|answered|dismissed <gate> · <guard> · <reason> */`.
- Tailwind `@source not "../.taste-skill"` stays in index.css (gate archives carry old class strings).
- Keep the tests' format contracts: `check_ui_semantics.js` reads HSL triplets (`--foreground: H S% L%`) + hex `--color-evidence-*` from the file text; `check_ui_ledger.js --record` after the route move.
- Dev servers: fresh Vite (5173) + uvicorn (8000, `PYTHONPATH=src SKINTELLECT_DB_PATH=.dev-db/skintellect-dev.db`) each session.

## Guardrails

- Content/wiring preserved byte-identical EXCEPT the sanctioned route move (`/`↔`/explore`) and the new landing route (new content = README/PRODUCT.md facts only).
- Tokens confined to `index.css`; never a second token source; Furrow scaffold files ported in and discarded.
- Never edit tests to force passes; 3-strike rule per gate; deletion-safety rule.
- Work stays on `redesign/furrow`; merge only after user review; branch deleted after merge; `redesign/hallmark-retheme` stays as the Console checkpoint until then.

## Verification

All repo gates green + sloplint 0 FAIL + kept-ledger 100% on 8 routes + EGM dispositions recorded + before/after evidence committed. Then the user reviews the light theme live and approves the merge; memory updated before any compact.
