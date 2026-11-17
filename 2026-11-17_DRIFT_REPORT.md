# EGM Drift Report — 2026-11-17

**Scope**: all 42 EGM.md contract files (root + `src/`, `frontend/`, `experiments/`, `scripts/` trees), audited against the codebase at HEAD `305ab3e` in both directions: doc-to-code hallucinations/staleness and missing public-surface coverage. Every finding below was verified in source with `file:line` evidence by six partitioned read-only auditor passes; the drift concentrates in contracts untouched since before the 2026-11-12 legacy-UI retirement (`893a020`), the Furrow retheme, and the graph/explore feature rewrites.
**Severity legend**: HIGH = contract asserts something absent/wrong (hallucinated or deleted symbol, wrong route, dead link, wrong behavior). MEDIUM = stale/imprecise/ambiguous claim that could mislead. LOW = cosmetic or wording-level drift.
**Totals**: 79 findings — 27 HIGH / 28 MEDIUM / 24 LOW — across 23 contracts; 19 contracts clean (`src/EGM.md`, 3 of 5 experiments, 15 of 16 primitives).
**Disposition**: every doc-side finding was fixed in the same round, commit `c75a9a7` (25 files). Code-level behavior untouched; the three code-vs-spec conflicts are recorded below as known-drift notes in their contracts and listed under Disposition at the end of this report.

---

## EGM.md

- [HIGH] "Source root holding the single `skintellect` application package (config, SQLite foundation, Gemini transport, CLI, and **eight child packages**)" → there are **seven** child packages (`agents`, `api`, `catalog`, `core`, `formulation`, `ingestion`, `research`); the 8th was `web`, deleted in 893a020, and the count was never updated (wording dates from initial contract commit a7dbb43). The child contract itself says "seven child contracts" (evidence: `ls src/skintellect` shows exactly 7 package dirs; `src/skintellect/EGM.md:7`)
- [HIGH] "Network: Gemini REST/SDK endpoints … PubChem PUG REST … **No other outbound providers**" → the product image proxy makes outbound HTTPS GETs to `https://storage.skinsort.com` via `urllib.request.urlopen` (`IMAGE_ALLOWED_HOSTS = {"storage.skinsort.com"}`) (evidence: `src/skintellect/api/catalog.py:35,104-111`, route `GET /api/products/{product_id}/image` at `src/skintellect/api/catalog.py:113`)
- [MEDIUM] "File writes: `data/exports/*.json` … `reports/latest/*.json` and `reports/history/` … `.env` edits" → omits the image-proxy disk cache: first fetch of a product image writes `data/cache/product-images/<product_id>` (`mkdir(parents=True)` + `os.replace`), a recurring on-demand file write (evidence: `src/skintellect/config.py:76` `IMAGE_CACHE_DIR`; `src/skintellect/api/catalog.py:130-141`)
- [MEDIUM] Missing coverage: public module constant `IMAGE_CACHE_DIR` in `config.py` is not mentioned anywhere in the contract chain (root, src, or skintellect), despite being consumed by the API layer and `tests/test_image_proxy.py` (evidence: `src/skintellect/config.py:76`; `src/skintellect/api/catalog.py:130`; `tests/test_image_proxy.py:50`)
- [LOW] "Non-contract top-level directories (no source code; intentionally not documented with contracts): `docs/`, `data/`, `reports/`, `tests/`, `.github/`" → the enumeration omits top-level `openspec/` (OpenSpec workflow dir with `specs/` and `changes/` present in the repo, undocumented either way) (evidence: repo root listing; `openspec/specs` contains 8 spec dirs)
- [LOW] "per-feature budgets cap research (6 calls/120 s)" → the research service/graph runs are 6/120, but the `POST /research/reviews/prepare` endpoint wraps its work in `run_budget(max_calls=6, max_seconds=90)` — a second research-surface budget the claim does not cover (evidence: `src/skintellect/api/research.py:143` vs `src/skintellect/research/service.py:26`, `src/skintellect/agents/graph.py:950`)

## src/EGM.md

No drift detected.

## src/skintellect/EGM.md

- [MEDIUM] Missing coverage: the `config.py` Interface block enumerates the module's public surface (`DB_PATH`, `load_environment`, `llm_enabled`, `set_embedding_model`, `set_absa_model`, `resolve_database_path`, `EXPORTS_DIR`, `PROJECT_ROOT`, `BASE_DIR`, `APP_NAME`/`APP_DESCRIPTION`/`APP_VERSION`) but omits public constant `IMAGE_CACHE_DIR` (`data/cache/product-images`), which is load-bearing for the image proxy side effect (evidence: `src/skintellect/config.py:76`; consumer `src/skintellect/api/catalog.py:130`)
- [LOW] "Generation is temperature-0 with JSON-schema-constrained output" → unconditional as written, but the `gemini-4-argon` path pops `temperature` from `generationConfig` entirely (thinking-level model), so generation on that model is not temperature-0 (evidence: `src/skintellect/gemini.py:285` vs `src/skintellect/gemini.py:297` `payload['generationConfig'].pop('temperature',None)`)
- Note: the "Known CLI drift" invariant was verified and is still accurate — `cmd_recommend`/`cmd_filter` call `get_recommendations`/`search_products` with exactly the listed nonexistent kwargs (`brand_country`, `min_match`, `limit`, `max_cloggers`, `require_*` vs actual `country`/`min_match_score`/`max_pore_cloggers`/`must_be_*`; `active_ingredient` vs `active_term`), and `cmd_recommend` still prints `p['analysis']['soothers']` while groups are keyed `smoothers` (evidence: `src/skintellect/cli.py:158-172,218,229-246`; `src/skintellect/catalog/recommendations.py:77-92,244-262,192`)

## src/skintellect/agents/EGM.md

