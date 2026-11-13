# ui-primitives Specification

## Purpose
The shared UI control library is the single source of interactive controls the frontend composes. This capability owns the contract for the six control packages added by this change (toggle group with its underlying toggle item, checkbox, switch, slider, sheet) so screens stop re-implementing these behaviors by hand and inherit consistent keyboard, ARIA, and styling conventions.

## Requirements

### Requirement: Shared control packages exist and are the only source of these controls

The library SHALL export the missing control packages — toggle group (including its single toggle item), checkbox, switch, slider, and sheet — from the same import surface as the existing control packages, and screens SHALL use these packages instead of hand-rolled equivalent markup.

#### Scenario: Screen composes a control from the library
- **WHEN** any screen needs a checkbox, switch, slider, grouped toggle buttons, or an off-canvas panel
- **THEN** it imports that control from the shared library rather than declaring native or hand-styled equivalents inline

#### Scenario: No duplicate implementations remain in migrated screens
- **WHEN** the migration passes over ExploreView, FilterSidebar, ProductDetailModal, and PersonaDrawer complete
- **THEN** the hand-rolled strip/chip/tab/checkbox markup those screens used previously is removed, not left alongside the library controls

### Requirement: Controls expose consistent variants, sizes, and disabled states

Each new control package SHALL follow the library's established variant/size conventions and the project's semantic color tokens, and SHALL render a disabled state that is visually distinct and non-interactive.

#### Scenario: Disabled control
- **WHEN** a control renders with its disabled state set
- **THEN** it is visually distinct from enabled controls and activating it (pointer or keyboard) produces no state change

### Requirement: Controls provide native keyboard and screen-reader semantics

Each control SHALL provide the interaction semantics of its native equivalent through the headless layer it wraps: grouped toggle buttons support arrow-key movement within the group and expose their pressed state; checkboxes toggle with Space and expose checked state; switches expose their on/off role and state; sliders support arrow-key value adjustment; the sheet traps focus while open, closes on Escape, and restores focus on close.

#### Scenario: Keyboard-only user operates a migrated screen
- **WHEN** a keyboard-only user reaches migrated controls on Explore, the filter sidebar, the product detail modal, or the persona drawer
- **THEN** every control is reachable and operable by keyboard alone, and screen readers announce each control's role and current state

#### Scenario: Sheet dismisses without a pointer
- **WHEN** the mobile filter sheet is open and the user presses Escape or moves focus out of the sheet
- **THEN** the sheet closes and focus returns to the trigger that opened it

### Requirement: Each control package carries its own contract document

Every new control package directory SHALL contain an `EGM.md` contract (overview, exported components, boundaries) in the same form as the existing control packages.

#### Scenario: Reviewer audits a new package
- **WHEN** a reviewer opens any newly added control package directory
- **THEN** an `EGM.md` is present whose exports match the package's `index.ts`
