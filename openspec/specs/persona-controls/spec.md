# persona-controls Specification

## Purpose
The persona drawer lets users edit their persona attributes and apply skin-type presets that re-score recommendations. This capability owns the drawer's control behavior and its save semantics.

## Requirements

### Requirement: Persona attribute controls bind to persona state

The persona drawer's attribute toggles SHALL be presented as checkboxes (standard on/off attributes) and switches (strict exclusion attributes), each bound to the same persona state as today so changing a control updates the active persona exactly as the incumbent native controls did.

#### Scenario: Attribute change updates persona
- **WHEN** the user toggles an attribute checkbox or strict-exclusion switch in the drawer
- **THEN** the persona state updates exactly as it did with the incumbent native controls

### Requirement: Skin-type presets form an exclusive group with instant apply

The skin-type presets SHALL be presented as an exclusive grouped selection where selecting a preset instantly applies it to the persona, preserving the incumbent instant-apply-on-preset behavior.

#### Scenario: Preset selection applies immediately
- **WHEN** the user selects a skin-type preset
- **THEN** the preset becomes the group's single selection and its values apply to the persona immediately, without a separate confirm step

### Requirement: Persona save persists and reports failure

Saving the persona SHALL persist it via the persona save endpoint (`POST /api/personas`) as today. On success the app SHALL confirm the save (toast) and the saved persona SHALL become the active one. On failure the app SHALL surface an error indication (toast) and the previously active persona SHALL remain in effect. The drawer closes on Apply before the save resolves (incumbent behavior, confirmed 2026-11-13): it does not promise to keep unsaved edits visible after a failed save.

#### Scenario: Save succeeds
- **WHEN** the user saves the persona and the endpoint accepts the request
- **THEN** a confirmation toast shows, the saved persona becomes active, and it persists across reloads

#### Scenario: Save fails
- **WHEN** the save request fails (network or server error)
- **THEN** an error toast shows and the previously active persona remains in effect