- [HIGH] Verification: `python -m tests.smoke_agents` "(agent/board/CSI smoke checks; documented in `docs/DEVELOPMENT.md`)" → no `tests/smoke_agents.py` exists (tests/ contains only smoke_api.py, run_legacy_direct.py, etc.); the board/CSI smoke suite lives at `experiments/smoke_agents.py` and is invoked as `python -m experiments.smoke_agents` (evidence: tests/ directory listing — no smoke_agents; experiments/EGM.md:98 "no `tests/smoke_agents.py` exists"; the module actually resides at experiments/smoke_agents.py). The documented command fails with "No module named tests.smoke_agents"; the stale cross-reference it leans on is docs/DEVELOPMENT.md:129.
- [MEDIUM] Invariant: "semantic vector routing (never overriding an explicit category)" → suppression is route-specific, not absolute: code skips semantic routing only when `has_explicit_category and sem_route in ("science_qa", "greeting", "conversation_memory", "conversation_ack")`; semantic routes `compare`, `review_inquiry`, `explore`, and `general_chat` still fire (and can reroute away from search) even when the query names an explicit category (evidence: src/skintellect/agents/intent.py:371-374).
- All other claims verified against current code: `__init__.__all__` (9 exports), the five `@tool` wrappers + four input models, `IntentRoutePlan` fields, `SEMANTIC_ROUTE_ANCHORS`/threshold 0.25, clarification `task='clarification'`/`clarification-v1`/`timeout_seconds=4`/`FACET_CLUSTERS`/`DEFAULT_FACET`, graph nodes/edges/`route_after_intent`, review-ID fallback `[1, 2, 3]`, the `niacinamide-33038007` ceramide filter, `run_budget(max_calls=6, max_seconds=120)`, `deterministic_workflow`/`langgraph_compiled_workflow` trace modes, `BaseTool.__call__`/`StructuredTool.__call__` patching with `is_tool`/`tool_name`/`tool_doc` fallback, 36-char session title, `copilot_sessions`/`copilot_messages`/`gemini_runs`, `_SESSIONS`/`_VECTORIZED_ANCHORS`, `model_steps.choose_plan` ("there are no write tools" prompt), and `python -m tests.smoke_api` / `python -m tests.run_legacy_direct` (both exist). No notable public entity in the package is missing from the contract.

## src/skintellect/api/EGM.md

- [HIGH] "Static mounts: `/static` from `config.STATIC_DIR`" (Side Effects) → no `/static` mount exists and `config.STATIC_DIR` does not exist anywhere in `src/` (the constant was retired; `src/EGM.md:11` documents its removal). The only mount in the app is `/assets` from `frontend/dist/assets` via `CachedStaticFiles` (evidence: src/skintellect/api/app.py:58-60; src/skintellect/config.py:72-76 has no STATIC_DIR).
- [MEDIUM] `[catalog.py:router]` route list omits the public route `GET /api/products/{product_id}/image` (image proxy with SSRF allowlist and disk cache), which is registered on the same router (evidence: src/skintellect/api/catalog.py:113; absent from src/skintellect/api/EGM.md:9 — the word "image" appears nowhere in the contract).

## src/skintellect/catalog/EGM.md

- [MEDIUM] `[products.py]` interface list omits public `get_product_image_url`, the catalog-side loader backing the public image-proxy route `GET /api/products/{product_id}/image` (evidence: src/skintellect/catalog/products.py:201-212; src/skintellect/catalog/EGM.md:8 lists only `get_products`, `get_product_by_id`, `get_catalog_stats`, `load_records`).
- [LOW] "Module-global caches keyed by `[store.py:Catalog.stamp]`: … `[store.py:Catalog._display]`" → `Catalog._display` is a per-instance attribute initialized in `__init__` (per-catalog cache), not a module-global (evidence: src/skintellect/catalog/store.py:39 vs src/skintellect/catalog/EGM.md:31).

## src/skintellect/core/EGM.md

- [LOW] "`[policies.py:PersonaMatchResult]` (`match_percentage`, `is_eligible`, `status`, `contributing_reasons`, `flagged_concerns`, `unknown_factors`, `coverage_score`)" → the field list omits the first field `product_id` of the public dataclass (evidence: src/skintellect/core/policies.py:14)
- Note: the isolation invariant ("no production module outside `core/` imports `skintellect.core`; only `tests/test_agents_and_core.py`") was re-verified by import search and still holds exactly; all penalty/bonus/clamp/eligibility numbers match the code exactly.

## src/skintellect/formulation/EGM.md

- [MEDIUM] "`[models.py]` - FastAPI request/response contracts: `RoutineAnalyzeRequest`, `RoutineAnalyzeResponse`, `FormulaLabRequest`, `FormulaLabResponse`, …" → these classes exist with the documented defaults, but nothing in the API layer imports them: `api/formulation.py` contains only `GET /api/dupes/{product_id}` and imports from `research.alternatives`; `analyze_formula_full`/`FormulaLabResponse` are wired nowhere in `src/` (the live consumer is a duplicated copy in `experiments/formula_lab/`). Presenting them as current FastAPI contracts misleads — they are orphaned contracts for retired Formula Lab / Routine Studio routes that the root EGM itself says "remain unregistered by design" (evidence: src/skintellect/api/formulation.py:1-16 (whole router); src/skintellect/formulation/models.py:9,24,34,68 unreferenced by any `src/skintellect/api/*` import; duplicate at experiments/formula_lab/models.py:9-68)

## src/skintellect/ingestion/EGM.md

- [MEDIUM] "`[maintenance.py:clean_database]` canonicalization is fixed-policy: NULL/empty categories become `Moisturizers`" → the update is conditional: only rows with `category_slug = 'moisturizers' OR category_slug IS NULL` are converted; a NULL/empty category with any other slug (e.g. `sunscreens`) is left untouched (evidence: src/skintellect/ingestion/maintenance.py:554-559 vs src/skintellect/ingestion/EGM.md:22).

