# Workflow

1. **Default: commit straight to `main`.** Meaningful conventional messages (`feat(ui): …`, `fix(api): …`, `ai: …`). CI gates (`build`, `scripts/check.py`, `tests/check_ui_semantics.js`, `tests/ui_smoke.py`) protect main — a bad commit gets `git revert`-ed, not debated.
2. **Branch only for** a pre-merge review or a discardable experiment. Name it after the outcome (`session-delete`, `copilot-product-context`), open the PR, and **delete the branch immediately after merge**.
3. **Big changes** (new capability, multi-surface, contract change): an openspec plan first (proposal + tasks — nothing else), then the work, usually on main. Grilling/ADRs only on genuine forks (`docs/adr/`).
4. **Docs ship with the change that touches them**: `PRODUCT.md`, `frontend/DESIGN.md`, `GLOSSARY.md` never drift.
