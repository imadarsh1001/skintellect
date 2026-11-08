# Collapsible

## Overview
Generic shadcn-vue style collapsible primitive wrapping the radix-vue collapsible family (`CollapsibleRoot`, `CollapsibleTrigger`, `CollapsibleContent`). Provides expand/collapse behavior with CSS animations; no app-domain logic and no API calls.

## Interface
- Exported by `index.ts` (lines 1-3): `Collapsible`, `CollapsibleTrigger`, `CollapsibleContent`
- `Collapsible` (`Collapsible.vue`): wraps radix-vue `CollapsibleRoot`; props `CollapsibleRootProps`, emits `CollapsibleRootEmits`, forwarded via `useForwardPropsEmits` (`Collapsible.vue:forwarded`); scoped slot exposes `{ open }` (`Collapsible.vue:template`)
- `CollapsibleTrigger` (`CollapsibleTrigger.vue`): wraps radix-vue `CollapsibleTrigger`; props `CollapsibleTriggerProps` bound via `v-bind`
- `CollapsibleContent` (`CollapsibleContent.vue`): wraps radix-vue `CollapsibleContent`; props `CollapsibleContentProps`; adds animation classes `data-[state=closed]:animate-collapsible-up` / `data-[state=open]:animate-collapsible-down` (`CollapsibleContent.vue:template`)

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- `Collapsible` is the state owner (radix-vue `CollapsibleRoot`); `Trigger`/`Content` must be used within it to receive state
- The classes `animate-collapsible-up`/`animate-collapsible-down` (`CollapsibleContent.vue:10`) are referenced but not defined by any theme source: `tailwind.config.js:plugins` is `[]` and `src/assets/index.css` declares no such keyframes, so they currently resolve to no-op classes; open/close behavior still works via radix-vue state-driven visibility

## Side Effects
- None (state transitions are local component state managed by radix-vue)

## Verification
- Run (from `frontend/`): `npm run build`