## src/skintellect/research/EGM.md

- [HIGH] "All request/response models derive from `[models.py:StrictModel]` with `extra='forbid'`: unknown fields are rejected" → `QueryRequest` and `AlternativeRequest` derive from plain `pydantic.BaseModel` with no `extra` configuration, so unknown fields are silently ignored, not rejected; `SearchIntent` also derives from `BaseModel` (it sets `extra="forbid"` explicitly, but not via `StrictModel`). These are the request models for public routes `POST /api/search/interpret`, `POST /api/alternatives`, and `POST /api/research/copilot/plan` (evidence: src/skintellect/research/models.py:155, 167, 170 vs src/skintellect/research/EGM.md:24).
- [LOW] `study.py` is absent from the Interface section: public functions `initialize`, `select_cohort`, `readiness`, `prepare_cohort`, `save_evaluation`, `main` (the module defines the study cohort and its `readiness` backs the public `GET /api/research/demo` route); it is mentioned only in passing in Verification (evidence: src/skintellect/research/study.py:17-122 vs src/skintellect/research/EGM.md:6-21, 52).

## scripts/EGM.md

- [HIGH] Overview: exhaustive inventory "The package holds three offline developer gates (`check.py`, `audit_workspace.py`, `check_query_parser.py`), two evaluation harnesses (`evaluate_review_nlp.py`, `evaluate_release.py`), and one manual smoke driver (`test_copilot_intents.py`)" → a seventh code-bearing script exists and is absent from the contract: `scripts/fetch_catalog_icons.py`, an argparse CLI (`--source`, `--refresh`) that downloads remote SVGs from assets.skinsort.com into `frontend/public/icons/` and writes per-family `manifest.json` provenance files (evidence: scripts/fetch_catalog_icons.py:26-58). It is referenced nowhere in scripts/README.md, docs/DEVELOPMENT.md, or the root README.
- [MEDIUM] Overview: "The scripts only orchestrate checks and aggregate reports; all domain logic is delegated to the `skintellect` package under `../src`" → `fetch_catalog_icons.py` performs network downloads, hashing, and file writes directly with no `skintellect` delegation (evidence: scripts/fetch_catalog_icons.py:29-58, `import urllib.request`, `ICON_ROOT` writes).
- [HIGH] Side Effects: "[scripts/audit_workspace.py:main] spawns `node --check` subprocesses for every JavaScript file under `STATIC_DIR` (30-second timeout each); a missing Node binary is recorded as an error" → no such behavior exists: the JS/`STATIC_DIR` audit was removed with the retired template trees in 893a020; the script now contains no Node invocation and reports `javascript_syntax_checked: 'moved to tests/check_ui_semantics.js'` — contradicting both the code and the contract's own Interface bullet two paragraphs earlier (evidence: scripts/audit_workspace.py:32-35, 57).
- [LOW] Interface/Side Effects: `skintellect.gemini.GeminiClient` cited at `src/skintellect/gemini.py:93` → defined at line 97 (evidence: src/skintellect/gemini.py:97).
- [LOW] Interface: `skintellect.config.DB_PATH` cited at `src/skintellect/config.py:104` → defined at line 105 (evidence: src/skintellect/config.py:105).
- All other claims verified against current code: `scripts/__init__.py` docstring-only marker, audit_workspace legacy-import module set/`?mode=ro`/link scanner/`reports/latest/workspace-audit.json`, check.py env strip list and reset values, `scripts/check.py:67` Node child lacking `TimeoutExpired` handling, 120s/30s child timeouts, `.test-work` wiring, `C:\Program Files\nodejs` PATH prepend, venv-conditional `.runtime` PYTHONPATH, check_query_parser's 20 CASES and four-field comparison, evaluate_review_nlp's 12 CASES/argparse bounds/exit 2/batches of five, evaluate_release's `--offline` mode selection, `run_budget(30, 900)`, `ValueError('prepare_cohort_before_evaluation')` gate, `ranking_metrics` keys, `review_agreement` join keys, `evaluation_kind`/`human_reviewed: False`, the `scripts/evaluate_release.py:14` intra-package import, test_copilot_intents (no functions, no `__main__` guard, cwd-relative `src`, unused `get_or_create_copilot_session` import, `copilot.py:265`/`:283`/`:236` all exact), `tests/test_release.py:143` (exact), pyproject `dev = ["ruff>=0.14,<1"]` as the only extra, absence of pytest.ini/setup.py/Makefile, and `.github/workflows/checks.yml:24: python scripts/check.py`.

## frontend/EGM.md

- [HIGH] "`:root`/`.dark` hold the semantic HSL variables" (contract line 10) → the `.dark` variable block no longer exists; index.css declares only `:root` and explicitly notes "Manila is the shipped surface: :root IS the light theme; no .dark class is applied" (evidence: frontend/src/assets/index.css:29-79; grep for `.dark` selector = 0 hits)
- [HIGH] "defines the `evidence.*` token family (`verified #12635a`, `source #245ba9`, `unknown #805309`, `negative #a63244`, `mixed #6843a8`)" → all five hex values are stale from the Furrow retheme; actual tokens are `verified #246e3a`, `source #215c78`, `unknown #4d4641`, `negative #90302e`, `mixed #554077` (evidence: frontend/src/assets/index.css:126-135)
- [HIGH] "the locally customized evidence variants (Badge `verified|source|unknown|negative|mixed`, Button `evidence`) are extracted to `src/lib/evidence.ts` and re-attached by import" → only the Badge variants exist; `evidence.ts` exports only `evidenceBadgeVariants`, and `Button.vue` has variants `default|destructive|outline|secondary|ghost|link` with no `evidence` variant and no import from `@/lib/evidence` (evidence: frontend/src/lib/evidence.ts:13-19; frontend/src/components/ui/button/Button.vue:9-27)
- [MEDIUM] Runtime dependency list (contract line 8) omits `vue-router ^4.6.4` and the three `@fontsource/red-hat-*` packages, all present in `package.json` dependencies (the fonts are imported by the CSS entry) (evidence: frontend/package.json:12-25; frontend/src/assets/index.css:21-25)
- [MEDIUM] Missing coverage: the `src/assets/index.css` description omits the entire hallmark-retheme layer — the `@theme static` motion tokens (`--duration-feedback/state/moment/stagger`, `--ease-entry/move`), the custom `@utility` definitions (`key-moulded`, `enter-rise-sm`, `stagger-entry`, `span-sweep`, `feedback`), `--scrim`, `--shadow-card/lift`, and the `--font-display/sans/outlier` faces, all load-bearing for `lib/motion.ts` and the ui primitives (evidence: frontend/src/assets/index.css:63, 73-75, 110-118, 138-159, 163-219)
- [LOW] "`vendor-vue` (vue/vue-router/@vue)" → the `manualChunks` regex also explicitly routes `@vueuse` into `vendor-vue`, which the parenthetical does not cover (evidence: frontend/vite.config.ts:37)

