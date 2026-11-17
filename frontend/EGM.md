# frontend

## Overview
Vue 3 + Vite + Tailwind CSS v4 SPA ("skintellect-frontend" per `package.json:name`): a science-grounded skincare formulation explorer. This directory holds the build/tooling surface (Vite, TypeScript, Tailwind v4 via `@tailwindcss/vite`, `package.json`, `index.html`) plus the `src` application tree; build artifacts land in `dist/` (pruned from documentation).

## Interface
### Build & Tooling Sources (direct files)
- `package.json` (`package.json:scripts`): `dev` = `vite` (dev server), `build` = `vue-tsc -b && vite build` (type-check then bundle), `preview` = `vite preview`. Runtime dependencies: `vue ^3.5.13`, `vue-router ^4.6.4`, `reka-ui ^2.11` (headless primitives), `class-variance-authority`, `clsx`, `tailwind-merge`, `@vueuse/core`, `lucide-vue-next`, `marked`, `dompurify`, `vue-sonner`, `@fontsource/red-hat-display`, `@fontsource/red-hat-text`, `@fontsource/red-hat-mono` (imported by the CSS entry); devDependencies: `vite ^6.0.3`, `vue-tsc`, `typescript ^5.7.2`, `tailwindcss ^4` + `@tailwindcss/vite` (CSS-first Tailwind, no config file), `tw-animate-css` (animation utilities), `@vitejs/plugin-vue`
- `vite.config.ts` (`vite.config.ts:defineConfig`): `@vitejs/plugin-vue` + `@tailwindcss/vite` plugins; path alias `'@'` → `./src` (`vite.config.ts:resolve.alias`); dev server on port `5173` with proxy `'/api'` → `http://127.0.0.1:8000` and `changeOrigin: true` (`vite.config.ts:server.proxy`); production build outputs to `dist/` with `emptyOutDir: true` (`vite.config.ts:build`) and splits node_modules into semantic vendor chunks via `manualChunks` (`vite.config.ts:build.rollupOptions.output`): `vendor-vue` (vue/vue-router/@vue/@vueuse), `vendor-reka` (reka-ui), `vendor-markdown` (marked/dompurify), everything else → `vendor-misc`; route views load lazily (one chunk per view) via the router
- `src/assets/index.css` (Tailwind CSS entry, Tailwind v4 CSS-first): `@import "tailwindcss"` + `@import "tw-animate-css"`; `@custom-variant dark` for class-based dark mode; `:root` holds the semantic HSL variables (Manila is the shipped surface: `:root` IS the light theme; no `.dark` block exists); `@theme inline` maps them to Tailwind tokens (`background`, `foreground`, `primary`, `secondary`, `destructive`, `muted`, `accent`, `popover`, `card`, `border`, `input`, `ring`), derives `--radius-sm/md/lg/xl` from `--radius`, and defines the `evidence.*` token family (`verified #246e3a`, `source #215c78`, `unknown #4d4641`, `negative #90302e`, `mixed #554077` with `-bg` variants). The hallmark-retheme layer also lives here: `@theme static` motion tokens (`--duration-feedback/state/moment/stagger`, `--ease-entry/move`), custom `@utility` classes (`key-moulded`, `enter-rise-sm`, `stagger-entry`, `span-sweep`, `feedback`), `--scrim`, `--shadow-card/lift`, and the `--font-display/sans/outlier` faces loaded from the `@fontsource/red-hat-*` imports. Local customized variant class strings live outside generated files in `src/lib/evidence.ts`
- `index.html`: SPA entry; `#app` mount div and `/src/main.ts` module script (`index.html:10-11`); `<title>Skintellect - Honest Science-Grounded Moisturizer Intelligence</title>` (line 7); body carries base theme classes (`bg-background font-sans antialiased text-foreground`, line 9)
- `tsconfig.json`: `strict: true`, `noEmit: true`, `isolatedModules: true`, `moduleResolution: 'bundler'`, path mapping `'@/*' → ['src/*']` (`tsconfig.json:paths`), includes `src/**/*.{ts,d.ts,tsx,vue}`
- `tsconfig.node.json`: composite project scoped to `vite.config.ts` only (`tsconfig.node.json:include`)
- `components.json` (`components.json`): shadcn-vue generator config — `style: 'default'`, Tailwind css entry `src/assets/index.css`, aliases `components → @/components`, `ui → @/components/ui`, `utils → @/lib/utils`

### Child Contract
- src: [./src/EGM.md](./src/EGM.md) - Application source: `main.ts` bootstrap, `App.vue` root state owner, `components/` (ui primitives + compare/explore/graph/research features), `lib/` (API client, types, utils)

## Invariants
- The `'@'` alias must stay aligned across three sources: `vite.config.ts:resolve.alias`, `tsconfig.json:paths` (`@/* → src/*`), and the shadcn-vue `components.json:aliases`
- The shadcn-vue CLI overwrites generated files under `src/components/ui/`; the locally customized evidence variants (`Badge` `verified|source|unknown|negative|mixed`) are extracted to `src/lib/evidence.ts` (which exports `evidenceBadgeVariants`) and re-attached by import after any CLI re-pull — never re-inline the class strings (`Button` has no `evidence` variant; its variants are `default|destructive|outline|secondary|ghost|link`)
- Semantic color tokens require matching CSS variables (e.g. `--primary`, `--background`, `--radius`) declared in the Tailwind CSS entry `src/assets/index.css`; components reference them only through Tailwind utility classes; animation utilities (`animate-in/out`, `fade-in-0`, …) come from the imported `tw-animate-css` package and are live
- Backend origin contract: in dev, all `/api` requests are proxied to `http://127.0.0.1:8000` (`vite.config.ts:server.proxy`); `src/lib/api.ts` uses relative `BASE_URL = ''` so production hosting must reverse-proxy `/api` to the FastAPI backend
- `npm run build` runs `vue-tsc -b` first: TypeScript strict errors (including `.vue` template type errors) fail the build; there is no unit test runner configured for this package

## Side Effects
- Dev server: binds port `5173` and forwards `/api` traffic to the backend at `http://127.0.0.1:8000` (`vite.config.ts:server`)
- Build: writes the production bundle to `dist/`, deleting its previous contents first (`emptyOutDir: true`, `vite.config.ts:build`); `vue-tsc -b` emits `.tsbuildinfo` files (`tsconfig.tsbuildinfo`, `tsconfig.node.tsbuildinfo`) alongside the tsconfigs

## System Verification
- Run (from `frontend/`): `npm run build`
- Cross-cutting UI semantics check (from repository root): `node tests/check_ui_semantics.js`
- No unit test runner is configured for the frontend
