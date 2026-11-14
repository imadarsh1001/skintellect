# Design Language: Skintellect - Honest Science-Grounded Moisturizer Intelligence

> Extracted from `http://localhost:5173` on November 15, 2026
> 1715 elements analyzed

This document describes the complete design language of the website. It is structured for AI/LLM consumption — use it to faithfully recreate the visual design in any framework.

## Color Palette

### Primary Colors

| Role | Hex | RGB | HSL | Usage Count |
|------|-----|-----|-----|-------------|
| Primary | `#0e6b71` | rgb(14, 107, 113) | hsl(184, 78%, 25%) | 291 |
| Secondary | `#172940` | rgb(23, 41, 64) | hsl(214, 47%, 17%) | 707 |

### Tonal Ramps

Generated in OKLCH from each role colour, so the steps are perceptually even. The site's own colour keeps its position in the ladder.

| Role | 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| primary | `#d2ffff` | `#c2f5f9` | `#ace5ea` | `#8cced3` | `#63aeb4` | `#409096` | `#2b797f` | **`#0e6b71`** | `#0c5055` | `#034145` | `#002427` |
| secondary | `#e9f7ff` | `#dcebff` | `#cadbf2` | `#afc2dc` | `#8ca2bd` | `#6f849f` | `#5a6e87` | `#47586f` | `#38485c` | `#2c3a4b` | **`#172940`** |
| neutral | `#ecf6ff` | `#dfebfc` | `#cedaed` | `#b3c1d6` | `#91a1b7` | `#74839a` | **`#606f85`** | `#4b586a` | `#3c4758` | `#303948` | `#191f29` |

### Semantic Pairs

| Role | Background | Foreground | Contrast | Level |
|------|------------|------------|----------|-------|
| `surface.page` | `#f5f7fa` | `#172940` | 13.71:1 | AAA |
| `surface.raised` | `#ffffff` | `#172940` | 14.71:1 | AAA |
| `action.primary` | `#0e6b71` | `#ffffff` | 6.25:1 | AA * |
| `action.secondary` | `#172940` | `#ffffff` | 14.71:1 | AAA * |

\* No colour the site already uses for text reaches 4.5:1 on that surface — the foreground shown is black or white, substituted in.

### Dominance

Share of painted background area — what the page looks like, as opposed to what it declares most often.

- `#f1f5f9` — 99%
- `#e2e8f0` — 1%
- `#0e6b71` — 0%
- `#00bc7d` — 0%

### Neutral Colors

| Hex | HSL | Usage Count |
|-----|-----|-------------|
| `#606f85` | hsl(216, 16%, 45%) | 240 |
| `#000000` | hsl(0, 0%, 0%) | 8 |

### Background Colors

Used on large-area elements: `#f5f7fa`, `#ffffff`

### Text Colors

Text color palette: `#172940`, `#606f85`, `#12635a`, `#0e6b71`, `#1447e6`, `#007a55`, `#314158`, `#ffffff`, `#000000`, `#fe9a00`

### Gradients

```css
background-image: linear-gradient(to right top, rgb(14, 107, 113) 0%, oklch(0.596 0.145 163.225) 100%);
```

```css
background-image: linear-gradient(to right bottom, oklab(0.481727 -0.0724493 -0.0302838 / 0.05) 0%, rgb(255, 255, 255) 50%, rgb(255, 255, 255) 100%);
```

### Full Color Inventory

| Hex | Contexts | Count |
|-----|----------|-------|
| `#e2e8f0` | border, background | 1636 |
| `#172940` | text | 707 |
| `#12635a` | text, border | 367 |
| `#f1f5f9` | background, text | 332 |
| `#0e6b71` | text, background, border | 291 |
| `#606f85` | text | 240 |
| `#fe9a00` | text | 72 |
| `#007a55` | text | 36 |
| `#a4f4cf` | border | 36 |
| `#1447e6` | text | 36 |
| `#bedbff` | border | 36 |
| `#314158` | text | 36 |
| `#000000` | text | 8 |
| `#00bc7d` | background | 1 |

## Typography

### Type System

