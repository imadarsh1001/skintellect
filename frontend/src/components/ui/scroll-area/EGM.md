# ScrollArea

## Overview
Generic shadcn-vue style scroll area primitive wrapping the reka-ui scroll area family with an integrated scrollbar. Two purely presentational components; no app-domain logic and no API calls.

## Interface
- Exported by `index.ts` (lines 1-2): `ScrollArea`, `ScrollBar`
- `ScrollArea` (`ScrollArea.vue`): wraps reka-ui `ScrollAreaRoot` + `ScrollAreaViewport` + `ScrollAreaCorner` plus the local `ScrollBar`; props `ScrollAreaRootProps & { class? }` with `type` defaulting to `'hover'` (`ScrollArea.vue:withDefaults`); `class` is stripped from forwarded props (`ScrollArea.vue:delegatedProps`); content provided via default slot inside `ScrollAreaViewport`
- `ScrollBar` (`ScrollBar.vue`): wraps reka-ui `ScrollAreaScrollbar` + `ScrollAreaThumb`; props `ScrollAreaScrollbarProps & { class? }` with `orientation` defaulting to `'vertical'` (`ScrollBar.vue:withDefaults`); orientation-specific sizing (`h-full w-2` vertical / `h-2 flex-col` horizontal, `ScrollBar.vue:template`); thumb styled `rounded-full bg-border`

## Invariants
- Generic primitive only: no app-domain logic and no API calls
- `ScrollArea` always renders one `ScrollBar` (default vertical); a horizontal scrollbar requires callers to render `ScrollBar` explicitly with `orientation="horizontal"`
- `class` is consumed by the wrapper and not forwarded to the underlying reka-ui root (`ScrollArea.vue:delegatedProps`)

## Side Effects
- None

## Verification
- Run (from `frontend/`): `npm run build`
