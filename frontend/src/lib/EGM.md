# lib

## Overview
Peanut package holding the frontend's shared infrastructure: the backend REST/SSE API client (`api.ts`), the domain type contracts (`types.ts`), the Tailwind class merge helper (`utils.ts`), the motion helpers (`motion.ts`), the badge evidence-variant source (`evidence.ts`), plus the evidence-summary builder (`evidence-summary.ts`) and markdown renderer (`markdown.ts`) — the latter three still owe their own interface sections here. Every component-level network call, cross-component type, and motion-token read flows through this package.

## Interface
### `utils.ts`
- `cn(...inputs: ClassValue[])` (`utils.ts:cn`, lines 4-6): `twMerge(clsx(inputs))` from `clsx` + `tailwind-merge`; the single styling merge helper used by all `ui/` primitives
- `inciNames(product)` (`utils.ts:15-21`): prefers `product.names` but falls back to `ingredients[].name` — the single display/diff ingredient-list helper
- `KeyActive` / `keyActiveName` / `keyActiveNote` / `keyActiveIcon` / `localIconPath` / `ingredientBenefitIcons` (`utils.ts:31-67`): active-ingredient keying and local icon-path helpers backing the compare matrix and explore cards

### `types.ts` (type-only module, no runtime code)
- `FormulaStatus` (`types.ts:FormulaStatus`): `'verified_complete' | 'unverified' | 'missing'`
- `Product` (`types.ts:Product`): catalog entity; notable contracts: `ingredients?: Array<{ name: string; [key: string]: any }>`, `names?: string[]` (INCI list), `reviews[]` with ABSA `aspects` (`aspect`, `sentiment: 'positive' | 'negative' | 'neutral'`, `negated`, `span`, lines 33-38), safety flags typed as SQLite-style integer booleans (`fungal_acne_safe?: number`, `fragrance_free?: number`, `alcohol_free?: number`, `oil_free?: number`, lines 49-52), `persona_match` with `match_status: 'match' | 'contraindicated' | 'unknown'` (lines 53-60)
- `SkinPersona` (`types.ts:SkinPersona`): `id`, `name`, `skin_type: 'oily' | 'dry' | 'combination' | 'sensitive' | 'normal'`, `concerns`, `goals`, exclusions `exclude_fungal_acne_triggers`/`exclude_drying_alcohols`/`exclude_fragrance`, `custom_exclusions`
- `PersonaEvaluation` (`types.ts:PersonaEvaluation`): per-product persona result incl. `missing_formula: boolean`
- `ConnectionNode` / `ConnectionEdge` / `ConnectionPath` / `ProductConnections` (`types.ts:89-115`): the live connections-graph DTO consumed by `components/graph/IngredientGraph.vue` through `api.ts`'s `fetchConnections`. (`IngredientGraphNode` / `IngredientGraphLink` / `IngredientGraphData` also exist at `types.ts:128-145` as legacy co-occurrence shapes — `api.ts` does not import them and no component uses them.)
- `CopilotStep` (`types.ts:CopilotStep`): `status: 'pending' | 'in_progress' | 'completed' | 'failed'`
- `CopilotToolCall` (`types.ts:CopilotToolCall`): `status: 'executing' | 'done' | 'failed'`
- `CopilotCitation` (`types.ts:CopilotCitation`): `source_kind: 'product' | 'review' | 'reference_note'`
- `ClarificationOption` / `ClarificationPayload` (`types.ts:166-178`): HITL clarification DTO (`needs_clarification`, `options[]`, `allow_custom`)
- `CopilotMessage` (`types.ts:CopilotMessage`): chat message incl. UI-only transient fields `showDebugger`, `showPlan`, `showCustomClarification`, `customClarificationText`, `streamingStage` (lines 193-197) plus `enter` (the motion-arc "settled history" flag, lines 198-199)

