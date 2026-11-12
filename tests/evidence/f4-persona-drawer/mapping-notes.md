# F4 — PersonaDrawer incumbent mapping (captured before swap)

Branch: `feat/f4-persona-drawer` (stacked on `feat/ui-primitives`). Baselines: `baseline-drawer-default-1440.png`, `baseline-drawer-edited-1440.png`.

## Structure and what changed

| Block | Incumbent | Post-swap | Preserved behavior |
|---|---|---|---|
| Preset Selector | `Button` per persona, active = `variant=default` + Check icon, `@click="selectExisting(p)"` | **Unchanged (Buttons)** — presets apply instantly AND close the drawer; a toggle-group item that closes its own dialog would be wrong | instant-apply-on-preset ✓ |
| Skin Type | 5 `Button`s (`variant` by `editedPersona.skin_type === st`) | `ToggleGroup type="single"` bound to `editedPersona.skin_type`; re-click = deselect → undefined → **ignored** (incumbent was a no-op) | local edit until Apply ✓ |
| Target Goals | `Badge` chips, `toggleGoal` splice/push | **Unchanged** — not in F4's task scope | local multi-toggle ✓ |
| Strict exclusions | 3 native `<input type=checkbox>` v-model | 3 `Switch` with `v-model` + native `label for=id` forwarding (click-on-text toggles exactly once) | local edits until Apply ✓ |
| Footer | Cancel / Apply & Recalculate Matches | **Unchanged** | emit contract ✓ |

## Save path (untouched, verified end-to-end)

`applyCustom` → emits `save-custom-persona` → `App.vue handleSaveCustomPersona` → `usePersona.saveCustom` → `POST /api/personas` → success toast / error toast. Live verification: edit skin→dry + fragrance off → Apply → toast "Skin profile saved — matches recalculated." → API shows `custom_uap` with `skin_type: "dry"` → reopening the drawer shows the persisted state.

## ⚠️ Flagged for reviewer decision (spec vs incumbent)

The `persona-controls` spec scenario says: *"Save fails → the drawer surfaces the error and preserves the user's unsaved edits."* The incumbent (and this change, unchanged) **closes the drawer immediately on Apply, before the save resolves** — on failure the error toast appears but the drawer is already closed and the edits are gone. Closing this gap requires holding the drawer open until the save resolves — a save-flow behavior change beyond F4's swap scope. Options for review: (a) correct the spec scenario to match the incumbent, or (b) schedule the drawer-stays-open-on-save change (touches `applyCustom` + `App.vue` handler). Not silently decided here.

## Verification notes

- Switches verified both directions: label-text click (for=id forwarding) and direct switch click each toggle exactly once.
- Skin-type ToggleGroup: selection updates local state; re-click ignored (incumbent no-op).
- Dialog close: reka keeps the content mounted through the close animation (`data-state=closed` → unmount after `animationend`); in the automation pane `animationend` fires late, so short-wait DOM checks falsely read "still open" — full unmount confirmed (`gone: true` on a later read). Same timing on pristine code; not a regression.
- Success-path verified; failure-path not simulated (needs network fault injection against the live backend) — parent's catch → error toast exists in code (`App.vue`).
