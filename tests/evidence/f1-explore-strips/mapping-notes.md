# F1 — Explore strips/chips incumbent mapping (captured before swap)

Branch: `feat/f1-explore-strips` (stacked on `feat/ui-primitives`). Baselines: `baseline-default-1440.png`, `baseline-filtered-1440.png`.

## Groups and semantics (verified against pristine code + live DOM)

| Group | Items | Selection | Active highlight | Wiring |
|---|---|---|---|---|
| Domain strip | `DOMAINS` = all/skin/hair/body/makeup | single (`setFilter('domain', v)`; clicking active = no-op) | `bg-primary text-primary-foreground shadow-xs` | `filters.domain === domain.value` |
| Category strip | `all` + 6 `CATEGORIES` | single (same pattern) | same, case-insensitive match (`filters.category.toLowerCase() === cat.toLowerCase()`) | `filters.category` |
| Quick chips | fungal_safe / fragrance_free / oil_free | boolean toggle (`setFilter(key, !current)`) | per-chip colors: emerald / blue / purple, white text | `filters.<key>` |
| (out of group) | "Barrier Lipids (Ceramides)" chip | toggles `searchInput` between `''` and `'ceramide'` — a **search-text** control, not a filter | primary | left hand-rolled deliberately (different state mechanism) |

## `setFilter` semantics (from `useExploreQuery.ts:104-113`) — preserved exactly

- Non-default value → URL param set, `page` reset to 1.
- `'all'` / `false` / `0` / default → **param removed** from URL.
- Defaults: `domain='all'`, `category='all'`.

## Round-trip URLs captured at baseline (cards=36/page; pager = page count)

| URL | Pages | Notes |
|---|---|---|
| `` (none) | 70 | default |
| `?domain=skin` | 70 | Skin (Face) active |
| `?domain=skin&category=Moisturizers` | 14 | + category active; sidebar select syncs to Moisturizers |
| `?domain=skin&category=Moisturizers&fungal_safe=true` | 4 | + fungal chip active (emerald) |

## Post-swap wiring (semantics preserved)

- Domain/Category: `ToggleGroup type="single"` bound with `:model-value` + `@update:model-value="(v) => setFilter(key, v ?? 'all')"` — reka's deselect-on-active-click maps to the `'all'` fallback, which removes the URL param exactly like the incumbent's All button. Category highlight stays case-insensitive via `activeCategory` computed (canonical CATEGORIES strings as item values).
- Quick chips: `ToggleGroup type="multiple"`; `activeQuickFilters` computed from the boolean filters; the update handler calls `setFilter(key, active.includes(key))` per key — same URL effects as the old flip.
- `toggleQuickFilter` deleted (orphaned by this change). Item styling overrides carry the incumbent pill/rounded-xl looks per group, including per-chip active colors.
