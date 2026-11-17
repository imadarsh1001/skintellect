# toggle

## Overview
shadcn-vue style toggle primitive wrapping the reka-ui `Toggle` root — a two-state pressed/unpressed button. Purely presentational; no app-domain logic and no API calls.

Authored from upstream shadcn-vue `unovue/shadcn-vue` commit `d1bf1b3a2d1a824b19f32d7253a28a43797b8253` (`apps/v4/registry/new-york-v4/ui/toggle`). Adaptations: `cn` imported from `@/lib/utils`; `data-slot` attributes omitted to match the project's existing primitive packages; class strings otherwise identical to upstream.

## Interface
- Exported by `index.ts`: `Toggle`, `toggleVariants` (cva), `ToggleVariants` type
- `Toggle` (`Toggle.vue`): wraps reka-ui `Toggle`; props `ToggleProps & { class?, variant?, size? }` with defaults `variant='default'`, `size='default'`, `disabled=false`; emits `ToggleEmits`, forwarded via `useForwardPropsEmits`; styling via `toggleVariants({ variant, size })` merged with `class` (`Toggle.vue`)
- `toggleVariants` (`index.ts`): variants `default|outline`, sizes `default|sm|lg`; handles pressed state (`data-[state=on]`), disabled, and svg sizing; the focus ring comes from the global `:focus-visible` outline rule in `src/assets/index.css` (the variants' base string declares no `focus-visible:` classes)

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Pressed state is owned by reka-ui `Toggle` (`v-model` / `pressed` prop or `defaultPressed`); `toggleVariants` is the single styling source shared with the toggle-group package
- Disabled state renders non-interactive (pointer-events-none + opacity)

## Side Effects
- None
