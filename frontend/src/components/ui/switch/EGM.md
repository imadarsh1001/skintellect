# switch

## Overview
shadcn-vue style switch primitive wrapping the reka-ui `SwitchRoot`/`SwitchThumb` family — a binary on/off toggle rendered as a track-and-thumb control. Purely presentational; no app-domain logic and no API calls.

Authored from upstream shadcn-vue `unovue/shadcn-vue` commit `d1bf1b3a2d1a824b19f32d7253a28a43797b8253` (`apps/v4/registry/new-york-v4/ui/switch`). Adaptations: `cn` imported from `@/lib/utils`; `data-slot` attributes omitted to match the project's existing primitive packages.

## Interface
- Exported by `index.ts`: `Switch`
- `Switch` (`Switch.vue`): wraps reka-ui `SwitchRoot`; props `SwitchRootProps & { class? }`; emits `SwitchRootEmits` (`update:checked`), forwarded via `useForwardPropsEmits`; thumb slides via `data-[state=checked]:translate-x-[calc(100%-2px)]`; optional `#thumb` slot replaces thumb content

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- On/off state is owned by reka-ui `SwitchRoot` (`v-model`/`checked`); Space toggles, `role='switch'` and state announcement come from the root
- Disabled state renders non-interactive (cursor-not-allowed + opacity)

## Side Effects
- None