- **Scale ratio** — 1.125 (major second), anchored at 10px · 86% of sizes sit on the ladder
- **Measure** — ~109 characters per line (wide, low confidence from 1 sample)
- **Fluid type** — none; sizes are fixed per breakpoint

### Named Scale

| Role | Size | Weight | Line Height | Tracking |
|------|------|--------|-------------|----------|
| `h2` | 30px / 1.875rem | 900 | 36px | -0.75px |
| `h1` | 20px / 1.25rem | 900 | 28px | normal |
| `h3` | 16px / 1rem | 400 | 24px | normal |
| `title-1` | 14px / 0.875rem | 600 | 20px | normal |
| `body` | 12px / 0.75rem | 400 | 16px | normal |
| `body-sm` | 11px / 0.6875rem | 500 | 16.5px | normal |
| `micro` | 10px / 0.625rem | 700 | 15px | 0.5px |

### Type Scale

| Size (px) | Size (rem) | Weight | Line Height | Letter Spacing | Used On |
|-----------|------------|--------|-------------|----------------|---------|
| 30px | 1.875rem | 900 | 36px | -0.75px | h2 |
| 20px | 1.25rem | 900 | 28px | normal | div, h1 |
| 16px | 1rem | 400 | 24px | normal | html, head, script, meta |
| 14px | 0.875rem | 600 | 20px | normal | button, svg, rect, path |
| 12px | 0.75rem | 400 | 16px | normal | nav, a, button, svg |
| 11px | 0.6875rem | 500 | 16.5px | normal | p, span, svg, path |
| 10px | 0.625rem | 700 | 15px | 0.5px | div, span |

### Heading Scale

```css
h2 { font-size: 30px; font-weight: 900; line-height: 36px; }
h1 { font-size: 20px; font-weight: 900; line-height: 28px; }
h3 { font-size: 16px; font-weight: 400; line-height: 24px; }
```

### Body Text

```css
body { font-size: 12px; font-weight: 400; line-height: 16px; }
```

### Font Weights in Use

`600` (799x), `400` (483x), `700` (329x), `500` (64x), `800` (36x), `900` (4x)

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
| sm | 4px | 36 |
| md | 8px | 4 |
| lg | 12px | 6 |
| lg | 16px | 38 |
| xl | 24px | 1 |

## Elevation

3 levels from 6 raw shadows · neutral tint

**xs** — blur 0px, y 1px, used 1× · 5 layers
```css
box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.05) 0px 1px 0px 0px;
```

**sm** — blur 3px, y 1px, used 81× · 6 layers
```css
box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px;
```

**md** — blur 6px, y 4px, used 1× · 6 layers
```css
box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 4px 6px -1px, rgba(0, 0, 0, 0.1) 0px 2px 4px -2px;
```

## CSS Custom Properties

### Colors

