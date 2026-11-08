# Card

## Overview
Generic shadcn-vue style card primitive: a set of six purely presentational layout components (`Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`) composed via slots. No app-domain logic and no API calls.

## Interface
- Exported by `index.ts` (lines 1-6): `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`
- All six components accept a single prop `class?: HTMLAttributes['class']` (e.g. `Card.vue:defineProps`)
- Element and styling contract per component (each in its own `.vue` template):
  - `Card.vue:template`: `<div>` with `rounded-xl border bg-card text-card-foreground shadow-sm transition-all`
  - `CardHeader.vue:template`: `<div>` with `flex flex-col gap-1.5 p-5`
  - `CardTitle.vue:template`: `<h3>` with `font-semibold leading-none tracking-tight text-foreground text-base`
  - `CardDescription.vue:template`: `<p>` with `text-sm text-muted-foreground leading-relaxed`
  - `CardContent.vue:template`: `<div>` with `p-5 pt-0`
  - `CardFooter.vue:template`: `<div>` with `flex items-center p-5 pt-0`

## Invariants
- Generic primitives only: no app-domain logic and no API calls in any of the six components
- Layout spacing contract: `CardHeader` carries the card's top padding (`p-5`); `CardContent`/`CardFooter` use `pt-0` so only the header insets content from the card edge
- Semantic element contract: title renders as `<h3>`, description as `<p>`; changing these changes document outline semantics

## Side Effects
- None

## Verification
- Run (from `frontend/`): `npm run build`
