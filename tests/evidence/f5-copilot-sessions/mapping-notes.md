# F5 — Copilot session delete (captured before/after)

Branch: `feat/f5-copilot-session-delete` (off `ui_components`; needs no new primitives). Baseline: `baseline-copilot-sessions-1440.png` — session Select + New Chat only, **no delete affordance**; backend `DELETE /research/copilot/sessions/{id}` existed unused; `deleteCopilotSession()` already in `api.ts`.

## Implementation

- Inline `Delete` affordance (Trash2 outline Button, destructive hover) between the session Select and New Chat — acts on the **currently selected session**; any session becomes current via the Select (spec's "each session offers delete" holds through select-then-delete).
- `vue-sonner` toast confirm: "Delete this copilot session? / The conversation and its stored history will be removed." with a **Delete** action button; dismissing (auto-dismiss ~4 s) sends **nothing** (verified: 0 network requests while pending → after auto-dismiss).
- `handleDeleteSession`: DELETE (404 for never-persisted local placeholders tolerated as deleted) → remove from list → switch to first remaining session (its own history loads — no stale messages) or, when the list empties, fresh `handleNewChat()` state. `toast.success('Session deleted.')` after.

## Verified scenarios (spec `copilot-sessions`)

| Scenario | Evidence |
|---|---|
| Confirmed deletion removes the session (persisted) | New Chat → 10 sessions → confirm → **9 sessions** (API count) |
| Confirmed deletion of an unpersisted placeholder | 404 tolerated → client list updated → switch to first remaining |
| Canceled deletion is a no-op | 0 network requests while toast pending → auto-dismiss |
| Visible session deleted → valid state | switched to remaining session, its own messages render (screenshot `post-swap-after-delete-1440.png`) |
| Background session | affordance acts on the current session only; background deletion = select-then-delete (interpretation documented; per-item buttons would need a list redesign beyond F5 scope) |

## Notes

- Session composable extraction remains out of scope (declared in the proposal's out-of-scope list).
- The current-session placeholder entry ("Current Session") is client-only until a message is sent; deleting it is always safe.
