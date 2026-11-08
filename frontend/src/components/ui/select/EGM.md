# Select

## Overview
Generic shadcn-vue style select primitive wrapping the radix-vue select family. Seven purely presentational components composed via slots; no app-domain logic and no API calls.

## Interface
- Exported by `index.ts` (lines 1-7): `Select`, `SelectValue`, `SelectTrigger`, `SelectContent`, `SelectGroup`, `SelectItem`, `SelectLabel`
- `Select` (`Select.vue`): wraps radix-vue `SelectRoot`; props `SelectRootProps`, emits `SelectRootEmits`, forwarded via `useForwardPropsEmits` (`Select.vue:forwarded`)
- `SelectValue` (`SelectValue.vue`): wraps radix-vue `SelectValue`; props `SelectValueProps`; slotless passthrough
- `SelectTrigger` (`SelectTrigger.vue`): wraps radix-vue `SelectTrigger` + `SelectIcon` with a `ChevronDown` icon from `lucide-vue-next`; props `SelectTriggerProps & { class? }`; styling `flex h-10 w-full ... [&>span]:line-clamp-1`
- `SelectContent` (`SelectContent.vue`): wraps radix-vue `SelectPortal` + `SelectContent` + `SelectViewport`; props `SelectContentProps & { class? }` with `position` defaulting to `'popper'` (`SelectContent.vue:withDefaults`); emits `SelectContentEmits`; `inheritAttrs: false` (`SelectContent.vue:defineOptions`) with `$attrs` merged onto the content element; popper mode sizes the viewport to trigger dimensions via `--radix-select-trigger-height`/`--radix-select-trigger-width`
- `SelectGroup` (`SelectGroup.vue`): wraps radix-vue `SelectGroup`; props `SelectGroupProps`
- `SelectItem` (`SelectItem.vue`): wraps radix-vue `SelectItem` + `SelectItemIndicator` + `SelectItemText` with a `Check` icon from `lucide-vue-next`; props `SelectItemProps & { class? }`; renders a left-side indicator column (`pl-8`) and focus/disabled states
- `SelectLabel` (`SelectLabel.vue`): wraps radix-vue `SelectLabel`; props `SelectLabelProps & { class? }`; styling `py-1.5 pl-8 pr-2 text-sm font-semibold`

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Open/close and value state are owned by radix-vue `SelectRoot`; `Trigger`/`Content`/`Value` must be used within `Select`
- `SelectContent` renders through `SelectPortal` (outside the app DOM tree) and defaults to `position="popper"` (`SelectContent.vue:withDefaults`)
- `animate-in`/`animate-out` transition classes declared in `SelectContent.vue:template` require the tailwindcss-animate plugin, but `tailwind.config.js:plugins` is `[]`; they currently resolve to no-op classes

## Side Effects
- None (DOM portal mounting and keyboard navigation are radix-vue behavior)

## Verification
- Run (from `frontend/`): `npm run build`
