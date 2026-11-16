> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Consolidated Review Report — Route-Level Code Splitting Delivery

**Scope:** commits `6f64eb6` (route lazy imports + vendor chunks), `46e57bb` (stale-chunk reload guard), `95a0e72` (review fixes: /explore handler, Firefox regex, cache headers), `4516ba5` (contract sync + key rename), `274557f` (follow-up: catch-all SPA route + shared stale-chunk recovery).
**Reviewers:** in-context karpathy-guidelines audit + EGM trio dispatched as isolated agents (egm-design → egm-zoom-out → egm-codebase-details), per the repo's review protocol.
**Disposition legend:** FIXED = fixed in this review round; ADOPTED-NIT = small fix applied; CORRECTED = claim corrected in this report, commit text left as history; DONE = fixed in the user-approved `274557f` follow-up; CONTESTED = rejected with rationale; ACCEPTED / DOCUMENTED = kept as recorded trade-off, no code change; DEFERRED = recorded, needs its own decision.

## Verified facts (recomputed by egm-codebase-details, not trusted)

- Before: single 610KB JS chunk (183KB gzip).
- After: first paint = entry 60,082 B (16,890 gzip) + vendor-vue 32,230 + vendor-reka 115,029 + vendor-misc 174,876 + HomeView 5,493 = **387,710 B raw / 124,273 B gzip**. index.html modulepreloads exactly that vendor set (confirmed against `frontend/dist/index.html`).
- `vendor-misc` = 45.1% of first-paint JS (comment in vite.config.ts is accurate).
- Markdown vendor 81,222 B loads only on `/copilot` (ResearchView does NOT import the markdown pipeline — the 6f64eb6 message overclaimed "Copilot/Research").
- Reload-guard loop protection verified: flag set before `location.assign`, cleared only by successful `afterEach`.
- Regex audit clean: `lucide-vue-next`/`vue-sonner` cannot match `vendor-vue` (trailing `[\\/]`); Windows paths normalized by Vite.

## Consolidated findings & dispositions

