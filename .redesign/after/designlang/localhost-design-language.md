# Design Language: Skintellect - Honest Science-Grounded Moisturizer Intelligence

> Extracted from `http://localhost:5173` on November 15, 2026
> 1768 elements analyzed

This document describes the complete design language of the website. It is structured for AI/LLM consumption — use it to faithfully recreate the visual design in any framework.

## Color Palette

### Primary Colors

| Role | Hex | RGB | HSL | Usage Count |
|------|-----|-----|-----|-------------|
| Primary | `#f7b83e` | rgb(247, 184, 62) | hsl(40, 92%, 61%) | 103 |
| Secondary | `#6ebcfc` | rgb(110, 188, 252) | hsl(207, 96%, 71%) | 324 |

### Tonal Ramps

Generated in OKLCH from each role colour, so the steps are perceptually even. The site's own colour keeps its position in the ladder.

| Role | 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| primary | `#fff0b0` | `#ffe39d` | `#ffd181` | **`#f7b83e`** | `#ce940c` | `#b07500` | `#965f00` | `#7c4b00` | `#673c00` | `#552f00` | `#321800` |
| secondary | `#cefcff` | `#bef0ff` | `#a7e0ff` | **`#6ebcfc`** | `#5da7e3` | `#3988c5` | `#2471aa` | `#125b8d` | `#054a77` | `#003c62` | `#00213b` |
| neutral | `#f3f6f9` | `#e7eaee` | `#d6dadd` | `#bcc1c5` | `#9ba0a5` | `#7e8387` | `#686d71` | `#53575b` | `#44474a` | **`#2d3135`** | `#1d1f21` |

### Semantic Pairs

| Role | Background | Foreground | Contrast | Level |
|------|------------|------------|----------|-------|
| `surface.page` | `#0d1013` | `#eceff2` | 16.53:1 | AAA |
| `surface.raised` | `#15191c` | `#eceff2` | 15.32:1 | AAA |
| `action.primary` | `#f7b83e` | `#1c0e00` | 10.68:1 | AAA |
| `action.secondary` | `#6ebcfc` | `#1c0e00` | 9.23:1 | AAA |

### Dominance

Share of painted background area — what the page looks like, as opposed to what it declares most often.

- `#0d1013` — 67%
- `#162519` — 25%
- `#06080b` — 7%
- `#142e43` — 1%
- `#20252a` — 0%
- `#f7b83e` — 0%

### Neutral Colors

| Hex | HSL | Usage Count |
|-----|-----|-------------|
| `#2d3135` | hsl(210, 8%, 19%) | 1529 |
| `#a1a7ad` | hsl(210, 7%, 65%) | 315 |
| `#5e666e` | hsl(210, 8%, 40%) | 52 |
| `#20252a` | hsl(210, 14%, 15%) | 36 |
| `#1c0e00` | hsl(30, 100%, 5%) | 13 |

### Background Colors

Used on large-area elements: `#0d1013`, `#15191c`

### Text Colors

Text color palette: `#eceff2`, `#61cb7c`, `#a1a7ad`, `#6ebcfc`, `#9da2a8`, `#1c0e00`, `#f7b83e`, `#000000`

### Full Color Inventory

| Hex | Contexts | Count |
|-----|----------|-------|
| `#2d3135` | border | 1529 |
| `#eceff2` | text, background | 753 |
| `#61cb7c` | text, border, background | 443 |
| `#6ebcfc` | text, border | 324 |
| `#a1a7ad` | text, border | 315 |
| `#162519` | background | 202 |
| `#06080b` | text, background | 127 |
| `#f7b83e` | background, text, border | 103 |
| `#5e666e` | border, background | 52 |
| `#142e43` | background | 36 |
| `#20252a` | background | 36 |
| `#1c0e00` | text | 13 |
| `#0d1013` | background | 10 |

## Typography

### Font Families

- **Host Grotesk** — used for all (538 elements)
- **Atkinson Hyperlegible Mono** — used for mono (1 elements)

