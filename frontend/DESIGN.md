---
name: Skintellect Frontend
description: Explainable cosmetic formulation intelligence — Operate-mode ledger over shadcn-vue + reka-ui (Furrow theme)
colors:
  background: "hsl(38.2 35.5% 93.9%)"
  foreground: "hsl(24 14.3% 6.9%)"
  card: "hsl(36 100% 99%)"
  muted: "hsl(41.3 26.7% 88.2%)"
  muted-foreground: "hsl(25 7.3% 32.2%)"
  primary: "hsl(16.7 97.1% 59.4%)"
  primary-foreground: "hsl(24 14.3% 6.9%)"
  secondary: "hsl(36 100% 99%)"
  accent: "hsl(20.7 96.7% 88.2%)"
  destructive: "hsl(0.5 53.6% 45.7%)"
  border: "hsl(41.5 15.3% 83.3%)"
  input: "hsl(25 7.3% 32.2%)"
  ring: "hsl(20.6 100% 42.4%)"
  scrim: "hsl(15 33.3% 2.4%)"
  evidence-verified: "#246e3a"
  evidence-verified-bg: "#d3edd7"
  evidence-source: "#215c78"
  evidence-source-bg: "#d2e9f5"
  evidence-unknown: "#4d4641"
  evidence-unknown-bg: "#e4e1db"
  evidence-negative: "#90302e"
  evidence-negative-bg: "#f8e2df"
  evidence-mixed: "#554077"
  evidence-mixed-bg: "#e7e1f5"
typography:
  body:
    fontFamily: "Red Hat Text 400/500 (body and labels), Red Hat Display 600 (heads), Red Hat Mono for what the ledger measured"
    fontSize: "0.75rem–0.875rem (data); 16px floor for running prose; functional text 11px floor"
    fontWeight: "400 body, 500 row titles/labels/controls, 600 heads, 700 only for markdown strong"
  display:
    fontFamily: "Red Hat Display 600"
    fontSize: "1.25rem–1.875rem"
    letterSpacing: "-0.035em (h1/h2), -0.015em (h3/h4)"
rounded:
  card: "0.625rem (10px) — --radius-lg"
  entry: "0.875rem (14px) — --radius-xl (notebook cards, the field band)"
  control: "0.375rem (6px) — --radius-sm (moulded keys, pills, count bubbles)"
  chip: "4px (rounded-[4px])"
  pill: "rounded-full only where the object is physically round (switch tracks, avatars)"
spacing:
  section-gap: "1.25rem (gap-5); the landing: gap-12 sm:gap-16"
  card-padding: "1rem–1.5rem (p-4 / p-6)"
  control-gap: "0.375rem (gap-1.5) — 0.5rem (gap-2)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.control}"
    shadow: "key-moulded: lit inset top edge, shaded inset bottom, 1px key shadow; active sinks 1px (active:translate-y-px)"
    hover: "bg-primary/90 (one color step, no lift)"
  button-outline:
    backgroundColor: "{colors.card}"
    textColor: "{colors.foreground}"
    border: "1px {colors.border} — the white key with a rule border and the same lit edge"
  badge-verified:
    backgroundColor: "{colors.evidence-verified-bg}"
    textColor: "{colors.evidence-verified}"
    rounded: "{rounded.chip}"
  card-surface:
    backgroundColor: "{colors.card}"
    textColor: "{colors.card-foreground}"
    border: "1px {colors.border} — hairline panel; resting surfaces carry no shadow"
  notebook-card:
    backgroundColor: "{colors.card}"
    border: "1px ink ring (border-foreground/70)"
    shadow: "var(--shadow-card) — floating, sanctioned"
    rounded: "{rounded.entry}"
  focus:
    outline: "2px solid {colors.ring}, offset 2px, instant (global :focus-visible)"
---

# Skintellect Frontend — Design System

## Overview

Operate-mode ledger UI for an evidence-first skincare formulation tool, dealt on Hallmark's **Furrow** theme (by request). The metaphor: a working record kept on the land — warm manila paper in three lightness steps, near-black ink rules, one **tangerine signal** (ear tag and baler twine: a fill with ink on it, never type), and **green for what is in date** (the verified verdict). The voice is a ledger's: plain and unit-bearing, never a number without its unit. Verdict-colored evidence chips are the visual language; every pair holds ≥ 4.5:1 on its own badge background (asserted by `tests/check_ui_semantics.js`). Eight routes: `/` (landing home), `/explore` (catalog), `/compare`, `/graph`, `/copilot`, `/research`, `/study`, `/progress`.

## Colors