```css
--foreground: 213 47% 17%;
--card: 0 0% 100%;
--card-foreground: 213 47% 17%;
--popover: 0 0% 100%;
--popover-foreground: 213 47% 17%;
--primary: 184 78% 25%;
--primary-foreground: 0 0% 100%;
--secondary: 210 40% 96.1%;
--secondary-foreground: 222.2 47.4% 11.2%;
--muted: 210 40% 96.1%;
--muted-foreground: 215.4 16.3% 45%;
--accent: 210 40% 96.1%;
--accent-foreground: 222.2 47.4% 11.2%;
--destructive: 351 54% 42%;
--destructive-foreground: 0 0% 100%;
--border: 214.3 31.8% 91.4%;
--ring: 184 78% 25%;
--color-purple-200: oklch(90.2% 0.063 306.703);
--color-purple-300: oklch(82.7% 0.119 306.383);
--color-amber-400: oklch(82.8% 0.189 84.429);
--tw-ring-shadow: 0 0 #0000;
--color-rose-200: oklch(89.2% 0.058 10.001);
--color-slate-200: oklch(92.9% 0.013 255.508);
--color-emerald-300: oklch(84.5% 0.143 164.978);
--color-slate-700: oklch(37.2% 0.044 257.287);
--color-blue-700: oklch(48.8% 0.243 264.376);
--color-amber-600: oklch(66.6% 0.179 58.318);
--color-purple-800: oklch(43.8% 0.218 303.724);
--tw-inset-ring-shadow: 0 0 #0000;
--color-emerald-700: oklch(50.8% 0.118 165.612);
--color-teal-50: oklch(98.4% 0.014 180.72);
--color-blue-300: oklch(80.9% 0.105 251.813);
--color-slate-300: oklch(86.9% 0.022 252.894);
--color-purple-900: oklch(38.1% 0.176 304.987);
--color-teal-800: oklch(43.7% 0.078 188.216);
--color-emerald-600: oklch(59.6% 0.145 163.225);
--color-purple-100: oklch(94.6% 0.033 307.174);
--tw-ring-offset-color: #fff;
--color-white: #fff;
--color-rose-100: oklch(94.1% 0.03 12.58);
--color-teal-950: oklch(27.7% 0.046 192.524);
--color-emerald-100: oklch(95% 0.052 163.051);
--color-rose-400: oklch(71.2% 0.194 13.428);
--color-emerald-200: oklch(90.5% 0.093 164.15);
--tw-ring-offset-width: 0px;
--color-purple-950: oklch(29.1% 0.149 302.717);
--color-purple-600: oklch(55.8% 0.288 302.321);
--color-rose-800: oklch(45.5% 0.188 13.697);
--color-amber-800: oklch(47.3% 0.137 46.201);
--color-blue-800: oklch(42.4% 0.199 265.638);
--tw-ring-offset-shadow: 0 0 #0000;
--color-blue-100: oklch(93.2% 0.032 255.585);
--color-slate-800: oklch(27.9% 0.041 260.031);
--color-emerald-900: oklch(37.8% 0.077 168.94);
--color-rose-50: oklch(96.9% 0.015 12.422);
--color-amber-500: oklch(76.9% 0.188 70.08);
--color-emerald-950: oklch(26.2% 0.051 172.552);
--color-slate-950: oklch(12.9% 0.042 264.695);
--color-rose-500: oklch(64.5% 0.246 16.439);
--color-slate-100: oklch(96.8% 0.007 247.896);
--color-emerald-500: oklch(69.6% 0.17 162.48);
--color-blue-900: oklch(37.9% 0.146 265.522);
--color-rose-700: oklch(51.4% 0.222 16.935);
--color-emerald-50: oklch(97.9% 0.021 166.113);
--color-indigo-500: oklch(58.5% 0.233 277.117);
--color-purple-50: oklch(97.7% 0.014 308.299);
--color-blue-600: oklch(54.6% 0.245 262.881);
--color-teal-300: oklch(85.5% 0.138 181.071);
--tw-border-style: solid;
--color-blue-200: oklch(88.2% 0.059 254.128);
--color-blue-50: oklch(97% 0.014 254.604);
--color-black: #000;
--color-emerald-400: oklch(76.5% 0.177 163.223);
--color-teal-200: oklch(91% 0.096 180.426);
--color-purple-700: oklch(49.6% 0.265 301.924);
--color-blue-950: oklch(28.2% 0.091 267.935);
--color-amber-50: oklch(98.7% 0.022 95.277);
--color-emerald-800: oklch(43.2% 0.095 166.913);
--color-amber-200: oklch(92.4% 0.12 95.746);
```

### Spacing

```css
--spacing: 0.25rem;
--tw-space-y-reverse: 0;
```

### Typography

