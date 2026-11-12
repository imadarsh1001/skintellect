# sheet

## Overview
shadcn-vue style sheet primitive — a dialog that slides in from a screen edge, wrapping the reka-ui `DialogRoot` family with portal rendering and side-aware slide animations. The generic off-canvas container used for mobile filter panels and drawers. No app-domain logic and no API calls.

Authored from upstream shadcn-vue `unovue/shadcn-vue` commit `d1bf1b3a2d1a824b19f32d7253a28a43797b8253` (`apps/v4/registry/new-york-v4/ui/sheet`). Adaptations: `cn` imported from `@/lib/utils`; `X` close icon imported from `lucide-vue-next` (upstream uses `@lucide/vue`); `data-slot` attributes omitted to match the project's existing primitive packages.

## Interface
- Exported by `index.ts`: `Sheet`, `SheetClose`, `SheetContent`, `SheetDescription`, `SheetFooter`, `SheetHeader`, `SheetTitle`, `SheetTrigger`
- `Sheet` (`Sheet.vue`): wraps reka-ui `DialogRoot`; props `DialogRootProps`, emits `DialogRootEmits`, forwarded via `useForwardPropsEmits` — owns open state (`v-model:open` / `defaultOpen`), focus trap, Escape-to-close
- `SheetTrigger` (`SheetTrigger.vue`): wraps reka-ui `DialogTrigger`, opens the sheet
- `SheetContent` (`SheetContent.vue`): renders `DialogPortal` + `SheetOverlay` + reka-ui `DialogContent`; props extend `DialogContentProps` with `side?: 'top'|'right'|'bottom'|'left'` (default `'right'`); side-specific slide-in/out animation classes; built-in `DialogClose` button (X icon + sr-only label) top-right; `inheritAttrs: false` with `$attrs` merged after forwarded props
- `SheetOverlay` (`SheetOverlay.vue`): reka-ui `DialogOverlay`, fixed backdrop `bg-black/80` with fade animation
- `SheetHeader` / `SheetFooter` (`*.vue`): layout stacks (`flex flex-col gap-1.5 p-4` / `mt-auto … p-4`)
- `SheetTitle` / `SheetDescription` (`*.vue`): reka-ui `DialogTitle`/`DialogDescription` with muted text styling
- `SheetClose` (`SheetClose.vue`): reka-ui `DialogClose` for custom close affordances

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Open state, focus trap, Escape handling, and focus restore are owned by reka-ui `DialogRoot`; content must render through `SheetContent` (portal) to participate in the dialog semantics
- `SheetTitle` must be present inside `SheetContent` for accessible labelling (reka-ui dialog warning otherwise)
- Animation classes depend on `tw-animate-css` (`animate-in`/`animate-out`/`slide-in-from-*`) already imported by the Tailwind entry

## Side Effects
- None (portal rendering via reka-ui `DialogPortal` is DOM-structural, not a network/side effect)
