# frontend

## Overview
Vue 3 + Vite + Tailwind CSS SPA ("skintellect-frontend" per `package.json:name`): a science-grounded skincare formulation explorer. This directory holds the build/tooling surface (Vite, TypeScript, Tailwind, PostCSS configs, `package.json`, `index.html`) plus the `src` application tree; build artifacts land in `dist/` (pruned from documentation).

## Interface
### Build & Tooling Sources (direct files)
- `package.json` (`package.json:scripts`): `dev` = `vite` (dev server), `build` = `vue-tsc -b && vite build` (type-check then bundle), `preview` = `vite preview`. Runtime dependencies: `vue ^3.5.13`, `radix-vue ^1.9.11` (headless primitives), `class-variance-authority`, `clsx`, `tailwind-merge`, `@vueuse/core`, `lucide-vue-next`, `marked`; devDependencies: `vite ^6.0.3`, `vue-tsc`, `typescript ^5.7.2`, `tailwindcss ^3.4.16`, `tailwindcss-animate` (present as a dependency but **not** registered — see Invariants), `@vitejs/plugin-vue`, `postcss`, `autoprefixer`
- `vite.config.ts` (`vite.config.ts:defineConfig`): `@vitejs/plugin-vue` plugin; path alias `'@'` → `./src` (`vite.config.ts:resolve.alias`); dev server on port `5173` with proxy `'/api'` → `http://127.0.0.1:8000` and `changeOrigin: true` (`vite.config.ts:server.proxy`); production build outputs to `dist/` with `emptyOutDir: true` (`vite.config.ts:build`)
- `tailwind.config.js` (`tailwind.config.js`): `darkMode: ['class']` (line 3); content globs `./index.html` and `./src/**/*.{vue,js,ts,jsx,tsx}` (lines 4-7); theme maps semantic tokens (`border`, `input`, `ring`, `background`, `foreground`, `primary`, `secondary`, `destructive`, `muted`, `accent`, `popover`, `card`) to `hsl(var(--…))` CSS variables (`tailwind.config.js:extend.colors`), adds the `evidence.*` token family (`verified #12635a`, `source #245ba9`, `unknown #805309`, `negative #a63244`, `mixed #6843a8` with `-bg` variants, lines 51-63), and derives `borderRadius.lg/md/sm` from `--radius` (lines 65-69)
- `postcss.config.js` (`postcss.config.js:plugins`): `tailwindcss` + `autoprefixer`
- `index.html`: SPA entry; `#app` mount div and `/src/main.ts` module script (`index.html:10-11`); `<title>Skintellect - Honest Science-Grounded Moisturizer Intelligence</title>` (line 7); body carries base theme classes (`bg-background font-sans antialiased text-foreground`, line 9)
- `tsconfig.json`: `strict: true`, `noEmit: true`, `isolatedModules: true`, `moduleResolution: 'bundler'`, path mapping `'@/*' → ['src/*']` (`tsconfig.json:paths`), includes `src/**/*.{ts,d.ts,tsx,vue}`
- `tsconfig.node.json`: composite project scoped to `vite.config.ts` only (`tsconfig.node.json:include`)
- `components.json` (`components.json`): shadcn-vue generator config — `style: 'default'`, Tailwind css entry `src/assets/index.css`, aliases `components → @/components`, `ui → @/components/ui`, `utils → @/lib/utils` (lines 11-15)

### Child Contract
- src: [./src/EGM.md](./src/EGM.md) - Application source: `main.ts` bootstrap, `App.vue` root state owner, `components/` (ui primitives + compare/explore/graph/research features), `lib/` (API client, types, utils)

## Invariants
- The `'@'` alias must stay aligned across three sources: `vite.config.ts:resolve.alias`, `tsconfig.json:paths` (`@/* → src/*`), and the shadcn-vue `components.json:aliases`
- `tailwindcss-animate` is a devDependency of `package.json` but `tailwind.config.js:plugins` is `[]`, so the `animate-in`/`animate-out` classes used in dialog/select templates and the `animate-collapsible-*` classes in collapsible currently generate no CSS; registering the plugin in `tailwind.config.js` is the fix path for those transitions
- Semantic color tokens require matching CSS variables (e.g. `--primary`, `--background`, `--radius`) declared in the Tailwind CSS entry `src/assets/index.css`; components reference them only through Tailwind utility classes
- Backend origin contract: in dev, all `/api` requests are proxied to `http://127.0.0.1:8000` (`vite.config.ts:server.proxy`); `src/lib/api.ts` uses relative `BASE_URL = ''` so production hosting must reverse-proxy `/api` to the FastAPI backend
- `npm run build` runs `vue-tsc -b` first: TypeScript strict errors (including `.vue` template type errors) fail the build; there is no unit test runner configured for this package

## Side Effects
- Dev server: binds port `5173` and forwards `/api` traffic to the backend at `http://127.0.0.1:8000` (`vite.config.ts:server`)
- Build: writes the production bundle to `dist/`, deleting its previous contents first (`emptyOutDir: true`, `vite.config.ts:build`); `vue-tsc -b` emits `.tsbuildinfo` files (`tsconfig.tsbuildinfo`, `tsconfig.node.tsbuildinfo`) alongside the tsconfigs

## System Verification
- Run (from `frontend/`): `npm run build`
- Cross-cutting UI semantics check (from repository root): `node tests/check_ui_semantics.js`
- No unit test runner is configured for the frontend