## frontend/src/EGM.md

- [MEDIUM] Invariant "The URL query on `/` is the authoritative explore state" → explore state is owned by the query on `/explore` (HomeView at `/` has no filters); contradicts the contract's own Overview ("/explore (ExploreView, URL-owned filters via useExploreQuery)") (evidence: frontend/src/router/index.ts:26-27; frontend/src/composables/useExploreQuery.ts:92-93)
- [MEDIUM] lib bullet describes the package as "api.ts REST/SSE client (persona adapter, stats/connections), types.ts domain contracts, utils.ts (`cn` + `inciNames` ingredient-list helper)" → utils.ts also publicly exports `keyActiveName`/`keyActiveNote`/`keyActiveIcon`/`localIconPath`/`ingredientBenefitIcons` + `KeyActive` type, and lib also contains `motion.ts`, `evidence.ts`, `evidence-summary.ts`, `markdown.ts`, none named (evidence: frontend/src/lib/utils.ts:15, 31-67; frontend/src/lib/ directory listing)
- [LOW] App.vue local-symbol enumeration omits `loadPersonas` (the `load` action App.vue destructures and calls in `onMounted`) and `goToCopilot` (the `ask-copilot-compare` handler) (evidence: frontend/src/App.vue:29-30, 92-94, 97)

## frontend/src/lib/EGM.md

- [HIGH] The `api.ts` Interface section lists 13 methods → the module exports 26 public functions; 13 are undocumented: `fetchCatalogStats`, `fetchConnections` (api.ts:137-147) and the entire Stage 5 evidence-research block — `searchInterpret`, `structuredSearch`, `assistantQuery`, `fetchDemo`, `fetchReferences`, `fetchQuality`, `fetchProgress`, `submitPreparationJob`, `cancelPreparationJob`, `prepareReviews`, `fetchAlternatives` plus their DTOs (`SearchIntentPayload`, `StructuredSearchResponse`, `DemoReadiness`, `ProgressSnapshot`, `ReviewInsights`, `AlternativesResponse`, …) (evidence: frontend/src/lib/api.ts:274-577)
- [HIGH] "`IngredientGraphNode`/`IngredientGraphLink`/`IngredientGraphData` (`types.ts:77-94`): graph DTO (co_occurrence weight) used by `api.ts` imports; note `components/graph/IngredientGraph.vue` declares its own local `GraphNode`/`GraphLink` shapes and does not use these" → wrong on all three counts: the DTOs live at types.ts:128-145; `api.ts` imports `CatalogStats, Product, ProductConnections, SkinPersona`, not the graph DTOs (api.ts:1); and `IngredientGraph.vue` no longer declares local shapes or uses a static dataset — it imports `ProductConnections` and calls `fetchConnections(id, 5)` per tray product. The DTOs it actually consumes (`ConnectionNode`/`ConnectionEdge`/`ConnectionPath`/`ProductConnections`, types.ts:89-115) are never mentioned in the contract (evidence: frontend/src/lib/types.ts:89-115, 128-145; frontend/src/lib/api.ts:1, 143-147; frontend/src/components/graph/IngredientGraph.vue:3-4, 18-52)
- [HIGH] Invariant "The reduced-motion probe is `usePreferredReducedMotion` — no hand-rolled `matchMedia('(prefers-reduced-motion: reduce)')` literals anywhere in the frontend" → two hand-rolled literals exist: `components/ai/ChatMessages.vue:31-33` and `views/ExploreView.vue:143` (evidence: frontend/src/components/ai/ChatMessages.vue:31-33; frontend/src/views/ExploreView.vue:143)
- [MEDIUM] Console side effect quoted as `console.warn('Stream failed, falling back to standard copilot ask:', ...)` (`api.ts:168`) → actual message is `'[copilot] Stream failed, falling back to non-streaming query:'` at line 239 (evidence: frontend/src/lib/api.ts:239)
- [MEDIUM] api.ts line anchors all stale: `BASE_URL` at `api.ts:3` → actually :5; `streamCopilot` degradation chain `api.ts:128-172` → actually 177-245; `deleteCopilotSession` exception `api.ts:189-194` → actually 261-266; SSE malformed-JSON warn `api.ts:151-159`/`158` → actually 215-228/227; `res.body.getReader()` `api.ts:134` → actually 203; `ProductFilters` "lines 5-22" → 7-24; `ProductsResponse` "lines 24-29" → 26-31 (evidence: frontend/src/lib/api.ts:5, 177-245, 203, 215-228, 227, 239, 261-266)
- [MEDIUM] types.ts line anchors stale: Product ABSA aspects "lines 27-32" → actually 33-38; SQLite-style safety flags "lines 40-43" → 49-52; `persona_match` "lines 44-51" → 53-60; graph DTO "77-94" → 128-145; Clarification DTO "115-127" → 166-178; `CopilotMessage` transient fields "lines 142-146" → 193-197 (evidence: frontend/src/lib/types.ts:33-38, 49-52, 53-60, 128-145, 166-178, 193-197)
- [MEDIUM] `utils.ts` Interface documents only `cn` → the module also publicly exports `inciNames`, `KeyActive`, `keyActiveName`, `keyActiveNote`, `keyActiveIcon`, `localIconPath`, `ingredientBenefitIcons` (evidence: frontend/src/lib/utils.ts:15, 31-67)
- [MEDIUM] Overview module inventory omits `evidence.ts` entirely (lists api.ts, types.ts, utils.ts, motion.ts, evidence-summary.ts, markdown.ts) although it is the public single source for the badge evidence variants re-attached in `ui/Badge.vue` (evidence: frontend/src/lib/evidence.ts:13-19; frontend/src/components/ui/badge/Badge.vue:4, 16)
- [LOW] `CopilotMessage` UI-only transient field list omits `enter` (the add-ui-personality-and-motion "settled history" flag) (evidence: frontend/src/lib/types.ts:198-199)

