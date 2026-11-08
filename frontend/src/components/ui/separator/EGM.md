# Separator

## Overview
Generic shadcn-vue style separator primitive wrapping the radix-vue `Separator`. A single purely presentational component; no app-domain logic and no API calls.

## Interface
- `Separator` (exported by `index.ts:1`, re-exporting `./Separator.vue`)
- Props (`Separator.vue:withDefaults`): radix-vue `SeparatorProps & { class? }` with `orientation` defaulting to `'horizontal'` and `decorative` defaulting to `true`
- Renders `Separator.vue:template`: radix-vue `SeparatorPrimitive` styled `shrink-0 bg-border` with `h-[1px] w-full` when horizontal and `h-full w-[1px]` when vertical

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- `decorative` defaults to `true`, so by default the element is hidden from the accessibility tree; callers must pass `decorative={false}` for it to be announced as a separator
- Size is derived entirely from `orientation`; callers must provide height/width context via `class` for the separator to be visible in flex layouts

## Side Effects
- None

## Verification
- Run (from `frontend/`): `npm run build`
