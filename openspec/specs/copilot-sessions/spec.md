# copilot-sessions Specification

## Purpose
The research copilot keeps named conversation sessions. This capability owns session lifecycle actions on the client, starting with deletion — the one lifecycle action the backend API already supports but the UI does not yet expose.

## Requirements

### Requirement: Sessions can be deleted through an explicit, confirmed affordance

Each session in the copilot's session list SHALL offer a delete affordance; deletion SHALL require an explicit confirmation step (a toast with a confirm action) before any request is made, and canceling the confirmation SHALL leave the session untouched.

#### Scenario: Confirmed deletion removes the session
- **WHEN** the user activates a session's delete affordance and confirms in the toast
- **THEN** the delete request is sent to the session API and, on success, the session disappears from the session list

#### Scenario: Canceled deletion is a no-op
- **WHEN** the user activates the delete affordance but dismisses or cancels the confirmation toast
- **THEN** no delete request is sent and the session remains in the list unchanged

### Requirement: Deleting a session leaves the copilot in a valid state

After a confirmed deletion, the copilot SHALL remain in a working state: if the deleted session was the one in view, the conversation area transitions to another valid session or an empty new-session state without errors or orphaned references; if it was not in view, the open conversation is unaffected.

#### Scenario: Deleting the visible session
- **WHEN** the user deletes the session currently open in the conversation area
- **THEN** the copilot shows another session or an empty new-session state, with no stale messages from the deleted session

#### Scenario: Deleting a background session
- **WHEN** the user deletes a session that is not currently open
- **THEN** the open conversation continues uninterrupted and the list no longer shows the deleted session