### `api.ts` (all endpoints relative; `BASE_URL = ''` at `api.ts:5`)
- Types: `ProductFilters` (`api.ts:ProductFilters`, lines 7-24), `ProductsResponse` (`api.ts:ProductsResponse`, lines 26-31)
- `fetchProducts(filters?)` (`api.ts:fetchProducts`): GET `/api/products?...`; serializes filters to `URLSearchParams`, booleans sent as `'true'`
- `fetchProduct(id, personaId='uap')` (`api.ts:fetchProduct`): GET `/api/products/{id}?persona_id=...`
- `fetchPersonas()` (`api.ts:fetchPersonas`): GET `/api/personas`
- `savePersona(persona)` (`api.ts:savePersona`): POST `/api/personas` (JSON body)
- `fetchDupes(productId)` (`api.ts:fetchDupes`): GET `/api/dupes/{productId}`
- `fetchEvidence(evidenceId)` (`api.ts:fetchEvidence`): GET `/api/evidence/{evidenceId}` (encoded)
- `fetchReviewInsights(productId)` (`api.ts:fetchReviewInsights`): GET `/api/products/{productId}/review-insights` (404s when the product has no resolvable evidence, per the backend route in `src/skintellect/api/research.py`)
- `askCopilot(payload)` (`api.ts:askCopilot`): POST `/api/research/copilot` (JSON; payload fields `session_id?`, `persona_id?`, `query`, `product_ids?`, `planning_mode?`)
- `streamCopilot(payload, onUpdate)` (`api.ts:streamCopilot`): POST `/api/research/copilot/stream`; manual SSE parsing — splits stream on `\n\n`, accepts `data: ` prefixed chunks, skips `[DONE]`, forwards parsed events to `onUpdate` (`{ event, node?, data }`), returns the `final_result` data
- `fetchCopilotSessions()` (`api.ts:fetchCopilotSessions`): GET `/api/research/copilot/sessions`
- `createCopilotSession(personaId='uap')` (`api.ts:createCopilotSession`): POST `/api/research/copilot/sessions/new?persona_id=...`
- `deleteCopilotSession(sessionId)` (`api.ts:deleteCopilotSession`): DELETE `/api/research/copilot/sessions/{sessionId}`; returns `res.ok` boolean
- `fetchCopilotSession(sessionId)` (`api.ts:fetchCopilotSession`): GET `/api/research/copilot/sessions/{sessionId}` (encoded)
- `fetchCatalogStats()` (`api.ts:fetchCatalogStats`): GET `/api/stats`
- `fetchConnections(productId, depth=5)` (`api.ts:fetchConnections`): GET `/api/products/{productId}/connections`
- Evidence-research surface (`api.ts:274-577`): `searchInterpret`, `structuredSearch`, `assistantQuery`, `fetchDemo`, `fetchReferences`, `fetchQuality`, `fetchProgress`, `submitPreparationJob`, `cancelPreparationJob`, `prepareReviews`, `fetchAlternatives` plus their DTO types (`SearchIntentPayload`, `StructuredSearchResponse`, `DemoReadiness`, `ProgressSnapshot`, `ReviewInsights`, `AlternativesResponse`, …) — mirroring the research-router endpoints listed in `src/skintellect/api/EGM.md`

### `motion.ts` (add-ui-personality-and-motion)
- `motionDurationMs(tokenName)` (`motion.ts:motionDurationMs`): reads a `--duration-*` custom property off `:root` and parses it to milliseconds — handles both `"450ms"` and `".45s"` (minified output); returns `0` when the token is missing, so callers degrade to instant
- `useCountUp(target, durationMs)` (`motion.ts:useCountUp`): tween a figure toward `target`, built on `@vueuse/core`'s `useTransition` + `usePreferredReducedMotion`; **ledger semantics — the tween starts from the previously displayed value** (a recompute amends, it never resets to zero); the first arrival reveals 0 → value; reduced motion renders the final value instantly

## Invariants
- Motion durations come ONLY from the theme tokens via `motionDurationMs` — never a component-local raw duration (single source: `frontend/src/assets/index.css` `@theme static`)
- The reduced-motion probe is `usePreferredReducedMotion` — no hand-rolled `matchMedia('(prefers-reduced-motion: reduce)')` literals anywhere in the frontend. Known violations (code-grounded, to reconcile): `components/ai/ChatMessages.vue:31-33` and `views/ExploreView.vue:143` hand-roll the match
- `BASE_URL` is empty (`api.ts:5`): all requests are same-origin relative; in dev they rely on the Vite proxy `/api` → `http://127.0.0.1:8000` (`frontend/vite.config.ts:server.proxy`), in production on reverse-proxy parity
- Error contract: every function `throw new Error(...)` on `!res.ok` **except** `deleteCopilotSession`, which returns the boolean `res.ok` without throwing (`api.ts:261-266`)
- `streamCopilot` degradation chain (`api.ts:177-245`): non-OK/empty stream body, thrown stream errors, or a stream that ends without a `final_result` all fall back to `askCopilot` and synthesize one `final_result` callback — callers receive a terminal event exactly once
- SSE frames are expected as `data: <JSON>` separated by blank lines with a `[DONE]` sentinel; malformed JSON chunks are `console.warn`-ed and skipped, never fatal (`api.ts:215-228`)
- `types.ts` is type-only: it must not gain runtime exports or it stops being erasable by `vue-tsc` isolated module settings
- `cn` output ordering is `tailwind-merge` semantics: later classes win on conflicting utilities — all `ui/` components rely on `props.class` being passed last

## Side Effects
- Network I/O: every exported `fetch*`/`askCopilot`/`streamCopilot` function performs an HTTP request (see Interface); `streamCopilot` additionally reads the response body incrementally via `res.body.getReader()` (`api.ts:203`)
- Console: `console.warn('Failed to parse SSE event chunk:', ...)` (`api.ts:227`) and `console.warn('[copilot] Stream failed, falling back to non-streaming query:', ...)` (`api.ts:239`)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
