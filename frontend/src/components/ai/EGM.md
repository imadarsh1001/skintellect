# ai

## Overview
Reusable presentation components implementing the shadcn-vue AI Elements patterns (Message Scroller, Prompt Input, Suggestion, Sources, Trace, Plan/Task) as Vue SFCs over the local `ui` primitives. Authored directly (the shadcn-vue CLI cannot run on this Node build), they carry no app-domain logic and no API calls: they render the payload shapes the copilot stream provides (`CopilotStep`, `CopilotCitation`, `trace`) and delegate interactions upward.

## Subdirectories & Boundaries
- `ChatMessages.vue` — Message Scroller: owns conversation scroll position; `streamTick` prop pins to newest content unless the user scrolled up; exposes `jumpToBottom()`
- `PromptInput.vue` — Prompt Input: auto-growing textarea bound via `modelValue`, Enter-to-send / Shift+Enter newline, `busy` state, emits `submit`
- `SuggestionChip.vue` — Suggestion: one-click prompt chip, emits `select(suggestion)`; content comes from structured fields (curated starters or backend clarification options)
- `SourcesList.vue` — Sources: citation badge row keyed by `evidence_id`, emits `inspect(citation)`; the extension point for future Inline Citation when per-claim evidence ids exist in the stream
- `TaskPlan.vue` — Plan/Task: renders `CopilotStep[]` with progress count; auto-expands on a `'failed'` step
- `AgentTrace.vue` — Trace: routing decision, agent dispatch matrix, event audit timeline (`ScrollArea`), stage latencies; `open` is a `defineModel` so parents control expansion

## Invariants
- No network access, no `@/lib/api` imports, no routing — every interaction is emitted upward
- All inputs are typed payloads from `@/lib/types`; components never parse or scrape model text
- Styling uses only the shared Tailwind tokens (evidence family included) plus `ui` primitives

## Verification
- Run (from `frontend/`): `npm run build`
