# Furrow theme kit — reusing this theme on the next project

Everything needed to stand a **new** project up on Furrow in one place. The
canonical spec is Hallmark's `references/themes/furrow.md` (tokens, type,
surfaces, Range, controls, motion, voice, do-nots); this doc is the
battle-tested mapping onto a shadcn-vue + Tailwind v4 app and the patterns
that took real effort to get right here.

## Effort expectations

| Scenario | Effort | Why |
| --- | --- | --- |
| New site, Furrow from day one | ~half a day to first screens | No content-preservation machinery needed: skip baselines/kept-ledger. Scaffold → tokens → primitives → sweep. |
| Redesign an existing light app onto Furrow | 1–2 sessions | Add the structural ledger + interactive-state captures; expect a text-color conversion pass (every accent-as-type site). |
| Redesign a dark app onto Furrow | +the dark→light flip cost | Every hardcoded dark assumption surfaces; audit scrim/shadows/contrast pairs first. |

## 1. Fast path

```
node <hallmark>/scripts/theme.mjs scaffold furrow
```
writes `tokens.css` + `base.css` beside the app stylesheet — **port them into
the project's single token file and discard the scaffold files** (one token
source). The scaffold's names are Furrow's own (`--color-paper`,
`--color-ink`, …); map them onto the app's semantic names (section 2), never
ship a second token source.

## 2. Token mapping (scaffold name → semantic name)

| Furrow scaffold | shadcn semantic | Value (HSL) |
| --- | --- | --- |
| paper | `--background` | `38.2 35.5% 93.9%` |
| paper-2 | `--card`, `--popover`, `--secondary` | `36 100% 99%` |
| paper-3 | `--muted` | `41.3 26.7% 88.2%` |
| ink | `--foreground`, all `*-foreground` | `24 14.3% 6.9%` |
| ink-muted | `--muted-foreground`, `--input` | `25 7.3% 32.2%` |
| rule | `--border` | `41.5 15.3% 83.3%` |
| accent (tangerine) | `--primary` | `16.7 97.1% 59.4%` |
| focus tangerine | `--ring` | `20.6 100% 42.4%` |
| accent-soft | `--accent` | `20.7 96.7% 88.2%` |
| — | `--scrim` | `15 33.3% 2.4%` |

Radius scale stays shadcn-standard (`--radius: 0.625rem`; card 10px =
`rounded-lg`, entry 14px = `rounded-xl`, controls/chips 6px = `rounded-sm`).
Fonts: `@fontsource/red-hat-display` 600 (heads), `red-hat-text` 400/500,
`red-hat-mono` 400/500 (figures only — never labels/chips/heads).

## 3. The moulded key (the theme's signature control)

```css
@utility key-moulded {
  box-shadow:
    inset 0 1px 0 hsl(var(--card) / 0.6),
    inset 0 -1px 0 hsl(var(--foreground) / 0.14),
    0 1px 1px hsl(var(--border));
}
```
Apply to primary/outline/destructive/secondary button variants + the selected
tab; pair with `active:translate-y-px`. Shadows exist ONLY here and under
floating things (menu/dialog/notebook card) — never resting surfaces.

## 4. Verdict/evidence chip family

Five meanings are product truth, colors re-dealt for light manila (all pairs
≥ 4.5:1 on their own badge backgrounds — assert with a contrast test):
verified `#246e3a`/`#d3edd7` (green = in-date), source `#215c78`/`#d2e9f5`
(water blue), unknown `#4d4641`/`#e4e1db` (manila grey), negative
`#90302e`/`#f8e2df` (sienna — the theme ships no red; this is a deliberate
extension), mixed `#554077`/`#e7e1f5` (violet). Score-tier chips may reuse
the scale only if the number carries the meaning (documented exception).

## 5. Patterns that took real effort here (copy, don't rediscover)

- **Exclusive image states, never layered fallbacks**: an `<img>` plus an
  icon absolutely positioned behind it composites through the SVG's
  transparent pixels. Photo-or-placeholder via one state flag
  (`loading | ok | failed`), `@error` → hide img, text/placeholder carries
  the meaning — never a substitute glyph.
- **One icon family** (lucide); scraped asset vocabularies get fetched
  locally (bounded sets: 41 + 53 SVGs ≈ 172 KB) with a sha256 manifest; map
  source URLs → local files by one slug rule mirrored in exactly two places
  (fetcher + `localIconPath`), and cross-reference them in comments.
- **Unidirectional accent rule**: tangerine is a fill with ink on it — the
  primary key, the selected tab, the field band, the focus ring. A full
  retheme of an existing app means converting every accent-as-type site;
  budget a grep pass (`text-primary` minus `-foreground`) before starting.
- **Ledger voice**: never a number without its unit; measured values in mono
  with `tabular-nums`, a step smaller than adjacent text.
- **Census before asset work**: enumerate every external URL family in the
  data (grep the keys), decide fetch/render/proxy/keep-external per family,
  and record the decision in the run's Picks block.

## 6. Verification kit (what proved this implementation)

- `sloplint --render --kept` per route (0 FAIL bar; waive REFLEX on the
  stamp with reasons, never silently).
- A contrast test reading the token file (HSL triplets + hex evidence pairs)
  — see `tests/check_ui_semantics.js` for the format contract.
- A structural kept-ledger when redesigning (`tests/check_ui_ledger.js`)
  recorded AFTER sanctioned wiring changes.
- **Interactive-state captures** (modal open, tray/drawer states) alongside
  route captures — route-at-rest batteries miss dossier surfaces; that miss
  shipped two rethemes of raw-JSON bugs here. Zoom captures at 1.28x.
- Hallmark gotchas: run `gate.mjs`/`sloplint` from the repo root; restart
  Vite after token-file edits (and after `sed -i`, which breaks the watcher);
  `gate.mjs` fingerprints repo-root `src/` only — reset `.taste-skill/build.json`
  to re-verify SPA edits.

## 7. Reference implementations in this repo

- Token file: `frontend/src/assets/index.css` (stamp + :root + @theme +
  `key-moulded` + prose rules)
- Primitives: `frontend/src/components/ui/button/Button.vue` (moulded
  variants), tabs fill treatment in `frontend/src/App.vue`
- Icon helpers: `frontend/src/lib/utils.ts` (`keyActive*`,
  `localIconPath`, `ingredientBenefitIcons`)
- Fetcher: `scripts/fetch_catalog_icons.py`; image proxy:
  `src/skintellect/api/catalog.py` (`get_product_image`) +
  `tests/test_image_proxy.py`
- Landing composition (ruled ledger hero + field band + notebook cards):
  `frontend/src/views/HomeView.vue`