### Type System

- **Scale ratio** — 1.125 (major second), anchored at 11px · 83% of sizes sit on the ladder
- **Measure** — ~105 characters per line (wide, low confidence from 1 sample)
- **Fluid type** — none; sizes are fixed per breakpoint

### Named Scale

| Role | Size | Weight | Line Height | Tracking |
|------|------|--------|-------------|----------|
| `h2` | 30px / 1.875rem | 500 | 36px | -0.9px |
| `h1` | 20px / 1.25rem | 500 | 28px | -0.6px |
| `h3` | 16px / 1rem | 400 | 24px | normal |
| `title-1` | 14px / 0.875rem | 500 | 20px | normal |
| `title-2` | 12px / 0.75rem | 400 | 16px | normal |
| `body` | 11px / 0.6875rem | 500 | 16.5px | normal |

### Type Scale

| Size (px) | Size (rem) | Weight | Line Height | Letter Spacing | Used On |
|-----------|------------|--------|-------------|----------------|---------|
| 30px | 1.875rem | 500 | 36px | -0.9px | h2 |
| 20px | 1.25rem | 500 | 28px | -0.6px | h1 |
| 16px | 1rem | 400 | 24px | normal | html, head, script, meta |
| 14px | 0.875rem | 500 | 20px | normal | button, svg, rect, path |
| 12px | 0.75rem | 400 | 16px | normal | nav, a, button, svg |
| 11px | 0.6875rem | 500 | 16.5px | normal | div, span, p, svg |

### Heading Scale

```css
h2 { font-size: 30px; font-weight: 500; line-height: 36px; }
h1 { font-size: 20px; font-weight: 500; line-height: 28px; }
h3 { font-size: 16px; font-weight: 400; line-height: 24px; }
```

### Body Text

```css
body { font-size: 11px; font-weight: 500; line-height: 16.5px; }
```

### Font Weights in Use

`500` (1277x), `400` (491x)

## Spacing

**Base unit:** 4px

| Token | Value | Rem |
|-------|-------|-----|
| spacing-4 | 4px | 0.25rem |
| spacing-8 | 8px | 0.5rem |
| spacing-12 | 12px | 0.75rem |
| spacing-16 | 16px | 1rem |
| spacing-20 | 20px | 1.25rem |
| spacing-24 | 24px | 1.5rem |
| spacing-32 | 32px | 2rem |

## Border Radii

| Label | Value | Count |
|-------|-------|-------|
| sm | 4px | 85 |
| md | 10px | 44 |

## CSS Custom Properties

### Colors

```css
--foreground: 211.2 17.8% 93.7%;
--card: 211 14.3% 9.7%;
--card-foreground: 211.2 17.8% 93.7%;
--popover: 211 14.3% 9.7%;
--popover-foreground: 211.2 17.8% 93.7%;
--primary: 39.7 91.6% 60.4%;
--primary-foreground: 31.3 100% 5.4%;
--secondary: 211 13.6% 14.4%;
--secondary-foreground: 211.2 17.8% 93.7%;
--muted: 213.2 26% 3.4%;
--muted-foreground: 211.1 6.5% 65.5%;
--accent: 206.7 54.4% 16.9%;
--accent-foreground: 211.2 17.8% 93.7%;
--destructive: 358.8 63% 35.5%;
--destructive-foreground: 6 20.5% 95.1%;
--border: 211 8.9% 19.2%;
--ring: 39.7 91.6% 60.4%;
--tw-ring-offset-shadow: 0 0 #0000;
--color-evidence-verified: #61cb7c;
--tw-ring-shadow: 0 0 #0000;
--color-evidence-source: #6ebcfc;
--tw-inset-ring-shadow: 0 0 #0000;
--color-evidence-verified-bg: #162519;
--color-rose-500: oklch(64.5% 0.246 16.439);
--color-evidence-mixed: #b6a1df;
--color-evidence-unknown-bg: #20252a;
--color-evidence-negative: #f66d67;
--color-purple-100: oklch(94.6% 0.033 307.174);
--color-evidence-source-bg: #142e43;
--tw-ring-offset-color: #fff;
--color-white: #fff;
--tw-border-style: solid;
--tw-ring-offset-width: 0px;
--color-evidence-unknown: #9da2a8;
--color-evidence-mixed-bg: #251d32;
--color-black: #000;
--color-evidence-negative-bg: #2f1a18;
```

