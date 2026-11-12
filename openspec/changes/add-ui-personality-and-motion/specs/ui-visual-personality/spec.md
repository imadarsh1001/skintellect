# Spec Delta

## Purpose

This capability owns the line between "creative and interesting" and "AI slop" for an Operate-mode product app: personality enters as one intentional, high-craft moment per view — never as ambient decoration, gradient noise, or effects that compete with the user's task.

## ADDED Requirements

### Requirement: Exactly one dealt moment per major view

Each major view — Explore (including its product detail modal), Research, Copilot, Study, Progress, Compare, and Graph — SHALL present exactly one deliberate, distinctive visual/interaction highlight — its "dealt moment" — with depth proportional to the view's traffic (deepest on Explore, product detail, and Copilot; lighter on the rest). Long or compound views MAY carry a second moment; none carries zero.

#### Scenario: Moment exists and is findable
- **WHEN** a reviewer walks any major view on desktop and at 390 px
- **THEN** at least one intentional highlight is present, composed (not a bolted-on effect), and consistent with the view's task flow

#### Scenario: Moments do not compound into noise
- **WHEN** the user moves through several views in one session
- **THEN** each moment reads as a deliberate accent within a quiet whole — the app never presents multiple simultaneous competing effects on one screen

### Requirement: Moments never disrupt task flow

A dealt moment SHALL NOT block interaction, obscure data, trigger on scroll-hijack, or delay time-to-content; on the first task-relevant interaction in a view it yields to the task immediately.

#### Scenario: Task beats moment
- **WHEN** the user interacts with a view's primary task (filtering, opening a product, sending a copilot message) while its moment is playing
- **THEN** the interaction responds immediately with no animation-induced delay or interference

### Requirement: Personality uses semantic tokens, never raw values

All new visual expression (accents, shadows, glows, timing, easing) SHALL be defined as semantic tokens in the Tailwind v4 `@theme` layer and referenced by components; raw hex, raw durations, or ad-hoc keyframes inside components are not permitted, and every new token is documented in `frontend/DESIGN.md` in the same change.

#### Scenario: Token audit passes
- **WHEN** the change's diff is audited for visual-expression values in components
- **THEN** every value resolves to a semantic `@theme` token that `frontend/DESIGN.md` documents

### Requirement: Personality stays within the established identity

New expression SHALL build on the established visual system (existing type scale, existing color semantics, existing corner/radius language) — it MAY add accent, shadow, and motion vocabulary; it SHALL NOT introduce new font families, replace the palette identity, or re-architect layouts.

#### Scenario: Identity preserved alongside personality
- **WHEN** the personality changes land and are compared against pre-change baselines
- **THEN** the app is recognizably the same product — same type system, same color semantics, same layout structure — with added expressiveness, not a different-looking app

### Requirement: Personality direction is grounded in the product's audience, not agent taste

Every dealt moment and every state's copy SHALL trace to a documented user need or persona dimension of the product (derived from the product context and the persona feature — e.g. skin types, goals, strict exclusions), recorded in an audience & voice brief before direction is picked. A moment or state that cannot be traced to a user need SHALL be rejected, however visually appealing it is.

#### Scenario: Moment has a user-need trace
- **WHEN** a dealt moment or state copy is reviewed
- **THEN** it references the audience brief entry it serves (e.g. a match-score reveal serving the personalization promise, an evidence-span highlight serving the explainability promise, filtered-empty copy that explains the strict exclusion)

#### Scenario: Untraceable flourish is rejected
- **WHEN** a proposed moment or copy cannot be traced to any documented user need or persona dimension
- **THEN** it is recorded as deferred and not implemented