```css
--text-2xl: 1.5rem;
--text-lg: 1.125rem;
--text-base--line-height: calc(1.5 / 1);
--font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono",
      "Courier New", monospace;
--tracking-wider: 0.05em;
--text-lg--line-height: calc(1.75 / 1.125);
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue",
      "Noto Sans", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji",
      "Segoe UI Symbol", "Noto Color Emoji";
--font-weight-bold: 700;
--text-xs--line-height: calc(1 / 0.75);
--default-font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue",
      "Noto Sans", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji",
      "Segoe UI Symbol", "Noto Color Emoji";
--text-xl: 1.25rem;
--leading-relaxed: 1.625;
--leading-snug: 1.375;
--font-weight-black: 900;
--text-2xl--line-height: calc(2 / 1.5);
--text-xl--line-height: calc(1.75 / 1.25);
--font-weight-semibold: 600;
--text-sm: 0.875rem;
--leading-tight: 1.25;
--font-weight-extrabold: 800;
--text-sm--line-height: calc(1.25 / 0.875);
--text-3xl--line-height: calc(2.25 / 1.875);
--text-3xl: 1.875rem;
--text-xs: 0.75rem;
--font-weight-medium: 500;
--font-weight-normal: 400;
--font-serif: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
--text-base: 1rem;
--default-mono-font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono",
      "Courier New", monospace;
--tracking-tight: -0.025em;
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
--radius: 0.5rem;
--radius-sm: calc(0.5rem - 4px);
--radius-2xl: 1rem;
--radius-3xl: 1.5rem;
--radius-xs: 0.125rem;
```

### Other

```css
--background: 216 33% 97%;
--input: 214.3 31.8% 91.4%;
--tw-animation-delay: 0s;
--tw-outline-style: solid;
--tw-animation-direction: normal;
--tw-enter-scale: 1;
--tw-gradient-from: rgba(0, 0, 0, 0);
--tw-gradient-to: rgba(0, 0, 0, 0);
--tw-exit-rotate: 0;
--container-sm: 24rem;
--tw-exit-translate-y: 0;
--tw-gradient-via-position: 50%;
--container-lg: 32rem;
--tw-gradient-to-position: 100%;
--default-transition-duration: 150ms;
--animate-pulse: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
--tw-gradient-from-position: 0%;
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--default-transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
--tw-animation-iteration-count: 1;
--tw-exit-opacity: 1;
--tw-animation-fill-mode: none;
--tw-exit-blur: 0;
--tw-translate-z: 0;
--tw-gradient-via: rgba(0, 0, 0, 0);
--tw-exit-translate-x: 0;
--container-3xl: 48rem;
--tw-translate-y: 0;
--blur-md: 12px;
--animate-spin: spin 1s linear infinite;
--container-4xl: 56rem;
--tw-enter-translate-x: 0;
--tw-divide-y-reverse: 0;
--container-2xl: 42rem;
--tw-exit-scale: 1;
--tw-translate-x: 0;
--tw-enter-rotate: 0;
--tw-enter-translate-y: 0;
--tw-enter-blur: 0;
--tw-enter-opacity: 1;
--container-7xl: 80rem;
--blur-sm: 8px;
```

### Semantic

```css
--color-amber-400: oklch(82.8% 0.189 84.429);
--color-amber-600: oklch(66.6% 0.179 58.318);
--color-amber-800: oklch(47.3% 0.137 46.201);
--color-amber-500: oklch(76.9% 0.188 70.08);
--color-amber-50: oklch(98.7% 0.022 95.277);
--color-amber-200: oklch(92.4% 0.12 95.746);
--destructive: 351 54% 42%;
--destructive-foreground: 0 0% 100%;
--color-blue-700: oklch(48.8% 0.243 264.376);
--color-blue-300: oklch(80.9% 0.105 251.813);
--color-blue-800: oklch(42.4% 0.199 265.638);
--color-blue-100: oklch(93.2% 0.032 255.585);
--color-blue-900: oklch(37.9% 0.146 265.522);
--color-blue-600: oklch(54.6% 0.245 262.881);
--color-blue-200: oklch(88.2% 0.059 254.128);
--color-blue-50: oklch(97% 0.014 254.604);
--color-blue-950: oklch(28.2% 0.091 267.935);
```

## Transitions & Animations

**Easing functions:** `cubic-bezier(0.4, 0, 0.2, 1)`

**Durations:** `0.15s`, `0.2s`

### Common Transitions

