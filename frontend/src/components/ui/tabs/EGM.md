# Tabs

## Overview
Generic shadcn-vue style tabs primitive wrapping the radix-vue tabs family. Four purely presentational components composed via slots; no app-domain logic and no API calls.

## Interface
- Exported by `index.ts` (lines 1-4): `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent`
- `Tabs` (`Tabs.vue`): wraps radix-vue `TabsRoot`; props `TabsRootProps`, emits `TabsRootEmits`, forwarded via `useForwardPropsEmits` (`Tabs.vue:forwarded`)
- `TabsList` (`TabsList.vue`): wraps radix-vue `TabsList`; props `TabsListProps & { class? }`; styling `inline-flex h-10 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground`
- `TabsTrigger` (`TabsTrigger.vue`): wraps radix-vue `TabsTrigger`; props `TabsTriggerProps & { class? }` forwarded via `useForwardProps` (`TabsTrigger.vue:forwarded`); active-state styling `data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm`
- `TabsContent` (`TabsContent.vue`): wraps radix-vue `TabsContent`; props `TabsContentProps & { class? }`; `value` passed explicitly (`TabsContent.vue:template`); styling `mt-2` with focus ring

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- Active-tab state is owned by radix-vue `TabsRoot`; `TabsTrigger`/`TabsContent` must be used within `Tabs` and paired by matching `value`
- `TabsContent` requires a `value` prop from `TabsContentProps` to bind to its trigger

## Side Effects
- None

## Verification
- Run (from `frontend/`): `npm run build`