## frontend/src/components/EGM.md

- [HIGH] Invariant "Tailwind theme tokens mapped in `frontend/tailwind.config.js:extend.colors` (including the `evidence.*` token family)" → `tailwind.config.js` does not exist (Tailwind v4 CSS-first, as frontend/EGM.md itself states); tokens are mapped in `src/assets/index.css` `@theme inline` (evidence: frontend/src/assets/index.css:81-136; `ls frontend/tailwind.config.*` = no such file)
- [HIGH] "graph: `IngredientGraph.vue`: self-contained ingredient co-occurrence explorer with curated static dataset; no props, no emits, no API calls" → the component was rewritten as a live-data evidence graph: it declares a `products` prop and fetches `/api/products/{id}/connections` via `fetchConnections` for every tray product (graph/table view modes) (evidence: frontend/src/components/graph/IngredientGraph.vue:3-4, 18-20, 37-52)
- [HIGH] "Network calls at this level occur only in `explore/ProductDetailModal.vue` (`fetchProduct`) and `research/ResearchCopilot.vue` (`streamCopilot`, `fetchCopilotSessions`, `createCopilotSession`, `fetchCopilotSession`, `fetchEvidence`); `compare` and `graph` are offline components" → `graph/IngredientGraph.vue` makes network calls (`fetchConnections`), and `ResearchCopilot.vue` additionally calls `askCopilot`, `deleteCopilotSession` (line 162) and `fetchProduct` (line 120) beyond the five listed (evidence: frontend/src/components/graph/IngredientGraph.vue:4, 44; frontend/src/components/research/ResearchCopilot.vue:6-15, 120, 162)
- [MEDIUM] Subdirectories & Boundaries omits the `ai` package (its own EGM.md plus `AgentTrace.vue`, `ChatMessages.vue`, `PromptInput.vue`, `SourcesList.vue`, `SuggestionChip.vue`, `TaskPlan.vue`) even though the Overview names it; `ai/EGM.md` exists but is never linked (evidence: frontend/src/components/ai/ directory listing)
- [MEDIUM] ui bullet lists 10 primitives ("badge, button, card, collapsible, dialog, input, scroll-area, select, separator, tabs") → `ui/` actually contains 16: adds `checkbox`, `sheet`, `slider`, `switch`, `toggle`, `toggle-group` (evidence: frontend/src/components/ui/ directory listing)
- [LOW] "`v-html` markdown rendering in `ResearchCopilot.vue` (line 599)" → the `v-html` render is at line 506 (evidence: frontend/src/components/research/ResearchCopilot.vue:506)

## frontend/src/components/ai/EGM.md

- [LOW] "All inputs are typed payloads from `@/lib/types`" → only SourcesList (`CopilotCitation[]`) and TaskPlan (`CopilotStep[]`) take `@/lib/types` payloads; ChatMessages takes `streamTick?: number`, PromptInput takes `modelValue: string`/`busy?`/`placeholder?`, SuggestionChip takes `suggestion: string`/`disabled?` — plain primitives, not from `@/lib/types` (evidence: frontend/src/components/ai/ChatMessages.vue:10-13, frontend/src/components/ai/PromptInput.vue:11-15, frontend/src/components/ai/SuggestionChip.vue:9-12)
- Reverse direction: all six components in the directory (ChatMessages, PromptInput, SuggestionChip, SourcesList, TaskPlan, AgentTrace) are documented; no notable uncovered component. Otherwise no drift (jumpToBottom, Enter/Shift+Enter/busy/submit, `select`, `inspect`, 'failed' auto-expand, `defineModel` open, ScrollArea timeline, no `@/lib/api` imports, evidence tokens all verified).

## frontend/src/components/compare/EGM.md

- [LOW] "`ProductComparisonMatrix.vue` (single file component, 200 lines)" → file is 227 lines (evidence: frontend/src/components/compare/ProductComparisonMatrix.vue:1-227)
- [LOW] Persona fit badge precedence cited at "lines 124-144" → actually at lines 137-157; semantics (match→verified+`persona_match.score`, contraindicated→negative, `match_score`→verified, else unknown) match (evidence: frontend/src/components/compare/ProductComparisonMatrix.vue:137-157)
- [LOW] "`sharedIngredients` … intersection of every product's `names` list" / "`getUniqueIngredients` … difference of a product's `names`" → both compute over `inciNames(product)`, which prefers `names` but falls back to `ingredients[].name` (evidence: frontend/src/components/compare/ProductComparisonMatrix.vue:28,34-39; frontend/src/lib/utils.ts:15-21)
- [LOW] "Consumes only generic ui primitives (`@/components/ui/card`, `badge`, `button`)" → also imports `inciNames`/`keyActiveName`/`keyActiveNote`/`keyActiveIcon` from `@/lib/utils` and the empty state embeds a `RouterLink to="/explore"` (evidence: frontend/src/components/compare/ProductComparisonMatrix.vue:4,86-91)

