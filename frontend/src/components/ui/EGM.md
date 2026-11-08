# ui

## Overview
The shared UI primitive library for the frontend: ten shadcn-vue style component packages built as thin wrappers around [radix-vue](https://www.radix-vue.com/) headless components, styled with Tailwind CSS and `class-variance-authority`. Each package is a self-contained Peanut (EGM term: the leaf contract of a directory of direct source files) exporting its components from an `index.ts`. This directory contains no direct source files of its own; it is an architectural grouping only.

## Subdirectories & Boundaries
- badge: [./badge/EGM.md](./badge/EGM.md) - `Badge` pill with variants `default|secondary|destructive|outline|verified|source|unknown|negative|mixed` (`Badge.vue:badgeVariants`)
- button: [./button/EGM.md](./button/EGM.md) - `Button` on radix-vue `Primitive` with variants `default|destructive|outline|secondary|ghost|link|evidence` and sizes `default|sm|lg|icon` (`Button.vue:buttonVariants`)
- card: [./card/EGM.md](./card/EGM.md) - `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter` layout family (`index.ts:1-6`)
- collapsible: [./collapsible/EGM.md](./collapsible/EGM.md) - `Collapsible`, `CollapsibleTrigger`, `CollapsibleContent` around radix-vue `CollapsibleRoot`
- dialog: [./dialog/EGM.md](./dialog/EGM.md) - `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter` around radix-vue `DialogRoot` with portal rendering
- input: [./input/EGM.md](./input/EGM.md) - `Input` native `<input>` with `useVModel` (`update:modelValue`) binding
- scroll-area: [./scroll-area/EGM.md](./scroll-area/EGM.md) - `ScrollArea`, `ScrollBar` around radix-vue `ScrollAreaRoot`/`ScrollAreaScrollbar`
- select: [./select/EGM.md](./select/EGM.md) - `Select`, `SelectValue`, `SelectTrigger`, `SelectContent`, `SelectGroup`, `SelectItem`, `SelectLabel` around radix-vue `SelectRoot`
- separator: [./separator/EGM.md](./separator/EGM.md) - `Separator` around radix-vue `SeparatorPrimitive`, defaults `orientation='horizontal'`, `decorative=true`
- tabs: [./tabs/EGM.md](./tabs/EGM.md) - `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` around radix-vue `TabsRoot`

## Cross-Package Invariants
- Every package is a generic shadcn-vue primitive: no app-domain logic and no API calls anywhere under this directory; all stateful behavior (open/close, value, orientation) is owned by the wrapped radix-vue roots
- Components declaring a `class?: HTMLAttributes['class']` prop merge caller styling through the shared `cn` helper from `@/lib/utils` (24 of 33 `.vue` files); the other 9 are pure radix-vue passthroughs with no `class` prop and no `cn` import, relying on Vue attribute fallthrough (`Collapsible.vue`, `CollapsibleContent.vue`, `CollapsibleTrigger.vue`, `Dialog.vue`, `DialogTrigger.vue`, `Select.vue`, `SelectGroup.vue`, `SelectValue.vue`, `Tabs.vue`). Theme tokens (`primary`, `muted`, `accent`, `popover`, `card`, `destructive`, ...) resolve to CSS variables mapped in `frontend/tailwind.config.js:extend.colors`
- `animate-in`/`animate-out`/`animate-collapsible-*` transition classes declared in dialog, select, and collapsible templates require animation keyframes/plugins that are absent (`tailwind.config.js:plugins` is `[]`); these classes currently resolve to no-ops

## Cross-Package Side Effects
- None at this level: components render DOM and delegate behavior to radix-vue; `dialog` and `select` mount portal content outside the app DOM tree via radix-vue `SelectPortal`/`DialogPortal`

## Verification
- Run (from `frontend/`): `npm run build`
