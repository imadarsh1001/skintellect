# toggle-group

## Overview
shadcn-vue style toggle-group primitive wrapping the reka-ui `ToggleGroupRoot`/`ToggleGroupItem` family — a group of related toggle buttons (single via `type='single'`, multiple via `type='multiple'`). Items inherit variant/size/spacing from the group through provide/inject. Purely presentational; no app-domain logic and no API calls.

Authored from upstream shadcn-vue `unovue/shadcn-vue` commit `d1bf1b3a2d1a824b19f32d7253a28a43797b8253` (`apps/v4/registry/new-york-v4/ui/toggle-group`). Adaptations: `cn` imported from `@/lib/utils`; `toggleVariants` imported from the sibling package `@/components/ui/toggle` (single styling source, no duplication); `data-slot` attributes omitted to match the project's existing primitive packages.

## Interface
- Exported by `index.ts`: `ToggleGroup`, `ToggleGroupItem`
- `ToggleGroup` (`ToggleGroup.vue`): wraps reka-ui `ToggleGroupRoot`; props `ToggleGroupRootProps & { class?, variant?, size?, spacing? }` (`spacing` default `0`); emits `ToggleGroupRootEmits` via `useForwardPropsEmits`; provides `toggleGroup` context (variant/size/spacing) to items; root renders `data-size`/`data-variant`/`data-spacing` and the `--gap` CSS var
- `ToggleGroupItem` (`ToggleGroupItem.vue`): wraps reka-ui `ToggleGroupItem`; props `ToggleGroupItemProps & { class?, variant?, size? }`; injects group context, falling back to its own props; spacing-aware edge rounding (`data-[spacing=0]` joined/separated looks)

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Selection state is owned by reka-ui `ToggleGroupRoot` (`v-model` on the group, `value` on items); arrow-key movement inside the group comes from the root (roving focus)
- `ToggleGroupItem` must be used within `ToggleGroup` to receive context; without it, item-level props apply
- Styling always resolves through `toggleVariants` from the `toggle` package — never re-declared here

## Side Effects
- None