### Spacing

```css
--spacing: 0.25rem;
--tw-space-y-reverse: 0;
```

### Typography

```css
--font-display: "Host Grotesk", ui-sans-serif, system-ui, sans-serif;
--font-body: "Host Grotesk", ui-sans-serif, system-ui, sans-serif;
--font-outlier: "Atkinson Hyperlegible Mono", ui-monospace, monospace;
--text-2xl: 1.5rem;
--tracking-tight: -0.025em;
--leading-relaxed: 1.625;
--leading-snug: 1.375;
--font-weight-black: 900;
--text-lg: 1.125rem;
--text-2xl--line-height: calc(2 / 1.5);
--text-base--line-height: calc(1.5 / 1);
--tracking-wider: 0.05em;
--font-mono: "Atkinson Hyperlegible Mono", ui-monospace, monospace;
--text-xl--line-height: calc(1.75 / 1.25);
--font-weight-semibold: 600;
--text-sm: 0.875rem;
--text-lg--line-height: calc(1.75 / 1.125);
--leading-tight: 1.25;
--font-weight-extrabold: 800;
--font-weight-bold: 700;
--text-sm--line-height: calc(1.25 / 0.875);
--text-3xl--line-height: calc(2.25 / 1.875);
--text-xs: 0.75rem;
--default-font-family: "Host Grotesk", ui-sans-serif, system-ui, sans-serif;
--text-xs--line-height: calc(1 / 0.75);
--font-weight-medium: 500;
--text-3xl: 1.875rem;
--font-weight-normal: 400;
--font-serif: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
--text-xl: 1.25rem;
--text-base: 1rem;
--default-mono-font-family: "Atkinson Hyperlegible Mono", ui-monospace, monospace;
```

### Shadows

```css
--tw-inset-shadow-alpha: 100%;
--tw-drop-shadow-alpha: 100%;
--tw-inset-shadow: 0 0 #0000;
--tw-shadow-alpha: 100%;
--tw-shadow: 0 0 #0000;
```

### Radii

```css
--radius: 0.625rem;
--radius-sm: calc(0.625rem - 4px);
--radius-2xl: 1rem;
```

### Other

