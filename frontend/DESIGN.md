---
name: Skintellect Frontend
description: Explainable cosmetic formulation intelligence — Operate-mode console over shadcn-vue + reka-ui (Console theme)
colors:
  background: "hsl(211 19% 6.2%)"
  foreground: "hsl(211.2 17.8% 93.7%)"
  card: "hsl(211 14.3% 9.7%)"
  muted: "hsl(213.2 26% 3.4%)"
  muted-foreground: "hsl(211.1 6.5% 65.5%)"
  primary: "hsl(39.7 91.6% 60.4%)"
  primary-foreground: "hsl(31.3 100% 5.4%)"
  secondary: "hsl(211 13.6% 14.4%)"
  accent: "hsl(206.7 54.4% 16.9%)"
  destructive: "hsl(358.8 63% 35.5%)"
  border: "hsl(211 8.9% 19.2%)"
  input: "hsl(211 8% 40%)"
  ring: "hsl(39.7 91.6% 60.4%)"
  scrim: "hsl(216.1 57.8% 0.8%)"
  evidence-verified: "#61cb7c"
  evidence-verified-bg: "#162519"
  evidence-source: "#6ebcfc"
  evidence-source-bg: "#142e43"
  evidence-unknown: "#9da2a8"
  evidence-unknown-bg: "#20252a"
  evidence-negative: "#f66d67"
  evidence-negative-bg: "#2f1a18"
  evidence-mixed: "#b6a1df"
  evidence-mixed-bg: "#251d32"
typography:
  body:
    fontFamily: "Host Grotesk 400/500 (display and body), Atkinson Hyperlegible Mono for what an instrument measured"
    fontSize: "0.75rem–0.875rem (data); 16px floor for running prose"
    fontWeight: "400 body, 500 heads/labels/controls, 700 only for markdown strong"
  display:
    fontFamily: "Host Grotesk 500"
    fontSize: "1.25rem–1.875rem"
    letterSpacing: "-0.03em (h1/h2), -0.015em (h3/h4)"
rounded:
  card: "0.625rem (10px) — --radius-lg"
  control: "0.375rem (6px) — --radius-sm"
  chip: "4px (rounded-[4px])"
  pill: "rounded-full only for switch tracks, avatars, count discs"
spacing:
  section-gap: "1.25rem (gap-5)"
  card-padding: "1rem–1.5rem (p-4 / p-6)"
  control-gap: "0.375rem (gap-1.5) — 0.5rem (gap-2)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.control}"
    hover: "bg-primary/90 (one color step, no lift)"
  badge-verified:
    backgroundColor: "{colors.evidence-verified-bg}"
    textColor: "{colors.evidence-verified}"
    rounded: "{rounded.chip}"
  card-surface:
    backgroundColor: "{colors.card}"
    textColor: "{colors.card-foreground}"
    border: "1px {colors.border} — hairline panel, no shadow"
  focus:
    outline: "2px solid {colors.ring}, offset 2px, instant (global :focus-visible)"
---

# Skintellect Frontend — Design System

## Overview

Operate-mode console UI for an evidence-first skincare formulation tool, dealt on Hallmark's **Console** theme (graphite colourway). The metaphor: an instrument kept by careful people — a graphite ground in three lightness steps, hairline panels cut from one surface, **amber means a person** (primary actions, the persona, the current selection) and **cool blue means an instrument** (the copilot, system reads, versions). Nothing glows: no shadows, no blur, no gradients. Verdict-colored evidence chips are the visual language; every pair holds ≥ 4.5:1 on the graphite ground (asserted by `tests/check_ui_semantics.js`).

## Colors

All semantic colors resolve through Tailwind v4 `@theme inline` → CSS variables in `assets/index.css` (the single token file; `:root` is the dark theme — no `.dark` class is applied). Never raw palette classes (emerald/blue/slate…) or hexes in components; the only sanctioned hexes are the evidence family. Verdict semantics (product truth, hues re-dealt in the retheme): **verified** (green) = full verified INCI; **source** (blue) = attributed source; **unknown** (grey) = no reading yet; **negative** (red) = contraindication/flag; **mixed** (violet) = conflicting evidence. Class strings for badge variants live in `@/lib/evidence`.

## Typography

Host Grotesk (400 body, 500 heads/labels/controls; 700 only for markdown `strong`) + Atkinson Hyperlegible Mono for what an instrument measured — scores with units, INCI, IDs, timestamps, counts — always with `tabular-nums slashed-zero`. Heads: sentence case, weight 500, tracking −0.03em, `text-wrap: balance`. Labels, captions, table heads, chips, nav links: body face a step smaller, sentence case, untracked — never mono, never tracked caps. Emphasis comes from weight and the amber signal, never from gradient text or eyebrows.

## Layout

Explore = strips (domain, category, quick chips) → hero band (stat row with hairline-separated stats + context) → sidebar (w-80, lg+) + card grid (36/page). Content column max-w-3xl inside bands. Spacing rhythm: gap-5 between page sections, gap-6 between sidebar and grid, gap-1.5–2 inside control rows. Below `lg` the sidebar lives in a left-side Sheet sharing the same query state. The container is capped (max-w-7xl) and centered.

## Elevation & Depth

Depth by lightness, never shadow: ground (`--background` 6.2%), panel one step up (`--card` 9.7%), deepest step for code/logs/wells (`--muted` 3.4%). Every surface separates with 1px `--border` hairlines; `--rule`-equivalent `--input` (40%) marks field edges and selected spines at ≥ 3:1. Portals (dialog/sheet/select) float on the `--scrim` overlay — no glass, no backdrop-blur, no box shadows anywhere.

## Shapes

Radius: cards 10px (`--radius-lg`), controls 6px (`--radius-sm`), chips 4px (`rounded-[4px]`), pills only where the object is physically round (switch tracks, avatars, count discs). One radius per nesting level, concentric.

## Components

16 primitive packages under `frontend/src/components/ui/` (badge, button, card, checkbox, collapsible, dialog, input, scroll-area, select, separator, sheet, slider, switch, tabs, toggle, toggle-group), each an EGM-contracted thin wrapper over reka-ui with cva variants; composed into domain components (`components/explore|research|ai|compare|graph/`). One filled primary (amber) per screen; secondaries outlined on `--card`; ghost actions neutral-hover on `--secondary`. Focus is one language: the global `:focus-visible` 2px amber outline, instant. Buttons carry `active:opacity-80` press feedback. Dialogs/sheets float over the scrim; never a floating shadow.

## Do's and Don'ts

- **Do** express every verdict through evidence tokens; **don't** invent hexes or use Tailwind default palette colors (emerald/slate/indigo…).
- **Do** keep the amber/cool contract: amber = person (their actions, their profile, their selection), cool = instrument (copilot output, system reads, timestamps); **don't** swap them — an amber reading or a cool deviation is the theme lying.
- **Do** set measured values (scores, counts, INCI, timestamps) in the mono face with tabular numerals; **don't** put mono on labels, heads, or buttons.
- **Do** keep interaction semantics from reka-ui; **don't** re-implement tabs/checkboxes/toggles with divs and click handlers.
- **Don't** animate beyond transform/opacity color-steps at micro durations; motion is state feedback, not decoration. Every animation collapses under `prefers-reduced-motion`.
- **Don't** add emoji as icons (lucide is the icon family; emoji survive only inside chat copy as content), tracked-caps labels, middle-dot meta strings, or per-card hover animations.
- **Don't** reach for shadows, blur, or gradients; elevation is a hairline or a lightness step.