| # | Sev | Finding | Disposition |
|---|-----|---------|-------------|
| K1 | Major | Original claim "first-paint dropped ~50% (184→33KB gzip)" ignored eager vendor-reka + vendor-misc pinned by App.vue chrome (Tabs→reka-ui, Toaster→vue-sonner, lucide). True reduction ≈ 32% gzip (184→124KB). | CORRECTED in this report; commit messages are history. |
| K2 | Major | Dynamic imports introduced a new failure mode: client holding old index 404s on lazy chunk after a redeploy → zombie tab. | FIXED — `46e57bb` router.onError guard. |
| K3 | Minor | Only 3 of 8 routes live-verified; CI runs check.py + build + semantics but NOT ui_smoke. | FIXED — all 8 routes verified on built dist (read-only browser pass). |
| D8 | Major | `GET /explore` had no FastAPI handler — direct load/refresh/shared link returned JSON 404. Pre-existing hole from the furrow route move (b29b375); ui_smoke structurally could not catch it (drives its own static shim, tests/ui_smoke.py:176). | FIXED — handler added in `95a0e72`, TestClient-probed 200. |
| D6 | Major | Reload-guard regex missed Firefox ("error loading dynamically imported module"). | FIXED — all three browser messages covered (`95a0e72`). |
| D5 | Major | Cache-stability rationale unimplemented server-side (StaticFiles sends no Cache-Control; index.html headerless). | FIXED — immutable assets + no-cache HTML (`95a0e72`), TestClient-probed. |
| D7 | Major | Guard regex can't distinguish stale-404 from offline blip → transient failure costs one reload; in-memory state (e.g. half-typed message) lost. | ACCEPTED as documented trade-off (router comment); canonical pattern; build-id probe rejected as machinery for a rare event. |
| D9 | Major | `emptyOutDir` wipes assets in place → non-atomic deploy window; guard is a band-aid at the wrong layer. | DEFERRED — deployment topology (keep-N builds / swap) is infra work beyond this change; single-box manual deploys. |
| Z1 | Major | manualChunks taxonomy is a re-partition; Rollup defaults would defer markdown too; taxonomy splits by package identity, not load timing. | CONTESTED — kept: stable chunk names across app-only deploys + readable dist; 12 lines; alternative recorded here. |
| Z5 | Major | /explore fix patched one instance; the failure class wants one catch-all SPA route replacing 8 handlers (net −25 lines). | DONE — `274557f` (user-approved follow-up; catch-all GET /{spa_path:path} + /api JSON-404 guard; probes: unknown SPA path 200, /api/nonexistent 404, /health + /docs unaffected). |
| Z6 | Nit | serve_index duplicates _serve_spa body (no-cache had to be added twice). | DONE — `274557f` (collapsed; no-build now a direct 503 everywhere). |
| Z4 | Nit | `?? pathname+search+hash` fallback reinvents `window.location.href`. | ADOPTED-NIT in `95a0e72` (preserving deep links); href simplification noted, equivalent semantics. |
| Z2/F2 | Major/Nit | vendor-misc unbounded catch-all eroding cache stability. | DOCUMENTED in vite comment (size/membership caveat); size-budget CI step deferred. |
| C1 | Blocker | frontend/src/EGM.md route table contradicted the router (pre-furrow map: `/`→ExploreView, /research→redirect); lazy loading + guard undocumented. | FIXED — `4516ba5` (8-route map, lazy loading, guard, sessionStorage key). |
| C2 | Major | api/EGM.md omitted /explore + cache policy. | FIXED — `4516ba5`. |
| C3 | Major | frontend/EGM.md omitted manualChunks; deps list missing dompurify + vue-sonner (pre-existing). | FIXED — `4516ba5`. |
| C4 | Major | Root EGM.md route list omitted /explore (pre-existing). | FIXED — `4516ba5`. |
| C6 | Nit | Storage key `skintellect:chunk-reload` broke `skintellect_*` snake_case convention. | FIXED — renamed `skintellect_chunk_reload` in `4516ba5`, contract updated. |
| C7 | Nit | "loads only when Copilot/Research render markdown" — only Copilot triggers it. | CORRECTED in this report (commit text is history). |
| C8 | Nit | "no-cache so it always revalidates" imprecise (HTMLResponse has no ETag → full refetch, no 304). | FIXED — comment corrected in `4516ba5`. |
| C9 | Nit | "hard-reload" wording (assign is a normal nav; works because of the later no-cache header). | CORRECTED in this report (history). |
| D10 | Nit | bfcache edge: flag restored via bfcache before afterEach clears → one unrecovered failure. Narrow; timestamped-flag alternative recorded. | DEFERRED. |
| D12 | Nit | Non-router async chunks (reka SelectItem/CardContent) uncovered; no app.config.errorHandler. | DONE — `274557f` (recoverFromStaleChunk exported and shared by app.config.errorHandler in main.ts; anything else logs). |
| D11 | Nit | Deep-link loss when `to` undefined in onError. | ADOPTED-NIT — fallback preserves pathname+search+hash (`95a0e72`). |
| D4 | Nit | No per-route loading UI between chunk fetch and render. | DEFERRED — imperceptible on cached/local loads; re-deal only if real-world navigation lag shows. |

## Commits produced by this review round

- `46e57bb` fix(ui): reload once on stale chunk fetch after a redeploy
- `95a0e72` fix(ui+api): review round on code splitting — explore 404, Firefox chunk error, cache headers
- `4516ba5` docs(contracts): sync EGM contracts with route splitting + cache policy; rename reload-guard key
- `274557f` refactor(api+ui): catch-all SPA route replaces 8 hand-written handlers; shared stale-chunk recovery (Z5/Z6/D12 done)

## Verdict summary

- karpathy lens: approved scope executed (lazy routes + vendor chunks, direct to main); gaps were claim precision (K1), an introduced failure mode (K2), and verification coverage (K3) — all corrected in-turn.
- egm-design: "conditionally approve pending findings 1, 2, 6, 7, 8, 9" → 1 corrected, 2 documented, 6/8 fixed, 7 accepted-documented, 9 deferred.
- egm-zoom-out: "earns its complexity at 70%" — route-splitting + index no-cache unambiguously worth it; guard = cheap insurance; taxonomy contested (kept); catch-all refactor proposed.
- egm-codebase-details: "the docs, not the code, lie here" → all four contracts synced.

**Remaining open items (all deferred, awaiting evidence — do not act unprompted):** D9 deploy topology (keep-N builds); Z2 vendor-misc size budget; D10 bfcache flag TTL; D4 route loading UI.
