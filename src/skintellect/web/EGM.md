# web (Server-Rendered Frontend Assets)

## Overview
Frontend asset boundary for the FastAPI app: `templates/` holds the server-rendered HTML pages (index, progress, research, study) and `static/` holds the JavaScript/CSS assets they reference. The `templates/` directory is HTML-only and pruned (no contract file); this blueprint indexes the documented static child below.

## Subdirectories & Boundaries
- static: [./static/EGM.md](./static/EGM.md) - static asset root served at `/static`; indexes the JS bundle contract (Studio runtime, API client, Vue app, page scripts). Its `css/` and `vendor/` folders are pruned assets.

## Invariants
- `templates/` pages load bundles by fixed URL: `index.html` loads `/static/vendor/vue.global.prod.js`, `/static/js/api.js`, and `/static/js/app.js`; `research.html`/`study.html`/`progress.html` each load `/static/js/workspace.js` plus their page script, and the workspace pages link `/static/css/workspace.css` (file references, not links to pruned folders).
- HTML page routes are owned by the API layer (`skintellect/api/app.py`: `GET /`, `/progress`, `/study`, `/research`, `/compare`, `/graph`); this directory contributes no Python.
- When `frontend/dist/index.html` exists, `GET /`, `/compare`, and `/graph` serve that built bundle instead of `templates/index.html` (`skintellect/api/app.py:serve_index`).

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