```css
--background: 211 19% 6.2%;
--input: 211 8% 40%;
--scrim: 216.1 57.8% 0.8%;
--tw-animation-delay: 0s;
--default-transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
--tw-animation-iteration-count: 1;
--tw-exit-opacity: 1;
--tw-outline-style: solid;
--tw-animation-fill-mode: none;
--tw-exit-blur: 0;
--tw-translate-z: 0;
--tw-animation-direction: normal;
--tw-enter-scale: 1;
--tw-exit-translate-x: 0;
--container-3xl: 48rem;
--tw-translate-y: 0;
--animate-spin: spin 1s linear infinite;
--tw-enter-translate-x: 0;
--container-4xl: 56rem;
--tw-divide-y-reverse: 0;
--tw-exit-rotate: 0;
--container-2xl: 42rem;
--tw-exit-scale: 1;
--container-sm: 24rem;
--tw-translate-x: 0;
--tw-exit-translate-y: 0;
--tw-enter-rotate: 0;
--container-lg: 32rem;
--tw-enter-translate-y: 0;
--tw-enter-blur: 0;
--default-transition-duration: 150ms;
--animate-pulse: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
--tw-enter-opacity: 1;
--container-7xl: 80rem;
--blur-sm: 8px;
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### Semantic

```css
--destructive: 358.8 63% 35.5%;
--destructive-foreground: 6 20.5% 95.1%;
--color-evidence-negative: #f66d67;
--color-evidence-negative-bg: #2f1a18;
```

## Transitions & Animations

**Easing functions:** `cubic-bezier(0.4, 0, 0.2, 1)`

**Durations:** `0.15s`

### Common Transitions

```css
transition: all;
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), outline-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-from 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-via 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-to 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), outline-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-from 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-via 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-to 0.15s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.15s cubic-bezier(0.4, 0, 0.2, 1), transform 0.15s cubic-bezier(0.4, 0, 0.2, 1), translate 0.15s cubic-bezier(0.4, 0, 0.2, 1), scale 0.15s cubic-bezier(0.4, 0, 0.2, 1), rotate 0.15s cubic-bezier(0.4, 0, 0.2, 1), filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), -webkit-backdrop-filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), backdrop-filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), display 0.15s cubic-bezier(0.4, 0, 0.2, 1), content-visibility 0.15s cubic-bezier(0.4, 0, 0.2, 1), overlay 0.15s cubic-bezier(0.4, 0, 0.2, 1), pointer-events 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: transform 0.15s cubic-bezier(0.4, 0, 0.2, 1), translate 0.15s cubic-bezier(0.4, 0, 0.2, 1), scale 0.15s cubic-bezier(0.4, 0, 0.2, 1), rotate 0.15s cubic-bezier(0.4, 0, 0.2, 1);
```

### Keyframe Animations

**spin**
```css
@keyframes spin {
  100% { transform: rotate(360deg); }
}
```

**pulse**
```css
@keyframes pulse {
  50% { opacity: 0.5; }
}
```

**enter**
```css
@keyframes enter {
  0% { opacity: var(--tw-enter-opacity,1); transform: translate3d(var(--tw-enter-translate-x,0),var(--tw-enter-translate-y,0),0)scale3d(var(--tw-enter-scale,1),var(--tw-enter-scale,1),var(--tw-enter-scale,1))rotate(var(--tw-enter-rotate,0)); filter: blur(var(--tw-enter-blur,0)); }
}
```

**exit**
```css
@keyframes exit {
  100% { opacity: var(--tw-exit-opacity,1); transform: translate3d(var(--tw-exit-translate-x,0),var(--tw-exit-translate-y,0),0)scale3d(var(--tw-exit-scale,1),var(--tw-exit-scale,1),var(--tw-exit-scale,1))rotate(var(--tw-exit-rotate,0)); filter: blur(var(--tw-exit-blur,0)); }
}
```

**collapsible-down**
```css
@keyframes collapsible-down {
  0% { height: 0px; }
  100% { height: var(--radix-collapsible-content-height,var(--bits-collapsible-content-height,var(--reka-collapsible-content-height,var(--kb-collapsible-content-height,auto)))); }
}
```

**collapsible-up**
```css
@keyframes collapsible-up {
  0% { height: var(--radix-collapsible-content-height,var(--bits-collapsible-content-height,var(--reka-collapsible-content-height,var(--kb-collapsible-content-height,auto)))); }
  100% { height: 0px; }
}
```

## Component Patterns

Detected UI component patterns and their most common styles:

### Buttons (149 instances)

```css
.buttons {
  background-color: rgb(21, 25, 28);
  color: rgb(236, 239, 242);
  font-size: 12px;
  font-weight: 500;
  padding-top: 0px;
  padding-right: 12px;
  border-radius: 6px;
}
```

### Cards (93 instances)

```css
.cards {
  background-color: rgb(21, 25, 28);
  border-radius: 6px;
  padding-top: 0px;
  padding-right: 12px;
}
```

### Inputs (1 instances)

```css
.inputs {
  background-color: rgb(6, 8, 11);
  color: rgb(236, 239, 242);
  border-color: rgb(94, 102, 110);
  border-radius: 6px;
  font-size: 12px;
  padding-top: 4px;
  padding-right: 12px;
}
```

### Links (4 instances)

```css
.links {
  color: rgb(161, 167, 173);
  font-size: 12px;
  font-weight: 500;
}
```

### Navigation (2 instances)

```css
.navigation {
  color: rgb(161, 167, 173);
  padding-top: 0px;
  padding-bottom: 0px;
  padding-left: 0px;
  padding-right: 0px;
  position: static;
}
```

### Tabs (4 instances)

```css
.tabs {
  color: rgb(161, 167, 173);
  font-size: 14px;
  font-weight: 500;
  padding-top: 12px;
  padding-right: 4px;
  border-color: rgb(247, 184, 62);
  border-radius: 0px;
}
```

### Switches (8 instances)

```css
.switches {
  background-color: rgb(94, 102, 110);
  border-radius: 6px;
  border-color: rgb(45, 49, 53);
}
```

## Component Clusters

Reusable component instances grouped by DOM structure and style similarity:

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(21, 25, 28);
  color: rgb(236, 239, 242);
  padding: 0px 0px 0px 0px;
  border-radius: 0px;
  border: 0px 0px 1px solid rgb(45, 49, 53);
  font-size: 16px;
  font-weight: 400;
```

