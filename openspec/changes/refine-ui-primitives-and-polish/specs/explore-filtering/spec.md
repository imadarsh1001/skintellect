# Spec Delta

## Purpose

The Explore screen is the primary browsing surface: users narrow the catalog with quick filter strips and a filter sidebar. This capability owns how those controls behave and the invariant that filter state stays owned by the URL, so any filtered view is shareable and reproducible.

## ADDED Requirements

### Requirement: Domain/category strip and quick-filter chips behave as grouped selections

The domain/category strip and the quick-filter chips SHALL behave as grouped selections with the same single/multi selection semantics they have today: activating a chip toggles or replaces its selection exactly as the current hand-rolled buttons do, and results refresh accordingly.

#### Scenario: Chip activation updates results and URL
- **WHEN** the user activates a quick-filter chip or a domain/category strip item
- **THEN** the product grid refreshes to the filtered result set and the URL reflects the new filter state

#### Scenario: Selection semantics unchanged from incumbent behavior
- **WHEN** the user activates each strip/chip group in the same sequence as before the migration
- **THEN** the resulting filter state and result set match the incumbent behavior for that sequence (no group gains or loses single/multi semantics)

### Requirement: Sidebar filter controls preserve incumbent query behavior

The filter sidebar SHALL present its four native dropdowns as select controls, its option checkboxes as checkboxes, its strict fungal/fragrance exclusion options as switches, its numeric range as a slider, and its price tiers as a grouped selection — all bound to the same query state as today.

#### Scenario: Sidebar control edits the same query state
- **WHEN** the user changes any sidebar control
- **THEN** the active query updates identically to the pre-migration control for the same input, including combination with strip/chip filters

#### Scenario: Strict exclusions are binary
- **WHEN** the user toggles a strict exclusion switch
- **THEN** the exclusion is fully on or fully off with no intermediate state

### Requirement: Filters are reachable on narrow viewports via a sheet

On viewports narrower than the desktop breakpoint, the filter sidebar SHALL be presented inside an off-canvas sheet opened from the Explore screen, sharing the same filter state as the desktop rendering.

#### Scenario: Narrow-viewport filter access
- **WHEN** the user opens Explore below the desktop breakpoint and activates the filter affordance
- **THEN** the filter controls appear in a sheet, edits there update the same query state, and closing the sheet returns focus to the affordance

### Requirement: Filter state remains URL-owned

All filter state SHALL remain owned by the URL as it is today: a URL captured from a filtered view SHALL reproduce the same filtered result set when reopened, and filter edits update the URL.

#### Scenario: Shared URL reproduces the view
- **WHEN** a user opens a URL copied from another user's filtered Explore view
- **THEN** the same filter selections are applied and the same result set is shown
