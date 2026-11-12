# slider

## Overview
shadcn-vue style slider primitive wrapping the reka-ui `SliderRoot`/`SliderTrack`/`SliderRange`/`SliderThumb` family — a range input supporting single and multiple thumbs, horizontal or vertical. Purely presentational; no app-domain logic and no API calls.

Authored from upstream shadcn-vue `unovue/shadcn-vue` commit `d1bf1b3a2d1a824b19f32d7253a28a43797b8253` (`apps/v4/registry/new-york-v4/ui/slider`). Adaptations: `cn` imported from `@/lib/utils`; `data-slot` attributes omitted to match the project's existing primitive packages. One upstream quirk kept verbatim: thumb uses `bg-white` (light-theme tokens make this equivalent to `bg-background`; revisit if dark mode ships).

## Interface
- Exported by `index.ts`: `Slider`
- `Slider` (`Slider.vue`): wraps reka-ui `SliderRoot`; props `SliderRootProps & { class? }`; emits `SliderRootEmits` (`update:modelValue`), forwarded via `useForwardPropsEmits`; renders one `SliderThumb` per entry of `modelValue` (multi-thumb via array model); track/range/thumb styling fixed via `data-[orientation]` variants

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Value state is owned by reka-ui `SliderRoot` (`v-model` as `number[]`); arrow-key adjustment, step, min/max, and ARIA value semantics come from the root
- Thumb count always matches the `modelValue` array length

## Side Effects
- None
