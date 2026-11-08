# static (Web Static Assets)

## Overview
Static asset root served by FastAPI at `/static` (mounted in `skintellect/api/app.py` from `config.STATIC_DIR`). This blueprint indexes only the documented child contract below. The `css/` (stylesheets `custom.css`, `workspace.css`) and `vendor/` (`vue.global.prod.js` Vue 3 runtime) directories are pruned asset folders without contract files and are intentionally not linked here.

## Subdirectories & Boundaries
- js: [./js/EGM.md](./js/EGM.md) - plain-JS frontend bundles: `window.Studio` shared runtime, `window.API` REST client, Vue 3 Studio app, and the research/study/progress page scripts; documents all same-origin `/api/*` calls, localStorage keys, timers, and text-only rendering invariants.

## Invariants
- Assets here are referenced by URL from the server-rendered templates and by `app.mount("/static", ...)` in `skintellect/api/app.py`; nothing in this directory executes on the server.
- Only `js/` contains documented, code-bearing frontend logic; `css/` and `vendor/` hold passive stylesheets and a third-party runtime bundle.

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
