# Button

## Overview
Generic shadcn-vue style button primitive wrapping the radix-vue `Primitive` element so it can render as any element type (`as`/`asChild`). Purely presentational: variant/size styling via `class-variance-authority`, no app-domain logic and no API calls.

## Interface
- `Button` (exported by `index.ts:1`, re-exporting `./Button.vue`)
- Props (`Button.vue:Props extends PrimitiveProps`): `variant?`, `size?`, `class?`, plus radix-vue `PrimitiveProps` (`as`, `asChild`); `as` defaults to `'button'` (`Button.vue:withDefaults`)
- Variant contract (`Button.vue:buttonVariants`): `default | destructive | outline | secondary | ghost | link | evidence`; default is `default`
- Size contract (`Button.vue:buttonVariants`): `default | sm | lg | icon`; default is `default`
- `evidence` variant (`Button.vue:buttonVariants`): fixed teal color scheme (`bg-[#0e6870]`)
- Renders `Button.vue:template`: `<Primitive :as="as" :as-child="asChild" :class="cn(buttonVariants({ variant, size }), props.class)">` with a default slot

## Invariants
- Generic primitive only: contains no app-domain logic and performs no API calls
- Element rendering is delegated to radix-vue `Primitive`; default rendered element is `<button>` unless callers override `as`/`asChild`
- `variant`/`size` values are limited to the keys declared in `Button.vue:buttonVariants`

## Side Effects
- None

## Verification
- Run (from `frontend/`): `npm run build`
