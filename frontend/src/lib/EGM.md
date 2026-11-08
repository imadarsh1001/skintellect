# lib

## Overview
Peanut package holding the frontend's shared infrastructure: the backend REST/SSE API client (`api.ts`), the domain type contracts (`types.ts`), and the Tailwind class merge helper (`utils.ts`). Every component-level network call and cross-component type flows through this package.

## Interface
### `utils.ts`
- `cn(...inputs: ClassValue[])` (`utils.ts:cn`, lines 4-6): `twMerge(clsx(inputs))` from `clsx` + `tailwind-merge`; the single styling merge helper used by all `ui/` primitives

### `types.ts` (type-only module, no runtime code)
- `FormulaStatus` (`types.ts:FormulaStatus`): `'verified_complete' | 'unverified' | 'missing'`
- `Product` (`types.ts:Product`): catalog entity; notable contracts: `ingredients?: Array<{ name: string; [key: string]: any }>`, `names?: string[]` (INCI list), `reviews[]` with ABSA `aspects` (`aspect`, `sentiment: 'positive' | 'negative' | 'neutral'`, `negated`, `span`, lines 27-32), safety flags typed as SQLite-style integer booleans (`fungal_acne_safe?: number`, `fragrance_free?: number`, `alcohol_free?: number`, `oil_free?: number`, lines 40-43), `persona_match` with `match_status: 'match' | 'contraindicated' | 'unknown'` (lines 44-51)
- `SkinPersona` (`types.ts:SkinPersona`): `id`, `name`, `skin_type: 'oily' | 'dry' | 'combination' | 'sensitive' | 'normal'`, `concerns`, `goals`, exclusions `exclude_fungal_acne_triggers`/`exclude_drying_alcohols`/`exclude_fragrance`, `custom_exclusions`
- `PersonaEvaluation` (`types.ts:PersonaEvaluation`): per-product persona result incl. `missing_formula: boolean`
- `IngredientGraphNode` / `IngredientGraphLink` / `IngredientGraphData` (`types.ts:77-94`): graph DTO (`co_occurrence` weight) used by `api.ts` imports; note `components/graph/IngredientGraph.vue` declares its own local `GraphNode`/`GraphLink` shapes and does not use these
- `CopilotStep` (`types.ts:CopilotStep`): `status: 'pending' | 'in_progress' | 'completed' | 'failed'`
- `CopilotToolCall` (`types.ts:CopilotToolCall`): `status: 'executing' | 'done' | 'failed'`
- `CopilotCitation` (`types.ts:CopilotCitation`): `source_kind: 'product' | 'review' | 'reference_note'`
- `ClarificationOption` / `ClarificationPayload` (`types.ts:115-127`): HITL clarification DTO (`needs_clarification`, `options[]`, `allow_custom`)
- `CopilotMessage` (`types.ts:CopilotMessage`): chat message incl. UI-only transient fields `showDebugger`, `showPlan`, `showCustomClarification`, `customClarificationText`, `streamingStage` (lines 142-146)

### `api.ts` (all endpoints relative; `BASE_URL = ''` at `api.ts:3`)
- Types: `ProductFilters` (`api.ts:ProductFilters`, lines 5-22), `ProductsResponse` (`api.ts:ProductsResponse`, lines 24-29)
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

## Invariants
- `BASE_URL` is empty (`api.ts:3`): all requests are same-origin relative; in dev they rely on the Vite proxy `/api` → `http://127.0.0.1:8000` (`frontend/vite.config.ts:server.proxy`), in production on reverse-proxy parity
- Error contract: every function `throw new Error(...)` on `!res.ok` **except** `deleteCopilotSession`, which returns the boolean `res.ok` without throwing (`api.ts:189-194`)
- `streamCopilot` degradation chain (`api.ts:128-172`): non-OK/empty stream body, thrown stream errors, or a stream that ends without a `final_result` all fall back to `askCopilot` and synthesize one `final_result` callback — callers receive a terminal event exactly once
- SSE frames are expected as `data: <JSON>` separated by blank lines with a `[DONE]` sentinel; malformed JSON chunks are `console.warn`-ed and skipped, never fatal (`api.ts:151-159`)
- `types.ts` is type-only: it must not gain runtime exports or it stops being erasable by `vue-tsc` isolated module settings
- `cn` output ordering is `tailwind-merge` semantics: later classes win on conflicting utilities — all `ui/` components rely on `props.class` being passed last

## Side Effects
- Network I/O: every exported `fetch*`/`askCopilot`/`streamCopilot` function performs an HTTP request (see Interface); `streamCopilot` additionally reads the response body incrementally via `res.body.getReader()` (`api.ts:134`)
- Console: `console.warn('Failed to parse SSE event chunk:', ...)` (`api.ts:158`) and `console.warn('Stream failed, falling back to standard copilot ask:', ...)` (`api.ts:168`)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
