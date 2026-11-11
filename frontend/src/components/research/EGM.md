# research

## Overview
Peanut package containing `ResearchCopilot.vue`: the "Formulation Research Copilot" chat interface over the backend's streaming LangGraph agent. Since the Stage 4 rebuild it is a coordinator, not a monolith — message scrolling, prompt input, suggestion chips, sources, workflow plan, and agent trace live in the reusable AI pattern components under `components/ai/` (shadcn-vue AI Elements patterns: Message Scroller, Prompt Input, Suggestion, Sources, Trace, Plan/Task). Multi-turn sessions, SSE stream mapping, HITL clarification cards, and evidence citation inspection remain here. `deleteCopilotSession` is exposed by the API client but has no UI affordance yet.

## Interface
- `ResearchCopilot.vue` (single file component, ~600 lines)
- Props (`ResearchCopilot.vue:defineProps`): `activeProductIds?: number[]`, `personaId?: string` (defaults used internally: `props.personaId || 'uap'`)
- Emits (`ResearchCopilot.vue:defineEmits`): `'view-details'` (product) and `'toggle-compare'` (product), fired from matching-formulation cards
- AI pattern components consumed (all under `@/components/ai/`):
  - `ChatMessages` — owns scroll position; `:stream-tick` bumps on every stream event so new content pins to the bottom unless the user scrolled up (fixes the old never-autoscrolling container)
  - `PromptInput` — auto-growing textarea, Enter-to-send / Shift+Enter newline, busy state
  - `SuggestionChip` — starter prompts only; per-message suggestions come from structured backend fields (`clarification.options`), never from scraping markdown
  - `TaskPlan` — renders the workflow steps from backend `node_update`/final `todo_list` payloads; auto-expands on failure
  - `SourcesList` — citation badges carrying `evidence_id`; emits `inspect`
  - `AgentTrace` — routing decision, dispatch matrix, event timeline, stage latencies from the `trace` payload (`intent_route`, `route_reason`, `activated_agents`/`bypassed_agents` for `search_catalog`, `extract_reviews`, `find_alternatives`, `retrieve_references`, `events[]`, `stage_timings_ms`)
- Markdown pipeline: `renderMarkdown` from `@/lib/markdown` (marked + DOMPurify sanitize) — see Invariants
- Session lifecycle: `onMounted → loadSessions()` (`fetchCopilotSessions` with local fallback), `handleNewChat()` (`createCopilotSession(personaId)` with local-id fallback), `handleSelectSession(sid)` (`fetchCopilotSession` maps stored messages)
- Send pipeline `handleSend(promptText?)`:
  - pushes the user message and a neutral assistant placeholder (`todo_list` = one in-progress "Interpreting..." step) — no client-side intent classification; the workflow plan is the backend's (`node_update` carries `todo_list`, node order constants in `NODE_ORDER` mark prior steps completed)
  - `streamCopilot({ session_id, persona_id, query, product_ids }, callback)`; callback bumps `streamTick`, maps `node_update` stage labels and `final_result` (`answer`, `search.products` → `matching_products`, `review_insights`, `alternatives`, `trace`, `references`/`citations` → citations with `source_kind: 'reference_note'`, `clarification`, `session_title` into the session list)
  - error path writes failure text into the assistant bubble and marks steps `'failed'`
- Citation inspection `inspectCitation(cit)`: `fetchEvidence(cit.id)` with an offline fallback quote; rendered in the verbatim-evidence `Dialog`
- HITL clarification contract: `msg.clarification.options` (`id`, `title`, `description`, `query`) as clickable cards re-sending via `handleSend(opt.query)`; `clarification.allow_custom` reveals the custom input (`submitCustomClarification`)

## Invariants
- `handleSend` is re-entrancy guarded: returns early when `loading` is true or the query is empty; `queryInput` is cleared immediately on send
- Assistant markdown always renders through `renderMarkdown` (`@/lib/markdown`) into `v-html`, which **sanitizes with DOMPurify** — the previous "backend content is trusted" invariant was deliberately flipped in Stage 4: model output can carry prompt-injected markup and is never trusted raw
- Suggestion chips render only structured sources: the curated `samplePrompts` (fresh conversation) and backend `clarification.options`; no regex scraping of assistant markdown (the old `getSuggestions` was deleted together with the client-side intent classifier)
- Workflow steps come from the backend stream only; the client never fabricates task lists from query text
- Inline citations are not rendered because the backend identifies evidence per answer, not per claim; `SourcesList` is the extension point when per-claim evidence ids appear in the stream
- The `sessionId` is client-generated before first server contact and only replaced by a server session after `createCopilotSession` succeeds or a session is selected
- `loading` is toggled in a `try/finally` around `streamCopilot`, so it always resets even on stream failure
- Starter prompt bar renders only while `messages.length <= 2`
- Session list keeps a "Current Session" entry for the active `sessionId` when the server list does not contain it (`loadSessions`)
- Emits are the only path to product UI: the copilot never opens detail modals or mutates comparison state itself

## Side Effects
- Network (all via `@/lib/api`): `fetchCopilotSessions` on mount; `createCopilotSession` on New Chat; `fetchCopilotSession` on session switch; `streamCopilot` SSE stream per send; `fetchEvidence` per citation inspection
- Clipboard: `navigator.clipboard.writeText` in `copyMessage` with a 2000 ms `setTimeout` to reset the copied indicator
