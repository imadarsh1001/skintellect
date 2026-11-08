# Dialog

## Overview
Generic shadcn-vue style modal dialog primitive wrapping the reka-ui dialog family. Seven purely presentational components composed via slots; no app-domain logic and no API calls.

## Interface
- Exported by `index.ts` (lines 1-7): `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter`
- `Dialog` (`Dialog.vue`): wraps reka-ui `DialogRoot`; props `DialogRootProps`, emits `DialogRootEmits`, forwarded via `useForwardPropsEmits` (`Dialog.vue:forwarded`)
- `DialogTrigger` (`DialogTrigger.vue`): wraps reka-ui `DialogTrigger`; props `DialogTriggerProps`
- `DialogContent` (`DialogContent.vue`): wraps reka-ui `DialogPortal` + `DialogOverlay` + `DialogContent`; props `DialogContentProps & { class? }`, emits `DialogContentEmits` via `useForwardPropsEmits` (`DialogContent.vue:forwarded`); overlay styling `fixed inset-0 z-50 bg-black/50 backdrop-blur-sm` (`DialogContent.vue:template`); panel is centered `fixed left-[50%] top-[50%] ... max-w-lg`; embeds a built-in `DialogClose` with an `X` icon from `lucide-vue-next` and `sr-only` "Close" label (`DialogContent.vue:template`)
- `DialogHeader` (`DialogHeader.vue`): `<div>` `flex flex-col gap-1.5 text-center sm:text-left`; single prop `class?`
- `DialogTitle` (`DialogTitle.vue`): wraps reka-ui `DialogTitle`, styling `text-lg font-semibold leading-none tracking-tight text-foreground`; props `DialogTitleProps & { class? }`
- `DialogDescription` (`DialogDescription.vue`): wraps reka-ui `DialogDescription`, styling `text-sm text-muted-foreground`; props `DialogDescriptionProps & { class? }`
- `DialogFooter` (`DialogFooter.vue`): `<div>` `flex flex-col-reverse sm:flex-row sm:justify-end sm:gap-2`; single prop `class?`

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- `DialogContent` renders through `DialogPortal` (outside the app DOM tree) and always includes its own close button; callers adding custom close controls will coexist with the built-in one
- Open/close state is owned by reka-ui `DialogRoot`; `Trigger`/`Content` must be used within `Dialog`
- `animate-in`/`animate-out` transition classes declared in `DialogContent.vue:template` require the tailwindcss-animate plugin, but `tailwind.config.js:plugins` is `[]`; they currently resolve to no-op classes

## Side Effects
- None (DOM portal mounting is handled by reka-ui `DialogPortal`; focus trapping and body scroll locking are reka-ui `DialogRoot` behavior)

## Verification
- Run (from `frontend/`): `npm run build`
