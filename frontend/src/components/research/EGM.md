# research

## Overview
Peanut package containing `ResearchCopilot.vue`: the "Formulation Research Copilot" chat interface over the backend's streaming LangGraph agent. It handles multi-turn sessions, SSE streaming with staged progress, HITL clarification cards, evidence citation inspection, and an agent-trace debugger drawer. This is the frontend's heaviest component (1078 lines) and the primary consumer of the `@/lib/api` copilot endpoints.

## Interface
- `ResearchCopilot.vue` (single file component, 1078 lines)
- Props (`ResearchCopilot.vue:defineProps`, lines 130-133): `activeProductIds?: number[]`, `personaId?: string` (defaults used internally: `props.personaId || 'uap'` at lines 200 and 350)
- Emits (`ResearchCopilot.vue:defineEmits`): `'view-details'` (product) and `'toggle-compare'` (product), fired from matching-formulation cards (lines 732, 739)
- API dependencies (`ResearchCopilot.vue:4-12`, imports from `@/lib/api`): `streamCopilot`, `fetchEvidence`, `fetchCopilotSessions`, `createCopilotSession`, `fetchCopilotSession` are invoked; `askCopilot` and `deleteCopilotSession` are imported (lines 5, 11) but never called
- Markdown pipeline: `marked.setOptions({ gfm: true, breaks: true })` (`ResearchCopilot.vue:38-41`); `renderMarkdown(content)` (`ResearchCopilot.vue:renderMarkdown`, lines 43-50) returns raw content unchanged on parse failure
- `getSuggestions(content, role)` (`ResearchCopilot.vue:getSuggestions`, lines 52-101): extracts prompt-suggestion strings matching regex `/(?:Try\s+)?[\*"]+([A-Z][^\n\*\"]{8,95}\??)[\*"]+/g` filtered to Find/Compare/Explain/What/How/Show/... prefixes; falls back to keyword-keyed static lists (ceramide/barrier, cleanser/fungal)
- Session state (`ResearchCopilot.vue:137-141`): `sessionId` client-generated as `'session_' + Math.random().toString(36).substring(2, 9)`, `sessions`, `queryInput`, `loading`, `copiedMsgId`; `messages` seeded with a hardcoded welcome assistant message (lines 155-163)
- Session lifecycle:
  - `onMounted` → `loadSessions()` (`ResearchCopilot.vue:loadSessions`, lines 182-196): `fetchCopilotSessions()`; on empty/error falls back to a local-only "Current Session" entry
  - `handleNewChat()` (`ResearchCopilot.vue:handleNewChat`, lines 198-224): `createCopilotSession(props.personaId || 'uap')`; on failure regenerates a local `sessionId` and resets messages
  - `handleSelectSession(sid)` (`ResearchCopilot.vue:handleSelectSession`, lines 226-251): `fetchCopilotSession(sid)` maps stored messages into the local shape; `console.error` on failure
- Send pipeline `handleSend(promptText?)` (`ResearchCopilot.vue:handleSend`, lines 275-440):
  - Intent classification regexes (lines 294-298): `isGreeting`, `isExplore`, `isCompare`, `isScience`, `isChat`
  - Builds staged `initialTasks` todo lists per intent (lines 300-326) and pushes an assistant placeholder message with `streamingStage` + `todo_list`
  - Calls `streamCopilot({ session_id, persona_id, query, product_ids }, callback)` (lines 347-353)
  - Callback handles SSE `event.event === 'node_update'` for node names `interpret_intent`, `retrieve_candidates`, `plan_and_retrieve_evidence`, `synthesize_grounded_answer` (lines 358-387) and `'final_result'` (lines 388-428) which maps `res.answer`, `res.search.products` → `matching_products` (capped at 4 cards in template), `res.review_insights`, `res.alternatives`, `res.trace.tools` → `tool_calls`, `res.references`/`res.citations` → citations with `source_kind: 'reference_note'`, `res.clarification`, and `res.session_title`
  - Error path (lines 431-436): writes failure text into the assistant bubble and marks todo statuses `'failed'`
- Citation inspection `inspectCitation(cit)` (`ResearchCopilot.vue:inspectCitation`, lines 442-453): `fetchEvidence(cit.id)`; fallback `{ quote: 'Source excerpt verification unavailable offline.' }` on failure
- Agent trace contract (template lines 830-1000): reads `msg.trace.intent_route`, `route_reason`, `agents_summary`, `activated_agents`/`bypassed_agents` (via `isAgentActive`, `ResearchCopilot.vue:isAgentActive`, lines 253-256, for agent names `search_catalog`, `extract_reviews`, `find_alternatives`, `retrieve_references`), `events[]` (`stage`, `action`, `reason`, `products_curated`, `candidates_found`, `timestamp`), and `stage_timings_ms` (`interpret`, `search`, `evidence`, `synthesis`, `elapsed_ms`)
- HITL clarification contract (template lines 618-694): renders `msg.clarification.options` (`id`, `title`, `description`, `query`) as clickable cards that re-send via `handleSend(opt.query)`; `clarification.allow_custom` reveals a custom input (`submitCustomClarification`, `ResearchCopilot.vue:submitCustomClarification`, lines 268-273)

## Invariants
- `handleSend` is re-entrancy guarded: returns early when `loading` is true or the query is empty (`ResearchCopilot.vue:277`); `queryInput` is cleared immediately on send
- Assistant responses always render through `renderMarkdown` into `v-html` (line 599); markdown is not sanitized by this component, so backend content is trusted input
- The `sessionId` is client-generated before first server contact and only replaced by a server session after `createCopilotSession` succeeds or a session is selected
- `loading` is toggled in a `try/finally` around `streamCopilot`, so it always resets even on stream failure
- Sample prompt bar renders only while `messages.length <= 2` (line 1010); suggestion chips on assistant bubbles come from `getSuggestions` and re-enter `handleSend`
- Session list keeps a "Current Session" entry for the active `sessionId` when the server list does not contain it (`loadSessions`)
- Emits are the only path to product UI: the copilot never opens detail modals or mutates comparison state itself

## Side Effects
- Network (all via `@/lib/api`): `fetchCopilotSessions` on mount; `createCopilotSession` on New Chat; `fetchCopilotSession` on session switch; `streamCopilot` SSE stream per send; `fetchEvidence` per citation inspection
- Clipboard: `navigator.clipboard.writeText` in `copyMessage` (`ResearchCopilot.vue:copyMessage`, lines 143-153) with a 2000 ms `setTimeout` to reset the copied indicator
- DOM injection: assistant markdown rendered with `v-html` (line 599)
- External navigation: citation modal anchor opens `activeCitation.url` in a new tab with `target="_blank" rel="noopener noreferrer"` (lines 1062-1073)
- Console: `console.error` in `copyMessage`/`handleNewChat`/`handleSelectSession` failure paths (lines 151, 213, 249)

## Verification
- Run (from `frontend/`): `npm run build`; from repo root also `node tests/check_ui_semantics.js`