## frontend/src/components/explore/EGM.md

- [HIGH] FilterSidebar "Props (`FilterSidebar.vue:defineProps`)" and "Emits (`FilterSidebar.vue:defineEmits`): `update:<propName>` for each prop plus `'reset'`" → there is no `defineProps` at all; all 11 filters are `defineModel` two-way bindings and `defineEmits` declares only `'reset'` (evidence: frontend/src/components/explore/FilterSidebar.vue:15-27)
- [HIGH] FilterSidebar "Renders native `<select>`, `<input type="checkbox">`, and `<input type="range" min="0" max="95" step="5">` elements plus ui `Button`/`Input`" → no native controls exist; uses shadcn/reka `Select`, `Switch`, `Slider` (`:min="0" :max="95" :step="5"`), and `ToggleGroup` (price tiers) alongside `Button`/`Input` (evidence: frontend/src/components/explore/FilterSidebar.vue:5-8,182-196,208-223,233-240)
- [HIGH] "`activeFilterCount` computed (`FilterSidebar.vue:activeFilterCount`, lines 85-98) counts non-default filter values" → no `activeFilterCount` symbol exists anywhere in the file (evidence: frontend/src/components/explore/FilterSidebar.vue:1-84 script section)
- [MEDIUM] Invariant "FilterSidebar … never mutates props and owns no filter state" → with `defineModel` the sidebar writes model values directly (`minMatch.value = Number(v[0])`, `priceTier = …`), a two-way contract rather than the documented emit-only pattern (evidence: frontend/src/components/explore/FilterSidebar.vue:12-14,78-83,186)
- [MEDIUM] "`getMatchScoreColor(score)`: score >= 90 → teal `#12635a`, >= 70 → blue `#245ba9`, else amber `#805309`" → returns evidence tokens whose actual values are `#246e3a` / `#215c78` / `#4d4641`; the cited hexes appear nowhere in the codebase (evidence: frontend/src/components/explore/ProductCard.vue:31-35; frontend/src/assets/index.css:126-131)
- [MEDIUM] ProductCard missing coverage: persona fit score counts up on arrival via `useCountUp` from `@/lib/motion` — behavior absent from the contract (evidence: frontend/src/components/explore/ProductCard.vue:5,41-42)
- [HIGH] ProductDetailModal "Template: five hand-rolled tab buttons (not ui Tabs)" → the modal uses ui Tabs primitives (`Tabs`/`TabsList`/`TabsTrigger` imported from `@/components/ui/tabs`) (evidence: frontend/src/components/explore/ProductDetailModal.vue:11,264-268)
- [MEDIUM] ProductDetailModal missing coverage: `loadError` retry state and the on-demand product image proxy `GET /api/products/{id}/image` with `imageState` loading/ok/failed are not in the contract (evidence: frontend/src/components/explore/ProductDetailModal.vue:59,79,88-96,182-192)
- [MEDIUM] PersonaDrawer "Behavior (`PersonaDrawer.vue:selectExisting`, `toggleGoal`, `applyCustom`)" → `toggleGoal` no longer exists; goal toggling now goes through ui `ToggleGroup` + `onGoalsUpdate` (evidence: frontend/src/components/explore/PersonaDrawer.vue:40-42,111-116)
- [MEDIUM] PersonaDrawer missing coverage: skin-type `ToggleGroup` and the "Strict Ingredient Contraindications" section with three `Switch`es bound to `exclude_fungal_acne_triggers`/`exclude_fragrance`/`exclude_drying_alcohols` are not in the contract (evidence: frontend/src/components/explore/PersonaDrawer.vue:88-106,128-154)
- [LOW] Stale line references, content itself verified: ProductCard formula badge precedence "lines 44-68" → 58-80 and safety flags "lines 128, 134, 140" → 151/157/163; ProductDetailModal local state "46-50" → 57-62, watches "66-85" → 99-118, `oil_free`/`silicone_free` "lines 316, 322" → 378/384, Raw JSON tab "lines 578-580" → 663-664, footer anchors "lines 588-597" → 673-682; PersonaDrawer "lines 28-29" → 29-30 and "`PersonaDrawer.vue:31`" → 32 (evidence: frontend/src/components/explore/ProductCard.vue:58-80,151-163; frontend/src/components/explore/ProductDetailModal.vue:57-62,99-118,378,384,663-664,673-682; frontend/src/components/explore/PersonaDrawer.vue:29-32)
- Reverse direction: all five components documented; ProductGrid matches the contract fully.

## frontend/src/components/graph/EGM.md

The contract describes a deleted implementation; the component was rewritten as a live-data explorer.

