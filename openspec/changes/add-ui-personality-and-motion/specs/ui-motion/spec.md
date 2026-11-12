# Spec Delta

## Purpose

Motion in the app exists to explain, not decorate. This capability owns how animation behaves app-wide: what motion is allowed to communicate, the consistency of micro-interactions on interactive elements, the mandatory reduced-motion fallback, and the performance envelope that keeps animation from becoming jank.

## ADDED Requirements

### Requirement: Motion serves meaning

Animations SHALL communicate feedback, state change, or spatial continuity — entrance/exit of content, hover/press acknowledgment, transition between views or states — and SHALL NOT run as pure decoration. Interaction feedback SHALL complete within ~200 ms; state and view transitions within ~300 ms; any longer choreography belongs to a view's dealt moment, not routine interactions.

#### Scenario: Feedback on interaction
- **WHEN** the user activates any interactive element (button, toggle, chip, card)
- **THEN** a visible acknowledgment (hover/press state) occurs immediately and completes within ~200 ms

#### Scenario: Transition explains a state change
- **WHEN** a panel, drawer, sheet, or modal opens or closes
- **THEN** its entrance/exit animates in a way that shows where it came from or went, rather than popping in or out instantly

### Requirement: Micro-interactions are consistent across the app

Interactive elements SHALL share one consistent feedback language (same hover/press/focus treatment per element class) implemented through the shared primitives, so screens do not accumulate divergent one-off animation styles.

#### Scenario: Same element, same feedback everywhere
- **WHEN** the user hovers or presses the same element class on different screens
- **THEN** the feedback is identical in kind and timing

### Requirement: Reduced motion is respected

All non-essential animation SHALL be disabled when the user's system requests reduced motion (`prefers-reduced-motion`); essential state changes still occur, instantly.

#### Scenario: Reduced-motion user
- **WHEN** the OS sets prefers-reduced-motion and the user navigates the app
- **THEN** no decorative animation runs, while all state changes, transitions, and feedback still complete correctly

### Requirement: Motion stays within the performance envelope

Animations SHALL animate only compositor-friendly properties (transform, opacity), SHALL NOT cause layout shift, and SHALL NOT drop frames during normal navigation on the supported viewport sizes.

#### Scenario: No layout shift from animation
- **WHEN** entrance or feedback animations run on any view
- **THEN** no content below or around the animating element shifts position as a result