### Button — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(21, 25, 28);
  color: rgb(247, 184, 62);
  padding: 0px 14px 0px 14px;
  border-radius: 6px;
  border: 1px solid rgb(94, 102, 110);
  font-size: 12px;
  font-weight: 500;
```

### Button — 90 instances, 4 variants

**Variant 1** (5 instances)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(247, 184, 62);
  padding: 12px 4px 12px 4px;
  border-radius: 0px;
  border: 0px 0px 2px solid rgb(247, 184, 62);
  font-size: 14px;
  font-weight: 500;
```

**Variant 2** (1 instance)

```css
  background: rgb(247, 184, 62);
  color: rgb(28, 14, 0);
  padding: 6px 12px 6px 12px;
  border-radius: 6px;
  border: 0px solid rgb(45, 49, 53);
  font-size: 12px;
  font-weight: 500;
```

**Variant 3** (48 instances)

```css
  background: rgb(6, 8, 11);
  color: rgb(236, 239, 242);
  padding: 6px 12px 6px 12px;
  border-radius: 6px;
  border: 0px solid rgb(45, 49, 53);
  font-size: 12px;
  font-weight: 500;
```

**Variant 4** (36 instances)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(110, 188, 252);
  padding: 0px 12px 0px 12px;
  border-radius: 6px;
  border: 0px solid rgb(45, 49, 53);
  font-size: 12px;
  font-weight: 500;
```

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(21, 25, 28);
  color: rgb(236, 239, 242);
  padding: 10px 10px 10px 10px;
  border-radius: 10px;
  border: 1px solid rgb(45, 49, 53);
  font-size: 16px;
  font-weight: 400;
```

### Button — 49 instances, 3 variants

**Variant 1** (3 instances)

```css
  background: rgb(247, 184, 62);
  color: rgb(28, 14, 0);
  padding: 4px 12px 4px 12px;
  border-radius: 4px;
  border: 0px solid rgb(45, 49, 53);
  font-size: 12px;
  font-weight: 500;
```

**Variant 2** (10 instances)

```css
  background: rgb(21, 25, 28);
  color: rgb(236, 239, 242);
  padding: 4px 12px 4px 12px;
  border-radius: 4px;
  border: 1px solid rgb(94, 102, 110);
  font-size: 12px;
  font-weight: 500;
```

**Variant 3** (36 instances)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(236, 239, 242);
  padding: 8px 0px 8px 0px;
  border-radius: 0px;
  border: 0px solid rgb(45, 49, 53);
  font-size: 16px;
  font-weight: 500;
```

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(21, 25, 28);
  color: rgb(236, 239, 242);
  padding: 32px 32px 32px 32px;
  border-radius: 10px;
  border: 1px solid rgb(45, 49, 53);
  font-size: 16px;
  font-weight: 400;
```

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(21, 25, 28);
  color: rgb(236, 239, 242);
  padding: 20px 20px 20px 20px;
  border-radius: 10px;
  border: 1px solid rgb(45, 49, 53);
  font-size: 16px;
  font-weight: 400;