```css
transition: all;
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), outline-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-from 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-via 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-to 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), outline-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-from 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-via 0.15s cubic-bezier(0.4, 0, 0.2, 1), --tw-gradient-to 0.15s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.15s cubic-bezier(0.4, 0, 0.2, 1), transform 0.15s cubic-bezier(0.4, 0, 0.2, 1), translate 0.15s cubic-bezier(0.4, 0, 0.2, 1), scale 0.15s cubic-bezier(0.4, 0, 0.2, 1), rotate 0.15s cubic-bezier(0.4, 0, 0.2, 1), filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), -webkit-backdrop-filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), backdrop-filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), display 0.15s cubic-bezier(0.4, 0, 0.2, 1), content-visibility 0.15s cubic-bezier(0.4, 0, 0.2, 1), overlay 0.15s cubic-bezier(0.4, 0, 0.2, 1), pointer-events 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: transform 0.15s cubic-bezier(0.4, 0, 0.2, 1), translate 0.15s cubic-bezier(0.4, 0, 0.2, 1), scale 0.15s cubic-bezier(0.4, 0, 0.2, 1), rotate 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
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
  background-color: rgb(245, 247, 250);
  color: rgb(23, 41, 64);
  font-size: 12px;
  font-weight: 600;
  padding-top: 0px;
  padding-right: 12px;
  border-radius: 6px;
}
```

### Cards (51 instances)

```css
.cards {
  background-color: rgb(255, 255, 255);
  border-radius: 16px;
  box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px;
  padding-top: 0px;
  padding-right: 0px;
}
```

### Inputs (1 instances)

```css
.inputs {
  color: rgb(23, 41, 64);
  border-color: rgb(226, 232, 240);
  border-radius: 6px;
  font-size: 12px;
  padding-top: 4px;
  padding-right: 12px;
}
```

### Links (4 instances)

```css
.links {
  color: rgb(96, 111, 133);
  font-size: 12px;
  font-weight: 500;
}
```

### Navigation (2 instances)

```css
.navigation {
  color: rgb(96, 111, 133);
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
  color: rgb(96, 111, 133);
  font-size: 14px;
  font-weight: 600;
  padding-top: 12px;
  padding-right: 4px;
  border-color: rgb(14, 107, 113);
  border-radius: 0px;
}
```

### Switches (8 instances)

```css
.switches {
  background-color: rgb(226, 232, 240);
  border-radius: 6px;
  border-color: rgb(226, 232, 240);
}
```

## Component Clusters

Reusable component instances grouped by DOM structure and style similarity:

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: oklab(0.999994 0.0000455678 0.0000200868 / 0.85);
  color: rgb(23, 41, 64);
  padding: 0px 0px 0px 0px;
  border-radius: 0px;
  border: 0px 0px 1px solid rgb(226, 232, 240);
  font-size: 16px;
  font-weight: 400;
```

### Button — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: oklab(0.481727 -0.0724493 -0.0302838 / 0.05);
  color: rgb(14, 107, 113);
  padding: 0px 14px 0px 14px;
  border-radius: 3.35544e+07px;
  border: 1px solid oklab(0.481726 -0.0724493 -0.0302838 / 0.3);
  font-size: 12px;
  font-weight: 600;
```

### Button — 79 instances, 2 variants

**Variant 1** (41 instances)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(14, 107, 113);
  padding: 12px 4px 12px 4px;
  border-radius: 0px;
  border: 0px 0px 2px solid rgb(14, 107, 113);
  font-size: 14px;
  font-weight: 600;
```

**Variant 2** (38 instances)

```css
  background: rgb(245, 247, 250);
  color: rgb(23, 41, 64);
  padding: 0px 12px 0px 12px;
  border-radius: 6px;
  border: 1px solid rgb(226, 232, 240);
  font-size: 12px;
  font-weight: 600;
```

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(255, 255, 255);
  color: rgb(23, 41, 64);
  padding: 10px 10px 10px 10px;
  border-radius: 16px;
  border: 1px solid rgb(226, 232, 240);
  font-size: 16px;
  font-weight: 400;
```

### Button — 9 instances, 3 variants

**Variant 1** (1 instance)

```css
  background: rgb(14, 107, 113);
  color: rgb(255, 255, 255);
  padding: 6px 12px 6px 12px;
  border-radius: 12px;
  border: 0px solid rgb(226, 232, 240);
  font-size: 12px;
  font-weight: 700;
```

