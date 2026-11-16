# ui

## Overview
The shared UI primitive library for the frontend: sixteen shadcn-vue style component packages built as thin wrappers around [reka-ui](https://www.reka-ui.com/) headless components, styled with Tailwind CSS and `class-variance-authority`. Each package is a self-contained Peanut (EGM term: the leaf contract of a directory of direct source files) exporting its components from an `index.ts`. This directory contains no direct source files of its own; it is an architectural grouping only.

## Subdirectories & Boundaries
- badge: [./badge/EGM.md](./badge/EGM.md) - `Badge` chip with variants `default|secondary|destructive|outline|verified|source|unknown|negative|mixed` (`Badge.vue:badgeVariants`)
- button: [./button/EGM.md](./button/EGM.md) - `Button` on reka-ui `Primitive` with variants `default|destructive|outline|secondary|ghost|link` and sizes `default|sm|lg|icon` (`Button.vue:buttonVariants`)
- card: [./card/EGM.md](./card/EGM.md) - `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter` layout family (`index.ts:1-6`)
- collapsible: [./collapsible/EGM.md](./collapsible/EGM.md) - `Collapsible`, `CollapsibleTrigger`, `CollapsibleContent` around reka-ui `CollapsibleRoot`
- dialog: [./dialog/EGM.md](./dialog/EGM.md) - `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter` around reka-ui `DialogRoot` with portal rendering
- input: [./input/EGM.md](./input/EGM.md) - `Input` native `<input>` with `useVModel` (`update:modelValue`) binding
- scroll-area: [./scroll-area/EGM.md](./scroll-area/EGM.md) - `ScrollArea`, `ScrollBar` around reka-ui `ScrollAreaRoot`/`ScrollAreaScrollbar`
- select: [./select/EGM.md](./select/EGM.md) - `Select`, `SelectValue`, `SelectTrigger`, `SelectContent`, `SelectGroup`, `SelectItem`, `SelectLabel` around reka-ui `SelectRoot`
- separator: [./separator/EGM.md](./separator/EGM.md) - `Separator` around reka-ui `SeparatorPrimitive`, defaults `orientation='horizontal'`, `decorative=true`
- checkbox: [./checkbox/EGM.md](./checkbox/EGM.md) - `Checkbox` around reka-ui `CheckboxRoot` (`v-model:checked`)
- sheet: [./sheet/EGM.md](./sheet/EGM.md) - `Sheet`, `SheetTrigger`, `SheetContent`, `SheetHeader`, `SheetTitle`, `SheetDescription` around reka-ui `DialogRoot` (side variants), portal rendering
- slider: [./slider/EGM.md](./slider/EGM.md) - `Slider` around reka-ui `SliderRoot`/`SliderTrack`/`SliderRange`/`SliderThumb` (`v-model` carries number[])
- switch: [./switch/EGM.md](./switch/EGM.md) - `Switch` around reka-ui `SwitchRoot`/`SwitchThumb` (`v-model:checked`)
- toggle: [./toggle/EGM.md](./toggle/EGM.md) - `Toggle` around reka-ui `Toggle` with cva `toggleVariants`
- toggle-group: [./toggle-group/EGM.md](./toggle-group/EGM.md) - `ToggleGroup`, `ToggleGroupItem` around reka-ui `ToggleGroupRoot` (single/multiple)
- tabs: [./tabs/EGM.md](./tabs/EGM.md) - `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` around reka-ui `TabsRoot`

## Cross-Package Invariants
- Every package is a generic shadcn-vue primitive: no app-domain logic and no API calls anywhere under this directory; all stateful behavior (open/close, value, orientation) is owned by the wrapped reka-ui roots
- Components declaring a `class?: HTMLAttributes['class']` prop merge caller styling through the shared `cn` helper from `@/lib/utils` (36 of 48 `.vue` files); the other 12 are pure reka-ui passthroughs with no `class` prop and no `cn` import, relying on Vue attribute fallthrough (`Collapsible.vue`, `CollapsibleContent.vue`, `CollapsibleTrigger.vue`, `Dialog.vue`, `DialogTrigger.vue`, `Select.vue`, `SelectGroup.vue`, `SelectValue.vue`, `Tabs.vue`, `Sheet.vue`, `SheetClose.vue`, `SheetTrigger.vue`). Theme tokens (`primary`, `muted`, `accent`, `popover`, `card`, `destructive`, ...) resolve to CSS variables mapped in `frontend/src/assets/index.css` (`@theme inline`)
- `animate-in`/`animate-out`/`animate-collapsible-*` transition classes declared in dialog, select, and collapsible templates depend on `tw-animate-css`, already imported by the Tailwind entry (`src/assets/index.css`)
- Portal motion durations are token-anchored: `DialogContent` and `SheetContent` carry `duration-(--duration-state)` (Sheet also `ease-(--ease-move)`) — no raw `duration-N` values anywhere in this directory, and `toggleVariants` uses the shared `feedback` utility (never a hand-rolled `transition-[...]` list)

## Cross-Package Side Effects
- None at this level: components render DOM and delegate behavior to reka-ui; `dialog` and `select` mount portal content outside the app DOM tree via reka-ui `SelectPortal`/`DialogPortal`

## Verification
- Run (from `frontend/`): `npm run build`
