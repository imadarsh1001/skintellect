# F2 — FilterSidebar incumbent mapping (captured before/after)

Branch: `feat/f2-filter-sidebar` (off `main` at `290f055` — all prior phases merged). Baseline sidebar visible in `tests/evidence/f1-explore-strips/baseline-default-1440.png` (native selects/checkboxes/range) and the ARIA listing in `explore-snapshot-pre.txt`.

## Swap inventory (bindings 1:1 — the two-way `defineModel` contracts and the view's `setFilter` handlers are unchanged)

| Control | Incumbent | Post-swap |
|---|---|---|
| Sort Results | native `<select v-model="sortBy">` | `Select` family (`SelectValue` shows the option label) |
| Category | native `<select>` | `Select` |
| Origin / Heritage | native `<select>` | `Select` |
| Skin Focus Goal | native `<select>` | `Select` |
| Budget Tier | 5 `Button`s grid-cols-5 | `ToggleGroup type="single"` (deselect → `'all'` fallback → param removed) |
| Strict Exclusions ×4 | native checkboxes (fungal/fragrance/oil/pore) | `Switch` ×4 + `label for=id` forwarding — all four live in the "Strict Exclusions" section, so all become switches (consistent with the F4 decision) |
| Min Persona Match | native `<input type=range>` (scalar `minMatch`) | `Slider` with a scalar↔array computed adapter (`minMatchSlider`) |

## Verified

- **Combined URL round-trip** (`?sort_by=rating_desc&country=South%20Korea&goal=barrier&price_tier=%24%24&min_match=60&fungal_safe=true&pore_free=true`): selects show the right labels, switches read checked/unchecked/unchecked/checked, `$$` is the on-item, match label reads 60. Screenshot: `post-swap-sidebar-combined-1440.png`.
- **Mobile Sheet** (`<lg`): desktop aside hidden, `Filters` trigger opens a left-side Sheet containing the same `FilterSidebar` bound to the same query state — editing `fragrance_free` inside the sheet updated the URL live (`?fungal_safe=true&fragrance_free=true`). Screenshot: `post-swap-sheet-390.png`.
- Sheet closes via X (unmount confirmed with an animation-aware wait); desktop rendering restored at 1440. Focus restore to the trigger is reka's dialog behavior — synthetic-click measurement can't verify it (documented, re-checked in the final walk-through).
- The sidebar remains reachable on narrow viewports per spec `explore-filtering` (sheet shares the desktop query state).
