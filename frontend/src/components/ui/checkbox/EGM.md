# checkbox

## Overview
shadcn-vue style checkbox primitive wrapping the reka-ui `CheckboxRoot`/`CheckboxIndicator` family — a two-state (and optional indeterminate) control with a check glyph. Purely presentational; no app-domain logic and no API calls.

Authored from upstream shadcn-vue `unovue/shadcn-vue` commit `d1bf1b3a2d1a824b19f32d7253a28a43797b8253` (`apps/v4/registry/new-york-v4/ui/checkbox`). Adaptations: `cn` imported from `@/lib/utils`; `Check` icon imported from `lucide-vue-next` (upstream uses `@lucide/vue`); `data-slot` attributes omitted to match the project's existing primitive packages.

## Interface
- Exported by `index.ts`: `Checkbox`
- `Checkbox` (`Checkbox.vue`): wraps reka-ui `CheckboxRoot`; props `CheckboxRootProps & { class? }`; emits `CheckboxRootEmits` (`update:checked` family), forwarded via `useForwardPropsEmits`; indicator renders a slot or the default `Check` glyph (`size-3.5`)

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Checked state is owned by reka-ui `CheckboxRoot` (`v-model`/`checked`/`indeterminate`); Space toggles and `data-[state]` styling come from the root
- Disabled state renders non-interactive (cursor-not-allowed + opacity)

## Side Effects
- None