```

### Button — 4 instances, 1 variant

**Variant 1** (4 instances)

```css
  background: rgb(6, 8, 11);
  color: rgb(236, 239, 242);
  padding: 8px 12px 8px 12px;
  border-radius: 6px;
  border: 1px solid rgb(94, 102, 110);
  font-size: 12px;
  font-weight: 500;
```

### Button — 4 instances, 1 variant

**Variant 1** (4 instances)

```css
  background: rgb(94, 102, 110);
  color: rgb(236, 239, 242);
  padding: 0px 0px 0px 0px;
  border-radius: 3.35544e+07px;
  border: 1px solid rgba(0, 0, 0, 0);
  font-size: 12px;
  font-weight: 400;
```

### Card — 36 instances, 1 variant

**Variant 1** (36 instances)

```css
  background: rgb(21, 25, 28);
  color: rgb(236, 239, 242);
  padding: 0px 0px 0px 0px;
  border-radius: 10px;
  border: 1px solid rgb(45, 49, 53);
  font-size: 16px;
  font-weight: 400;
```

## Layout System

**2 grid containers** and **593 flex containers** detected.

### The System

- **Content column** — 1280px wide (full-bleed — no constrained container found), 24px gutters (2% edge density)
  - Widest constrained block inside it: 768px
  - Width ladder: 768px · 1280px
- **Column system** — 3 columns
- **Section rhythm** — 24px vertical padding (ladder: 24px · 32px)
- **Gap scale** — 4px · 6px · 8px · 12px · 16px · 20px · 24px · 32px

### Container Widths

| Max Width | Padding |
|-----------|---------|
| 1280px | 24px |
| 768px | 0px |

### Grid Column Patterns

| Columns | Usage Count |
|---------|-------------|
| 5-column | 1x |
| 3-column | 1x |

### Grid Templates

```css
grid-template-columns: 282.656px 282.672px 282.656px;
gap: 20px;
grid-template-columns: 52.3906px 52.4062px 52.3906px 52.4062px 52.4062px;
gap: 4px;
```

### Flex Patterns

| Direction/Wrap | Count |
|----------------|-------|
| column/nowrap | 123x |
| row/nowrap | 431x |
| row/wrap | 39x |

**Gap values:** `4px`, `6px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`

## Accessibility (WCAG 2.1)

**Overall Score: 100%** — 170 passing, 0 failing color pairs

### Passing Color Pairs

| Foreground | Background | Ratio | Level |
|------------|------------|-------|-------|
| `#eceff2` | `#15191c` | 15.32:1 | AAA |
| `#61cb7c` | `#162519` | 7.88:1 | AAA |
| `#6ebcfc` | `#142e43` | 6.83:1 | AA |
| `#9da2a8` | `#20252a` | 6.01:1 | AA |
| `#1c0e00` | `#f7b83e` | 10.68:1 | AAA |
| `#eceff2` | `#06080b` | 17.37:1 | AAA |
| `#eceff2` | `#0d1013` | 16.53:1 | AAA |

## Design System Score

**Overall: 99/100 (Grade: A)**

| Category | Score |
|----------|-------|
| Color Discipline | 92/100 |
| Typography Consistency | 100/100 |
| Spacing System | 100/100 |
| Shadow Consistency | 100/100 |
| Border Radius Consistency | 100/100 |
| Accessibility | 100/100 |
| CSS Tokenization | 100/100 |

**Strengths:** Tight, disciplined color palette, Consistent typography system, Well-defined spacing scale, Clean elevation system, Consistent border radii, Strong accessibility compliance, Good CSS variable tokenization

## Z-Index Map

**2 unique z-index values** across 1 layers.

