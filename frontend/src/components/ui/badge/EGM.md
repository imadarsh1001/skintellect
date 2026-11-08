# Badge

## Overview
Generic shadcn-vue style badge primitive. A purely presentational labeled pill rendered as a styled `<div>` with a default slot; no app-domain logic and no API calls. Variant styling is defined via `class-variance-authority`.

## Interface
- `Badge` (exported by `index.ts:1`, re-exporting `./Badge.vue`)
- Props (`Badge.vue:Props`): `variant?: BadgeVariants['variant']`, `class?: HTMLAttributes['class']`
- Variant contract (`Badge.vue:badgeVariants`): `default | secondary | destructive | outline | verified | source | unknown | negative | mixed`; default variant is `default` (`Badge.vue:defaultVariants`)
- Domain-styled variants (`Badge.vue:badgeVariants`): `verified` (teal `#12635a`), `source` (blue `#245ba9`), `unknown` (amber `#805309`), `negative` (red `#a63244`), `mixed` (purple `#6843a8`)
- Renders `Badge.vue:template`: `<div :class="cn(badgeVariants({ variant }), props.class)">` with a default slot

## Invariants
- Generic primitive only: contains no app-domain logic and performs no API calls; all app meaning comes from the slot content and the `variant` chosen by callers
- Renders a plain `<div>` (not a reka-ui `Primitive`); slot content is unstyled by this component
- `variant` values are limited to the keys declared in `Badge.vue:badgeVariants`; an omitted `variant` falls back to `default` via `defaultVariants`

## Side Effects
- None

## Verification
- Run (from `frontend/`): `npm run build`
