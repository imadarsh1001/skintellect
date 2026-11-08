# Agents (LangGraph Research Workflow & Copilot)

## Overview
Agentic research subsystem: LangChain-compatible read-only tools (`tools.py`), the authoritative intent classifier and task planner (`intent.py`), the human-in-the-loop clarification engine (`clarification.py`), the LangGraph state-machine research workflow with deterministic fallback (`graph.py`), and the session-persistent Deep Agents copilot (`copilot.py`). `__init__.py` exports the public surface (`search_catalog_tool`, `get_ingredient_graph_tool`, `get_review_insights_tool`, `get_scientific_references_tool`, `get_product_detail_tool`, `ResearchGraphState`, `run_research_graph`, `ResearchCopilotSession`, `get_or_create_copilot_session`).

## Interface
- `[tools.py:search_catalog_tool]`, `[tools.py:get_ingredient_graph_tool]`, `[tools.py:get_review_insights_tool]`, `[tools.py:get_scientific_references_tool]`, `[tools.py:get_product_detail_tool]` - `@tool`-decorated read-only wrappers over catalog and research functions; input models `SearchCatalogInput`, `IngredientGraphInput`, `ReviewInsightsInput`, `ReferenceSearchInput`.
- `[intent.py:classify_and_plan]` - single authoritative intent router returning `[intent.py:IntentRoutePlan]` (`intent_type`, `route_reason`, `activated_agents`, `bypassed_agents`, `todo_list`, `mode`, `confidence`, `intent_dict`); `[intent.py:classify_semantic]` - n-gram cosine routing over `[intent.py:SEMANTIC_ROUTE_ANCHORS]` (threshold 0.25).
- `[clarification.py:is_ambiguous_skincare_inquiry]` - HITL trigger detection; `[clarification.py:generate_clarification_options]` - Tier 1 Gemini structured payload (`task='clarification'`, version `clarification-v1`, 4s timeout) falling back to the offline `[clarification.py:FACET_CLUSTERS]` matrix and `[clarification.py:DEFAULT_FACET]`; `[clarification.py:resolve_shorthand_clarification]` - maps replies like "1", "A", "first one", "serums" onto pending options; contracts `ClarificationOption`, `ClarificationPayload`.
- `[graph.py:run_research_graph]` - executes the compiled LangGraph (or the sequential fallback) inside `run_budget(max_calls=6, max_seconds=120)` and returns answer, search, review insights, alternatives, references, evidence, synthesis, clarification, and a full `trace`; `[graph.py:stream_research_graph]` - generator yielding `node_update` events then `final_result`.
- `[graph.py]` nodes: `[graph.py:node_interpret_intent]`, `[graph.py:node_retrieve_candidates]`, `[graph.py:node_plan_and_retrieve_evidence]`, `[graph.py:node_synthesize_grounded_answer]`; `[graph.py:ResearchGraphState]` (TypedDict); `[graph.py:get_sulfate_science_explanation]` (canned science explainer).
- `[copilot.py:ResearchCopilotSession]` - thread-scoped session (`ask`, `stream_ask`, `plan_task`, `persist_message`, `clear`); `[copilot.py:get_or_create_copilot_session]`, `[copilot.py:create_new_copilot_session]`, `[copilot.py:list_copilot_sessions]`, `[copilot.py:delete_copilot_session]`, `[copilot.py:ensure_copilot_tables]`.

## Invariants
- Tools are read-only by design: `[model_steps.py:choose_plan]`-style planning and `[intent.py]` routing activate only `search_catalog`, `extract_reviews`, `find_alternatives`, `retrieve_references`, `conversation_memory`, `clarification_generator`, or `greeting_handler`; there are no write tools (see `[model_steps.py:choose_plan]` prompt and `[intent.py:classify_and_plan]` dispatch sets).
- `[intent.py:classify_and_plan]` routing order is fixed: pending-clarification shorthand -> conversation memory -> acknowledgment -> general_chat doubt/feedback -> greeting -> explore -> science_qa fast path (suppressed when the query is a buying search) -> review_inquiry -> compare -> HITL clarification -> semantic vector routing (never overriding an explicit category) -> structured search default with contextual category inheritance from the previous user turn.
- `[graph.py:node_plan_and_retrieve_evidence]` falls back to product IDs `[1, 2, 3]` when a review inquiry has no candidate IDs; ceramide questions filter out the `niacinamide-33038007` reference.
- `[graph.py:node_retrieve_candidates]` bypasses catalog search unless `search_catalog` is activated, returning an empty result set; the compiled graph routes via `[graph.py:route_after_intent]` (retrieve_candidates -> plan_and_retrieve_evidence -> synthesize).
- `[graph.py:run_research_graph]` and `[graph.py:stream_research_graph]` degrade gracefully when `langgraph` is not installed (`_compiled_graph is None`): nodes run sequentially in the same order; `trace.mode` is `deterministic_workflow` vs `langgraph_compiled_workflow`.
- `[tools.py]` patches `BaseTool.__call__`/`StructuredTool.__call__` when `langchain_core` is importable; otherwise the local `tool` decorator only stamps `is_tool`/`tool_name`/`tool_doc` on plain functions.
- `[copilot.py:ResearchCopilotSession]` marks every todo task `completed` after a successful turn; a returned `clarification` payload is stored as `pending_clarification` with `original_query` and is resolved on the next turn via `[clarification.py:resolve_shorthand_clarification]`.
- Session title derives from the first user message (truncated to 36 chars) (`[copilot.py:ResearchCopilotSession.ask]`).

## Side Effects
- SQLite writes: `copilot_sessions` and `copilot_messages` (`[copilot.py:persist_message]`, `[copilot.py:create_new_copilot_session]`, `[copilot.py:delete_copilot_session]`, `[copilot.py:clear]`); schema creation via `[copilot.py:ensure_copilot_tables]`. Persistence failures are swallowed and the session falls back to in-memory state.
- Gemini calls: `[clarification.py:generate_clarification_options]` (Tier 1); all graph runs are wrapped in `run_budget(max_calls=6, max_seconds=120)` whose attempt/token events land in `gemini_runs` via `skintellect.gemini`.
- In-memory process state: `[copilot.py:_SESSIONS]` session cache (cold-start recovery reads SQLite), `[intent.py:_VECTORIZED_ANCHORS]` precomputed vectors, `monkeypatched` LangChain `__call__` methods.
- Catalog/DB reads through `catalog.store.get_catalog` and the wrapped research tools; no file I/O and no network calls beyond the Gemini client.

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
  `python -m tests.smoke_agents` (agent/board/CSI smoke checks; documented in `docs/DEVELOPMENT.md`)
