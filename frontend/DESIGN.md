---
name: Skintellect Frontend
description: Explainable cosmetic formulation intelligence — Operate-mode product UI over shadcn-vue + reka-ui
colors:
  primary: "hsl(184 78% 25%)"
  primary-foreground: "hsl(0 0% 100%)"
  background: "hsl(216 33% 97%)"
  foreground: "hsl(213 47% 17%)"
  card: "hsl(0 0% 100%)"
  card-foreground: "hsl(213 47% 17%)"
  muted: "hsl(210 40% 96.1%)"
  muted-foreground: "hsl(215.4 16.3% 45%)"
  accent: "hsl(210 40% 96.1%)"
  destructive: "hsl(351 54% 42%)"
  border: "hsl(214.3 31.8% 91.4%)"
  evidence-verified: "#12635a"
  evidence-verified-bg: "#e5f5f2"
  evidence-source: "#245ba9"
  evidence-source-bg: "#eaf2ff"
  evidence-unknown: "#805309"
  evidence-unknown-bg: "#fff4da"
  evidence-negative: "#a63244"
  evidence-negative-bg: "#fff0f2"
  evidence-mixed: "#6843a8"
  evidence-mixed-bg: "#f2edfc"
typography:
  body:
    fontFamily: "system sans stack (Tailwind default), ui-monospace for code/data"
    fontSize: "0.75rem–0.875rem"
    fontWeight: 500–700 (labels bold, body medium)
  display:
    fontFamily: "system sans stack"
    fontSize: "1.5rem–1.875rem"
    fontWeight: 800–900
    letterSpacing: "-0.025em (tracking-tight)"
rounded:
  sm: "calc(0.5rem - 4px)"
  md: "calc(0.5rem - 2px)"
  lg: "0.5rem"
  xl: "calc(0.5rem + 4px)"
  pill: "9999px (chips/round controls)"
spacing:
  section-gap: "1.25rem (gap-5)"
  card-padding: "1.25rem (px-5) / 1.5rem (p-6)"
  control-gap: "0.375rem (gap-1.5) — 0.5rem (gap-2)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
  badge-verified:
    backgroundColor: "{colors.evidence-verified-bg}"
    textColor: "{colors.evidence-verified}"
  badge-negative:
    backgroundColor: "{colors.evidence-negative-bg}"
    textColor: "{colors.evidence-negative}"
  card-surface:
    backgroundColor: "{colors.card}"
    textColor: "{colors.card-foreground}"
    rounded: "{rounded.xl}"
---

# Skintellect Frontend — Design System

## Overview

Operate-mode product UI for an evidence-first skincare formulation tool. Every surface optimizes scanability of *verifiable* claims: verdict-colored evidence badges (verified/source/unknown/negative/mixed) are the visual language, teal `primary` is the only brand accent, and controls are shadcn-vue-style primitives over reka-ui. Dark mode tokens exist (`_dark` variants) but dark is not a shipped surface yet.

## Colors

All semantic colors resolve through Tailwind v4 `@theme inline` → CSS variables in `assets/index.css` (`:root`). Never raw hex in components; the only sanctioned hexes are the evidence family above. Verdict semantics: **verified** (teal) = full verified INCI; **source** (blue) = attributed source; **unknown** (amber) = unverified claim; **negative** (rose) = contraindication/flag; **mixed** (purple) = mixed evidence. Class strings for badge/button variants live in `@/lib/evidence`.

## Typography

System sans; body 12–14px (`text-xs`/`text-sm`) with medium-to-bold weights — labels are uppercase `tracking-wider text-[11px] font-bold`, headings `font-black tracking-tight` at 24–30px. Data/code (JSON payload, INCI lists) uses `ui-monospace`. Emphasis comes from weight, never gradient text or eyebrow labels.

## Layout

Explore = strips (domain, category, quick chips) → hero header (stat row + context) → sidebar (w-80, lg+) + card grid (36/page). Content column max-w-3xl inside heroes. Spacing rhythm: gap-5 between page sections, gap-6 between sidebar and grid, gap-1.5–2 inside control rows. Below `lg` the sidebar lives in a left-side Sheet sharing the same query state.

## Elevation & Depth

Flat surfaces with 1px borders (`border-border`); `shadow-xs`/`shadow-2xs` for cards and controls, `shadow-lg` only for portal layers (dialogs/sheets). No zero-offset halos, no hard offset shadows. Rounded: cards `rounded-2xl`, controls `rounded-md/lg`, chips `rounded-full`.

## Shapes

Radius scale derives from `--radius: 0.5rem` (sm/md/lg/xl). Pills only for small controls (chips, preset buttons, filter rounds).

## Components

16 primitive packages under `frontend/src/components/ui/` (badge, button, card, checkbox, collapsible, dialog, input, scroll-area, select, separator, sheet, slider, switch, tabs, toggle, toggle-group), each an EGM-contracted thin wrapper over reka-ui with cva variants; composed into domain components (`components/explore|research|ai|compare|graph/`). Buttons: variants `default|destructive|outline|secondary|ghost|link|evidence`, sizes `default|sm|lg|icon`. Dialogs/Sheets: reka focus trap, Escape close, focus restore. Form controls (Select/Switch/Checkbox/Slider/ToggleGroup) inherit keyboard + ARIA from reka-ui — never hand-roll equivalents.

## Do's and Don'ts

- **Do** express every verdict through evidence tokens; **don't** invent hexes or gray-on-colored-surface secondary text.
- **Do** keep interaction semantics from reka-ui; **don't** re-implement tabs/checkboxes/toggles with divs and click handlers.
- **Do** write labels that name the action and the recovery ("Ask Copilot About This Formula", errors with Retry); **don't** use insider shorthand without a tooltip ("111 pts", "(Full)").
- **Don't** add a kicker/eyebrow above headings; the heading carries its own weight.
- **Don't** use emoji as the icon system inside controls — lucide is the drawn-icon family (emoji appear only as content flavor in data labels).
- **Don't** animate beyond transform/opacity micro-feedback; motion is feedback, not decoration.