All semantic colors resolve through Tailwind v4 `@theme inline` → CSS variables in `assets/index.css` (the single token file; `:root` IS the light theme — no `.dark` class is applied). Never raw palette classes (emerald/blue/slate…) or hexes in components; the only sanctioned hexes are the evidence family. Furrow's scaffold token names map onto the project's semantic names (paper/card/muted → background/card/muted, ink → foreground, rule → border, accent-soft → accent) — one token source. Verdict semantics (product truth, re-dealt for light manila): **verified** (green, what is in date) = full verified INCI; **source** (water blue) = attributed source; **unknown** (manila grey) = no reading yet; **negative** (sienna — the product's own fifth-verdict extension; Furrow ships no red) = contraindication/flag; **mixed** (violet) = conflicting evidence. Class strings for badge variants live in `@/lib/evidence`.

## Typography

Red Hat Display 600 for heads (sentence case, `text-wrap: balance`, tracking −0.035em on h1/h2, −0.015em on h3/h4); Red Hat Text 400 body, 500 for row titles, labels, chips and controls; Red Hat Mono 400/500 for what the ledger measured — scores with units, INCI, IDs, timestamps, counts, doses — always with `tabular-nums slashed-zero`, a step smaller than the text beside it. Mono-as-material only: never mono on a label, chip, head or button. Labels, captions, table heads, chips, nav links: body face a step smaller, sentence case, untracked — never tracked caps, never an eyebrow. Emphasis comes from weight and the tangerine fill, never from gradient text.

## Layout

Landing (`/`) = the ruled ledger hero (headline, one sentence, two moulded CTAs, the tangerine field band of live figures) → "The book as an index" (ink rule over three live rows) → four working surfaces as notebook cards. Explore (`/explore`) = strips (domain, category, quick chips) → hero band (stat row with hairline-separated stats + context) → sidebar (w-80, lg+) + card grid (36/page); below `lg` the sidebar lives in a left-side Sheet sharing the same query state. Spacing rhythm: gap-5 between page sections, gap-6 between sidebar and grid, gap-1.5–2 inside control rows. The container is capped (max-w-7xl) and centered.

## Elevation & Depth

Depth by lightness first: ground (`--background` 93.9%), sheet one step up (`--card` 99%), wells one step down (`--muted` 88.2%), the tangerine-soft well (`--accent` 88.2%) for hover and selection. Every surface separates with 1px `--border` hairlines; `--input` (the muted ink) marks field edges. Shadows exist ONLY under floating things — menus, dialogs, sheets, notebook cards — via `--shadow-card` and `--shadow-lift`; resting surfaces never carry a shadow. Portals (dialog/sheet/select) float on the `--scrim` overlay — the deepest ink, no glass, no backdrop-blur.

## Shapes

Radius: cards 10px (`--radius-lg`), entries/notebook cards 14px (`--radius-xl`), controls and pills 6px (`--radius-sm`), chips 4px (`rounded-[4px]`); `rounded-full` only where the object is physically round (switch tracks, avatars). One radius per nesting level, concentric.

## Components

16 primitive packages under `frontend/src/components/ui/` (badge, button, card, checkbox, collapsible, dialog, input, scroll-area, select, separator, sheet, slider, switch, tabs, toggle, toggle-group), each an EGM-contracted thin wrapper over reka-ui with cva variants; composed into domain components (`components/explore|research|ai|compare|graph/`). One filled primary (tangerine) per screen; secondaries are the white key with a 1px rule border; ghost actions neutral-hover on `--secondary`. Keys are moulded (`key-moulded`): a lit inset top edge, a shaded inset bottom, a 1px key shadow; active sinks 1px (`active:translate-y-px`). The selected tab is a tangerine fill with ink text. Focus is one language: the global `:focus-visible` 2px tangerine outline, instant. Buttons carry `active:opacity-80` alongside the sink. A routed view owns the page's single `h1`; the header brand wordmark is a paragraph.

## Do's and Don'ts

- **Do** express every verdict through evidence tokens; **don't** invent hexes or use Tailwind default palette colors (emerald/slate/indigo…).
- **Do** keep the tangerine contract: it is a FILL with ink on it (the primary key, the selected tab, the field band, the focus ring); **don't** ever set tangerine as type or as an icon color on paper — ink carries type.
- **Do** keep verdict green for what is verified (in date); **don't** borrow it for tier tags, decoration, or syntax highlighting. The "% Persona Fit" chips are the one sanctioned exception: they are a score scale (the number carries the meaning, green/blue mark the ≥90/≥70 tiers), not a provenance verdict — verdict chips always sit next to a shield/help icon, fit chips next to a percentage.
- **Do** set measured values (scores, counts, INCI, timestamps) in the mono face with tabular numerals and their units; **don't** put mono on labels, heads, or buttons, and never render a number without its unit.
- **Do** keep interaction semantics from reka-ui; **don't** re-implement tabs/checkboxes/toggles with divs and click handlers.
- **Don't** animate beyond transform/opacity color-steps at micro durations; motion is state feedback, not decoration. Every animation collapses under `prefers-reduced-motion`.
- **Don't** add emoji as icons (lucide is the icon family; emoji survive only inside chat copy as content), tracked-caps labels, middle-dot meta strings, or per-card hover animations.
- **Don't** put a shadow on a resting surface, blur behind a portal, or stack a gradient; elevation is a hairline, a lightness step, or the sanctioned floating-key shadow.
- **Don't** hardcode figures: the landing's stats and rows are live from the same API Explore uses, and a failed fetch leaves the band off the page rather than render an invented number.