**Variant 2** (4 instances)

```css
  background: rgb(241, 245, 249);
  color: rgb(23, 41, 64);
  padding: 6px 12px 6px 12px;
  border-radius: 12px;
  border: 0px solid rgb(226, 232, 240);
  font-size: 12px;
  font-weight: 700;
```

**Variant 3** (4 instances)

```css
  background: rgb(226, 232, 240);
  color: rgb(23, 41, 64);
  padding: 0px 0px 0px 0px;
  border-radius: 3.35544e+07px;
  border: 1px solid rgba(0, 0, 0, 0);
  font-size: 12px;
  font-weight: 400;
```

### Button — 55 instances, 4 variants

**Variant 1** (11 instances)

```css
  background: rgb(14, 107, 113);
  color: rgb(255, 255, 255);
  padding: 4px 12px 4px 12px;
  border-radius: 3.35544e+07px;
  border: 0px solid rgb(226, 232, 240);
  font-size: 12px;
  font-weight: 700;
```

**Variant 2** (2 instances)

```css
  background: rgb(14, 107, 113);
  color: rgb(255, 255, 255);
  padding: 0px 4px 0px 4px;
  border-radius: 6px;
  border: 0px solid rgb(226, 232, 240);
  font-size: 12px;
  font-weight: 600;
```

**Variant 3** (6 instances)

```css
  background: rgb(245, 247, 250);
  color: rgb(23, 41, 64);
  padding: 0px 4px 0px 4px;
  border-radius: 0px;
  border: 1px solid rgb(226, 232, 240);
  font-size: 12px;
  font-weight: 600;
```

**Variant 4** (36 instances)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(23, 41, 64);
  padding: 0px 0px 0px 0px;
  border-radius: 0px;
  border: 0px solid rgb(226, 232, 240);
  font-size: 16px;
  font-weight: 700;
```

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(23, 41, 64);
  padding: 32px 32px 32px 32px;
  border-radius: 24px;
  border: 1px solid oklab(0.481727 -0.0724493 -0.0302838 / 0.2);
  font-size: 16px;
  font-weight: 400;
```

### Card — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(255, 255, 255);
  color: rgb(23, 41, 64);
  padding: 20px 20px 20px 20px;
  border-radius: 16px;
  border: 1px solid rgb(226, 232, 240);
  font-size: 16px;
  font-weight: 400;
```

### Button — 4 instances, 1 variant

**Variant 1** (4 instances)

```css
  background: rgb(245, 247, 250);
  color: rgb(23, 41, 64);
  padding: 8px 12px 8px 12px;
  border-radius: 6px;
  border: 1px solid rgb(226, 232, 240);
  font-size: 12px;
  font-weight: 600;
```

### Card — 36 instances, 1 variant

**Variant 1** (36 instances)

```css
  background: rgb(255, 255, 255);
  color: rgb(23, 41, 64);
  padding: 0px 0px 0px 0px;
  border-radius: 16px;
  border: 1px solid oklab(0.928979 -0.00309899 -0.012155 / 0.8);
  font-size: 16px;
  font-weight: 400;
```

## Layout System

**2 grid containers** and **597 flex containers** detected.

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
| row/nowrap | 435x |
| row/wrap | 39x |

**Gap values:** `4px`, `6px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`

## Accessibility (WCAG 2.1)

**Overall Score: 100%** — 170 passing, 0 failing color pairs

### Passing Color Pairs

| Foreground | Background | Ratio | Level |
|------------|------------|-------|-------|
| `#172940` | `#f5f7fa` | 13.71:1 | AAA |
| `#007a55` | `#ecfdf5` | 5.09:1 | AA |
| `#1447e6` | `#eff6ff` | 6.28:1 | AA |
| `#314158` | `#f1f5f9` | 9.45:1 | AAA |
| `#172940` | `#ffffff` | 14.71:1 | AAA |
| `#ffffff` | `#0e6b71` | 6.25:1 | AA |
| `#172940` | `#f1f5f9` | 13.43:1 | AAA |
| `#12635a` | `#e5f5f2` | 6.31:1 | AA |

