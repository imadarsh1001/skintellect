# Spec Delta

## Purpose

Async surfaces spend a large share of their lifetime empty, loading, or failing — and generic spinner-plus-gray-text states are where "AI slop" shows first. This capability owns how empty, loading, and error states present across the app's async surfaces: designed, personality-carrying states that stay within the established identity and always offer a way forward.

## ADDED Requirements

### Requirement: Every async surface has designed empty, loading, and error states

Each async surface — the Explore grid and its product detail modal, the Research view (evidence, review insights, alternatives), the research Copilot, Compare, Study, Progress, and Graph views — SHALL present designed states for empty (nothing to show yet), loading (fetch in flight), and error (request failed) conditions, rather than blank areas, unstyled spinners, or raw error text.

#### Scenario: First visit to an empty surface
- **WHEN** the user reaches a surface with no data yet (e.g., no compare items, no copilot sessions, no results for a filter)
- **THEN** the surface shows its designed empty state with real copy and a suggested next action, not a blank region or generic placeholder

#### Scenario: Loading has a shaped presence
- **WHEN** data is being fetched on any async surface
- **THEN** the loading presentation occupies roughly the content's eventual shape (skeleton or equivalent), so the layout does not jump when data arrives

### Requirement: States carry personality within the established identity

Empty and error states SHALL use real product copy and visual accent consistent with the established design system (semantic tokens, existing type scale) — personality through precision and voice, not stock illustrations or joke text.

#### Scenario: Copy is real, not filler
- **WHEN** any empty or error state renders
- **THEN** its copy describes the actual condition in the product's voice and offers the next step, with no lorem ipsum, "Something went wrong" boilerplate alone, or off-identity visuals

### Requirement: Error states offer recovery

Every error state SHALL provide at least one recovery action (retry the request, clear the failing filter, or navigate to a working alternative), wired to the actual cause of the failure.

#### Scenario: Recovering from a failed fetch
- **WHEN** a data request fails and the error state shows
- **THEN** the user can act on it (e.g., retry succeeds when the backend recovers) without leaving the surface or refreshing the whole app
