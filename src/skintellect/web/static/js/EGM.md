# JS (Plain-JavaScript Frontend Bundles)

## Overview
Vanilla-JS frontend bundles served under `/static/js`. Two stacks coexist: the Vue 3 single-page Studio (`app.js` + `api.js`, loaded by `templates/index.html` with the vendored Vue from `/static/vendor/`) and the text-only server-rendered workspaces (`workspace.js` shared runtime plus page scripts `research.js`, `study.js`, `progress.js`). All rendering is text-only; source content never becomes trusted HTML (`workspace.js` header comment).

## Interface
- `[workspace.js:Studio]` - global facade `window.Studio` exposing `text`, `button`, `badge`, `api`, `safeLink`, `details`, `raw`, `aspect`, `table`, `stat`, `insight`, `reviewSummary`, `evidence`, `observation`, `filterObservations`, `quoteExplorer`, `status`; also runs `[workspace.js:initTabs]` on load.
- `[workspace.js:api]` - fetch wrapper prefixing `/api`, POST JSON bodies, and humanizing error codes (`preparation_already_active`, `disabled_or_missing_key`, `invalid_image_signature`, ...) via `[workspace.js:errorMessage]`.
- `[workspace.js:evidence]` - lazy-loaded `<details>` that fetches `/evidence/{id}` and renders `reported_experience`, `reference_note`, or catalog-record kinds; `[workspace.js:safeLink]` - only `http:`/`https:` links with `rel="noopener noreferrer"`.
- `[api.js:API]` - `window.API` REST client: `fetchProducts`, `fetchProductDetail`, `fetchPersonas`, `createPersona`, `analyzeRoutine`, `fetchDupes`, `analyzeFormula`, `fetchStats`, `fetchDomains`, `fetchIngredients`, `fetchIngredientDetail`, `fetchIngredientFunctions`, `fetchAgentsMeta`, `deliberateBoard`, `investigateCsi`.
- `[app.js]` - Vue 3 app (`createApp` from the global `Vue`) mounted on `#app`: catalog grid with filters/pagination (`loadProducts`, `debouncedSearch`), ingredient explorer (`ingState`), routine builder (`routine`, `analyzeRoutine` via `API`), compare tray, persona management (`applyPersona`, `saveCustomPersona`, `downloadPersonaJson`, `copyPersonaJson`), Formula Lab (`runFormulaAnalysis` via `API.analyzeFormula`), dupes modal (`loadDupesForProduct` via `API.fetchDupes`), and AI Board / CSI panels (`runAiBoardDeliberation`, `runCsiInvestigation`).
- `[research.js]` - research workspace page script: binds `#assistant`, `#interpret`, `#search` buttons to `/assistant/query`, `/search/interpret`, and `/search`; renders editable filters, evidence cards, and the answer panel; loads `/research/demo`, `/research/status`, and `/quality` on start.
- `[study.js]` - prepared-study page script: `loadStudy` (GET `/research/demo`), `loadReferences` (GET `/research/references`), `inspectProduct` (GET `/products/{id}/review-insights` + `/products/{id}/connections`), label transcription form (POST `/research/label` via `Studio.api`).
- `[progress.js]` - data-progress page script: polls `/research/progress` + `/research/demo` (`[progress.js:refresh]`), submits `[progress.js]` `#job-form` to `POST /research/jobs`, cancels via `POST /research/jobs/{id}/cancel`, re-renders only when the jobs JSON signature changes (`jobSignature`).

## Invariants
- Text-only rendering: every value is inserted with `textContent`/`createElement` (`[workspace.js:text]`); raw JSON appears only inside `<pre>` in collapsed `<details class="technical">` (`[workspace.js:raw]`).
- `[workspace.js:safeLink]` refuses non-HTTP(S) protocols and always sets `rel="noopener noreferrer"`.
- `Studio.api` treats unknown underscore error codes as opaque (404 -> "record no longer available", 422 -> "check the fields") and never surfaces provider bodies.
- `[progress.js]` polling runs every 5 seconds only while `!document.hidden && !submitting`; renders are idempotent via the `jobSignature` guard.
- `[study.js]` client-side mirrors server limits: label uploads must be PNG/JPEG and <= 6,000,000 bytes before POSTing; review snapshots are cached per product in `reviewCache` and evicted on error.
- `[app.js]` persona selection persists to `localStorage` key `skintellect_active_persona_id` (reading legacy `skinsort_active_persona_id` as fallback) and restores it on boot.
- Backend boundary drift (verified against `src/skintellect/api`): `[app.js]` calls `API.analyzeRoutine` (`POST /api/routine/analyze`) and `API.analyzeFormula` (`POST /api/formula-lab/analyze`), and `[api.js:API.deliberateBoard]`/`[api.js:API.investigateCsi]` call `/api/agents/*`; `[study.js]` posts `/research/label`. None of these routes are defined by the current FastAPI routers in `src/skintellect/api`, so those features return 404 until wired.

## Side Effects
- Network: all `fetch()` calls to same-origin `/api/*` endpoints listed above; Google Fonts and CDN Tailwind are loaded by the HTML host page, not by these files.
- DOM mutation: pages replace children of fixed element IDs (`#results`, `#jobs`, `#coverage`, `#products`, ...) and register event listeners; `[workspace.js:initTabs]` wires `[role=tablist]` keyboard navigation (Arrow/Home/End).
- Browser storage: `localStorage.setItem('skintellect_active_persona_id', ...)` in `[app.js:applyPersona]`.
- Clipboard: `navigator.clipboard.writeText` for routine markdown, persona JSON, and formula audit logs in `[app.js]`.
- Timers: `[app.js]` debounce timers (`searchTimer` 300 ms, `ingSearchTimer`, `formulaTimer`), `[progress.js]` 5-second `setInterval` polling, `copyFeedback` resets after 2 seconds.

## Verification
- Python backend; no pytest configured; this directory is plain JS with no build manifest. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
- `tests/check_ui_semantics.js` exists for UI semantic checks and `tests/ui_smoke.py` exercises the UI over HTTP.