## Design System Score

**Overall: 93/100 (Grade: A)**

| Category | Score |
|----------|-------|
| Color Discipline | 92/100 |
| Typography Consistency | 80/100 |
| Spacing System | 100/100 |
| Shadow Consistency | 90/100 |
| Border Radius Consistency | 90/100 |
| Accessibility | 100/100 |
| CSS Tokenization | 100/100 |

**Strengths:** Tight, disciplined color palette, Well-defined spacing scale, Clean elevation system, Consistent border radii, Strong accessibility compliance, Good CSS variable tokenization

## Gradients

**2 unique gradients** detected.

| Type | Direction | Stops | Classification |
|------|-----------|-------|----------------|
| linear | to right top | 2 | brand |
| linear | to right bottom | 3 | bold |

```css
background: linear-gradient(to right top, rgb(14, 107, 113) 0%, oklch(0.596 0.145 163.225) 100%);
background: linear-gradient(to right bottom, oklab(0.481727 -0.0724493 -0.0302838 / 0.05) 0%, rgb(255, 255, 255) 50%, rgb(255, 255, 255) 100%);
```

## Z-Index Map

**2 unique z-index values** across 1 layers.

| Layer | Range | Elements |
|-------|-------|----------|
| sticky | 10,40 | div.m.a.x.-.w.-.3.x.l. .f.l.e.x. .f.l.e.x.-.c.o.l. .g.a.p.-.3. .r.e.l.a.t.i.v.e. .z.-.1.0, header.b.o.r.d.e.r.-.b. .b.g.-.c.a.r.d./.8.5. .b.a.c.k.d.r.o.p.-.b.l.u.r.-.m.d. .s.t.i.c.k.y. .t.o.p.-.0. .z.-.4.0. .s.h.a.d.o.w.-.x.s |

## SVG Icons

**18 unique SVG icons** detected. Dominant style: **outlined**.

| Size Class | Count |
|------------|-------|
| xs | 8 |
| sm | 10 |

**Icon colors:** `currentColor`

## Motion Language

**Feel:** mixed · **Scroll-linked:** yes

### Duration Tokens

| name | value | ms |
|---|---|---|
| `xs` | `150ms` | 150 |
| `sm` | `200ms` | 200 |

### Easing Families

- **custom** (227 uses) — `cubic-bezier(0.4, 0, 0.2, 1)`

### Keyframes In Use

| name | kind | properties | uses |
|---|---|---|---|
| `pulse` | fade | opacity | 1 |

## Component Anatomy

### button — 148 instances

**Slots:** label, icon
**Variants:** outline · primary
**Sizes:** xs · md · sm · medium

| variant | count | sample label |
|---|---|---|
| outline | 103 | Profile:
uap (Combination · Barrier & Da |
| primary | 44 | Catalog & Explore |
| default | 1 | Barrier Lipids (Ceramides) |

### card — 40 instances

**Slots:** media
**Variants:** primary
**Sizes:** md · sm

| variant | count | sample label |
|---|---|---|
| primary | 37 | 576 FORMULAS WITH FULL INCI
·
2,502 inde |
| default | 3 | ✨
Formulation Studio
PRO · MULTI-DOMAIN
 |

## Brand Voice

**Tone:** neutral · **Pronoun:** third-person · **Headings:** Title Case (tight)

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
| Avg saturation | 0.546 |
| Shadow profile | soft |
| Avg shadow blur | 0px |
| Max radius | 24px |
| backdrop-filter in use | no |
| Gradients | 2 |

## Component Library

**Detected:** `shadcn/ui` (confidence 0.65)

Evidence:
- shadcn css tokens

Also considered: tailwind-ui (0.54), tailwindcss (0.3)

## Quick Start

To recreate this design in a new project:

2. **Import CSS variables:** Copy `variables.css` into your project
3. **Tailwind users:** Use the generated `tailwind.config.js` to extend your theme
4. **Design tokens:** Import `design-tokens.json` for tooling integration