- [HIGH] "self-contained … interactive SVG graph view … The dataset is curated static data embedded in the component; it declares no props and no emits and performs no API calls" → the component takes a required `products: Product[]` prop and fetches live data via `fetchConnections(id, 5)` → `GET /api/products/{id}/connections` on mount and on every compare-tray change (evidence: frontend/src/components/graph/IngredientGraph.vue:4,18-20,29-52,44; frontend/src/lib/api.ts:143; src/skintellect/api/research.py:61-62)
- [HIGH] "`GraphNode` interface (lines 8-16) … `GraphLink` interface (lines 18-22)"; "Embedded dataset … 11 curated moisturizer ingredients … 12 weighted co-occurrence links, weights 2-5"; "`selectedNode` (defaults to … `ceramide-np`), `viewMode` …, `searchQuery`"; "`filteredNodes`"; "`getCategoryColor` … barrier `#12635a` … excipient `#526277`" → none of these symbols exist; actual state is `viewMode`/`connectionsByProduct`/`loading` with `NODE_STYLES` for node types `product|ingredient|reference` (evidence: frontend/src/components/graph/IngredientGraph.vue:22-24,67-71)
- [HIGH] "graph view renders a static-position SVG (`viewBox="100 80 500 300"`, line 126) … clicking a node sets `selectedNode` (r 17 → 22) … dossier card …" → there is no SVG at all; the "Connections" view renders per-product evidence `Card` panels (ingredient badges, related formulas/paths, reference nodes, backend `notice`) (evidence: frontend/src/components/graph/IngredientGraph.vue:131-223)
- [HIGH] "table view renders a searchable `<table>`" → the table exists but is not searchable (no search input or query state); it renders an edge table with `relation` and `evidence_id` columns (evidence: frontend/src/components/graph/IngredientGraph.vue:226-261)
- [HIGH] Invariant "dataset is static and curated in component source … no runtime data loading" and Side Effects "None (no network, storage, or console access)" → runtime loading via `loadAll()` with per-product `'error'` state and a Retry button (evidence: frontend/src/components/graph/IngredientGraph.vue:29-52,135-141)
- [HIGH] "No props/emits: the component cannot be parameterized from outside" → it declares `defineProps<{ products: Product[] }>()` (evidence: frontend/src/components/graph/IngredientGraph.vue:18-20)
- [MEDIUM] Missing coverage for the actual feature set: per-product error/retry cards, empty state with `RouterLink to="/explore"`, loading skeleton, "related formulas" count badge — none described in the contract (evidence: frontend/src/components/graph/IngredientGraph.vue:111-129,135-141,150-152)
- [LOW] "(single file component, 258 lines)" → file is 264 lines (evidence: frontend/src/components/graph/IngredientGraph.vue:1-264)

## frontend/src/components/research/EGM.md

- [HIGH] "`deleteCopilotSession` is exposed by the API client but has no UI affordance yet" → a Delete affordance exists: header trash button → `confirmDeleteSession()` (toast with Delete action) → `handleDeleteSession(sid)` calls `deleteCopilotSession` and re-selects/creates a session (evidence: frontend/src/components/research/ResearchCopilot.vue:13,149-175,427-436)
- [MEDIUM] Missing coverage: `onMounted` also runs `consumeProductContext()` — reads `route.query.product_id`, fetches the product via `fetchProduct`, pushes a "on the analysis bench" context message, and clears the query param with `router.replace` (URL handoff from "Ask Copilot About This Formula"); correspondingly the Side Effects list omits the `fetchProduct` and `deleteCopilotSession` network calls (evidence: frontend/src/components/research/ResearchCopilot.vue:109-131,120,162)
- [MEDIUM] Missing coverage: `stream_fallback` SSE event handled with a degraded-mode `toast.info('Live streaming is unavailable…')`, and `tool_calls` mapped from `res.trace.tools` — neither in the contract's stream-mapping list (evidence: frontend/src/components/research/ResearchCopilot.vue:282-286,326-330)
- [LOW] "`ResearchCopilot.vue` (single file component, ~600 lines)" → file is 768 lines (evidence: frontend/src/components/research/ResearchCopilot.vue:1-768)
- Reverse direction: no undocumented components. All other claims verified (props/emits, the six `@/components/ai/` pattern components, `renderMarkdown` = marked + DOMPurify at frontend/src/lib/markdown.ts:1-24, `NODE_ORDER`, `inspectCitation` offline fallback, HITL clarification cards + `allow_custom` custom input, re-entrancy guard, `try/finally` loading reset, starter bar `messages.length <= 2`, "Current Session" entry, clipboard 2000 ms reset, emits-only product UI).

## frontend/src/components/ui/EGM.md (umbrella)

- [MEDIUM] Sheet package inventory: "Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle, SheetDescription" (6 components) → the sheet package publicly exports 8 components: `SheetClose` and `SheetFooter` are also exported from `sheet/index.ts` but omitted from the contract's list (internal `SheetOverlay` is additionally present, not exported) (evidence: frontend/src/components/ui/sheet/index.ts:2,5)
- [LOW] Overview: "sixteen shadcn-vue style component packages built as thin wrappers around reka-ui headless components" → overgeneralization: the card package contains zero reka-ui references (all 6 `Card*.vue` are plain layout divs), and `badge` (cva-styled div) / `input` (native `<input>` + `@vueuse/core` `useVModel`) do not wrap reka-ui either; 12 of 48 `.vue` files import no reka-ui (evidence: frontend/src/components/ui/card/Card.vue:1-20, frontend/src/components/ui/input/Input.vue:3, frontend/src/components/ui/badge/Badge.vue:1-5)
- [LOW] Cross-Package Invariants: "`animate-in`/`animate-out`... transition classes declared in dialog, select, and collapsible templates" → sheet templates also declare `animate-in`/`animate-out` and are omitted from the enumeration (evidence: frontend/src/components/ui/sheet/SheetOverlay.vue, frontend/src/components/ui/sheet/SheetContent.vue:35)

## frontend/src/components/ui/badge/EGM.md

No drift detected.

## frontend/src/components/ui/button/EGM.md

No drift detected.

## frontend/src/components/ui/card/EGM.md

No drift detected.

## frontend/src/components/ui/checkbox/EGM.md

No drift detected.

## frontend/src/components/ui/collapsible/EGM.md

No drift detected.

## frontend/src/components/ui/dialog/EGM.md

No drift detected.

## frontend/src/components/ui/input/EGM.md

No drift detected.

## frontend/src/components/ui/scroll-area/EGM.md

No drift detected.

## frontend/src/components/ui/select/EGM.md

No drift detected.

## frontend/src/components/ui/separator/EGM.md

No drift detected.

## frontend/src/components/ui/sheet/EGM.md

No drift detected.

## frontend/src/components/ui/slider/EGM.md

