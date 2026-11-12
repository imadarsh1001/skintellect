# F3 — ProductDetailModal incumbent tab mapping (captured before swap)

Branch: `feat/f3-product-tabs` (base: `ui_components`). Baseline screenshots: `baseline-modal-safety-1440.png` (+ INCI tab below).

## Incumbent tab/panel inventory (all 5 tab references)

| # | Tab value | Label | Icon | Count badge | Panel content root |
|---|---|---|---|---|---|
| 1 | `safety` | Safety & Clinical Fit | `Shield` | — | `div.space-y-5.text-xs` (description, certifications, actives grid, comedogenic analysis, persona alignment) |
| 2 | `ingredients` | Full INCI Ingredients | `FlaskConical` | `(N)` from `ingredients.length || names.length` | `div.space-y-4` (search input + ingredient rows) |
| 3 | `dupes` | Formula Alternatives | `Scale` | `(N)` from `dupesList.length` | `div.space-y-4` (alternatives grid w/ Inspect button) |
| 4 | `reviews` | Reviews & Experiences | `MessageSquare` | `(N)` from `reviews.length` | `div.space-y-4` (skin-type chips + review cards) |
| 5 | `raw` | Raw JSON | `FileCode` | — | `div.space-y-2` (JSON pre) |

## Behavior to preserve (verified against pristine code, lines 46, 66–76, 219–271)

- `activeTab` resets to `'safety'` on every modal open (`watch(props.open)`); `ingredientSearch`/`reviewSkinFilter` reset too.
- `activeTab` was `ref<'safety'|'ingredients'|'dupes'|'reviews'|'raw'>` — widened to `ref<string>` for the primitive's `update:modelValue` typing (panel comparisons unchanged).
- Tab bar: `border-b border-border/60 px-5 flex items-center gap-1 overflow-x-auto bg-card shrink-0`; triggers `py-3 px-3.5 border-b-2 font-bold text-xs`, active = `border-primary text-primary`, inactive = `border-transparent text-muted-foreground hover:text-foreground`. Computed style check: active border bottom-only 1.6px teal (no full box).
- Panels: only active mounted (`v-if`) — reka-ui `TabsContent` unmounts inactive by default (same semantics, no `forceMount`).
- Loader replaces panels while `loading` (stays outside tabs); `detailedProduct` guard wraps panels.
- Pre-existing latent bug fixed in passing: `FlaskConical` was used in the template but never imported (silent "failed to resolve component"); added to the lucide import list.

## Post-swap invariants

- Arrow-key navigation + `role=tablist/tab/tabpanel` ARIA now come from reka-ui (the F3 goal); visual styling preserved via `TabsList`/`TabsTrigger` class overrides (`cn` = clsx + tailwind-merge so overrides win).
- `Space`/`Enter` on a focused trigger selects it (native button activation inside `TabsTrigger`).