| Layer | Range | Elements |
|-------|-------|----------|
| sticky | 10,40 | div.m.a.x.-.w.-.3.x.l. .f.l.e.x. .f.l.e.x.-.c.o.l. .g.a.p.-.3. .r.e.l.a.t.i.v.e. .z.-.1.0, header.b.o.r.d.e.r.-.b. .b.g.-.c.a.r.d. .s.t.i.c.k.y. .t.o.p.-.0. .z.-.4.0 |

## SVG Icons

**29 unique SVG icons** detected. Dominant style: **outlined**.

| Size Class | Count |
|------------|-------|
| xs | 18 |
| sm | 10 |
| md | 1 |

**Icon colors:** `currentColor`

## Font Files

| Family | Source | Weights | Styles |
|--------|--------|---------|--------|
| Host Grotesk | self-hosted | 400, 500, 700 | normal |
| Atkinson Hyperlegible Mono | self-hosted | 400, 500 | normal |

## Motion Language

**Feel:** mixed · **Scroll-linked:** yes

### Duration Tokens

| name | value | ms |
|---|---|---|
| `xs` | `150ms` | 150 |

### Easing Families

- **custom** (227 uses) — `cubic-bezier(0.4, 0, 0.2, 1)`

## Component Anatomy

### button — 148 instances

**Slots:** label, icon
**Variants:** secondary · primary · destructive
**Sizes:** xs · sm · medium

| variant | count | sample label |
|---|---|---|
| primary | 45 | Catalog & Explore |
| secondary | 42 | Profile:
uap (Combination · Barrier & Da |
| default | 41 | Barrier Lipids (Ceramides) |
| destructive | 20 | All Domains |

### card — 40 instances

**Slots:** media
**Sizes:** lg · sm

## Brand Voice

**Tone:** friendly · **Pronoun:** third-person · **Headings:** Title Case (tight)

### Top CTA Verbs

- **compare** (37)
- **ask** (36)
- **all** (6)
- **pdrn** (3)
- **power** (2)
- **super** (2)
- **profile** (1)
- **explore** (1)

### Button Copy Patterns

- "compare" (36×)
- "ask copilot" (36×)
- "all categories" (2×)
- "1" (1×)
- "2" (1×)
- "70" (1×)
- "profile:
uap (combination · barrier & dark spots)" (1×)
- "catalog & explore" (1×)
- "compare matrix" (1×)
- "ingredient graph" (1×)

### Sample Headings

> Formulation Studio
> Universal Cosmetic Chemistry & Formulation Intelligence
> Acnestil Cleansing Mousse
> Power Serum Bright Serum
> Pore Clarifying Brightening Serum
> Plaisir No Shine Oil Free Gel

## Page Intent

**Type:** `landing` (confidence 0.45)

## Section Roles

Reading order (top→bottom): nav → nav → pricing → sidebar → nav → content

| # | Role | Heading | Confidence |
|---|------|---------|------------|
| 0 | nav | Formulation Studio | 0.4 |
| 1 | nav | — | 0.9 |
| 2 | pricing | Universal Cosmetic Chemistry & Formulation Intelligence | 0.4 |
| 3 | sidebar | — | 0.4 |
| 4 | nav | — | 0.9 |
| 5 | content | — | 0.3 |

## Material Language

**Label:** `flat` (confidence 0)

| Metric | Value |
|--------|-------|
| Avg saturation | 0.411 |
| Shadow profile | soft |
| Avg shadow blur | 0px |
| Max radius | 10px |
| backdrop-filter in use | no |
| Gradients | 0 |

## Component Library

**Detected:** `shadcn/ui` (confidence 0.65)

Evidence:
- shadcn css tokens

Also considered: tailwindcss (0.3)

## Quick Start

To recreate this design in a new project:

1. **Install fonts:** Add `Host Grotesk` from Google Fonts or your font provider
2. **Import CSS variables:** Copy `variables.css` into your project
3. **Tailwind users:** Use the generated `tailwind.config.js` to extend your theme
4. **Design tokens:** Import `design-tokens.json` for tooling integration