No drift detected.

## frontend/src/components/ui/switch/EGM.md

No drift detected.

## frontend/src/components/ui/tabs/EGM.md

No drift detected.

## frontend/src/components/ui/toggle/EGM.md

- [LOW] "`toggleVariants` (`index.ts`): … handles pressed state (`data-[state=on]`), disabled, focus-visible ring, svg sizing" → `toggleVariants`'s base string contains no `focus-visible:` classes at all; the toggle's focus ring comes from the global `:focus-visible` rule (an `outline`, not a ring utility), which the contract does not mention — unlike the tabs contract, which correctly attributes the ring to that global rule (evidence: frontend/src/components/ui/toggle/index.ts:9 — base string has `aria-invalid:ring-destructive/20` but no focus-visible classes; frontend/src/assets/index.css:264 — `:focus-visible { outline: 2px solid hsl(var(--ring)); … }`)

## frontend/src/components/ui/toggle-group/EGM.md

No drift detected.

## experiments/EGM.md

No drift detected. (CLI flags/defaults, fixed sample deck and default question, smoke suite stage banner, all four `smoke_agents.py` test functions incl. the gracefully-skipped `test_decoupled_router` with `skintellect.api.agents` genuinely absent, `AGENT_LLM_MODE=offline` at import without restore, `.runtime/` sys.path bootstrap for the smoke suite only, unittest file forcing `mock` per test, `tests/smoke_api.py` present while `tests/smoke_agents.py` is absent yet referenced by docs/DEVELOPMENT.md:129 and docs/modules/agents.md:30, no pytest in pyproject.toml, all six external `src/skintellect` paths — all verified.)

## experiments/formula_lab/EGM.md

No drift detected. (all function signatures, return-key lists, scoring arithmetic incl. the `[34,43]` fungal cliff with the stale `[34%,45%]` docstring note, Darmeto bonuses/deductions/tiers, floors 30/25/30/20 and binary fungal_safe 100/35, exact/alias-only DB matching, `None`-not-`True` flags, `tier="Heuristic score band"`, audit-log prefix string, `_INGREDIENTS_DB`/`_INGREDIENTS_STAMP` stamp-keyed cache, stdout reconfigure, all 9 pydantic models with their default strings, and the "diverged fork" claim vs `src/skintellect/formulation/scoring.py` (90-line divergence) — all verified.)

## experiments/ingredient_csi/EGM.md

- [LOW] Suspect score model: "+ `25` if absent from all safe decks" → the code adds +25 only when at least one safe deck was supplied (`if safe_decks: score += 25`); with zero safe decks candidates are vacuously absent from all safe decks yet receive no +25, so scores are 20 points lower than the contract's model in that case (evidence: experiments/ingredient_csi/detective.py:163-164)

## experiments/label_ocr/EGM.md

- [LOW] Side Effects cites `src/skintellect/gemini.py:249` (gemini_runs INSERT) and `src/skintellect/gemini.py:304` (gemini_cache INSERT OR REPLACE) → the statements are behaviorally correct (ensure_tables first, finally-block `_record` insert, cache insert on success) but the anchors have drifted to lines 253 and 308 (evidence: src/skintellect/gemini.py:253-258, 307-309, 315-316)

## experiments/specialist_board/EGM.md

No drift detected. (orchestrator composition, 5-round order and `round`/`stage` tags, return dicts of `run_deliberation`/`stream_deliberation`, SSE payload types init/typing/turn/done with 0.3 s/0.4 s sleeps, `_resolve_persona` fallback chain to hardcoded "Universal Combination Profile", all agent identities and return-key sets, first-5-token vehicle detection, persona-gated fungal flagging in the critic, judge never calling the LLM with >=90/>=75 consensus strings, `LLMClient(mode='auto')` env-precedence for `AGENT_LLM_MODE`, `TextResponse` 12000-char cap, `legacy_agent` task name, telemetry single-slot fields, package-marker-only `__init__.py`, and all four referenced `src/skintellect/formulation/scoring.py` symbols — all verified.)

---

## Disposition

- **FIXED (commit `c75a9a7`, 25 files)** — all doc-side findings above: legacy-UI references (root child count, `/static` mount, `audit_workspace` node scan, smoke_agents paths in `agents/EGM.md` + `docs/DEVELOPMENT.md` + `docs/modules/agents.md`), Furrow-retheme token hexes, the graph contract rewritten for the live-data component, FilterSidebar/ProductDetailModal/PersonaDrawer re-synced to their reka-ui implementations, 13 undocumented `api.ts` methods, 16-primitive ui inventory, sheet's 8 exports, image-proxy coverage across the contract chain (root → src → api → catalog → explore modal), all stale line anchors, and missing-coverage bullets (`study.py`, `get_product_image_url`, `IMAGE_CACHE_DIR`, `evidence.ts`, `useCountUp`, copilot delete/context/stream_fallback, App.vue symbols, fetch_catalog_icons.py).
- **Known-drift notes added to contracts (no code change)**: `research/EGM.md` (QueryRequest/AlternativeRequest/SearchIntent not `StrictModel`-derived — making them strict would change API behavior; user decision pending), `frontend/src/lib/EGM.md` (two hand-rolled `matchMedia('(prefers-reduced-motion: reduce)')` literals at `ChatMessages.vue:31-33` and `ExploreView.vue:143` violate the openspec ui-motion invariant — candidate small refactor to `usePreferredReducedMotion`), `frontend/src/components/explore/EGM.md` (FilterSidebar's `defineModel` two-way bindings supersede the emit-only pattern).
- **Pre-existing, documented, left as-is**: the `cli.py` `cmd_recommend`/`cmd_filter` TypeError drift (verified still accurate, already recorded in `src/skintellect/EGM.md`), and the unwired `research/labels.py:read_label` handler (root boundary note + `api/EGM.md` known-drift line).
