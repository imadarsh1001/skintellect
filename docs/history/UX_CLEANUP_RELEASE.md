> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# UX and workspace cleanup

Updated 23 October 2026. This pass improves the prepared research interface and organizes
its generated files. The catalog and research engine retain their existing API contracts.

## Interface changes

- Start here: readable product cards, keyboard-accessible tabs, full-width product evidence,
  review theme tables, paginated quotes, and readable ingredient/source disclosures.
- Ask a question: one primary action, example questions, optional editable filters,
  clear empty/error states, supported quotes, and scoped ingredient alternatives.
- Data progress: understandable task states, coverage, cancellation and reuse of previous
  settings. Model metadata, raw JSON and usage details are collapsed initially.
- Shared styles improve font size, spacing, contrast, navigation and narrow-screen layout.
- A failed related-product request no longer hides loaded review evidence. Retrying lazy
  detail panels replaces earlier failed content. Source strings use text-only rendering.

## Root and parent directory audit

The directory above this project contains three loose files: `aws_lesson_list.csv`,
`aws_saa_003_adrian.ipynb`, and `demo_feature_selection.py`. Their timestamps predate this
implementation. No evidence was found that this work modified them; there is no earlier
hash baseline for those files, so historical authorship cannot be established. They were
left in place. No files outside the project were moved or edited in this cleanup pass.

| Root item | Decision |
| --- | --- |
| `README.md` | Entry point linking documentation, app startup and reports |
| `run-research.cmd`, `run-mcp.cmd` | Keep accessible launchers; suppress generated Python bytecode |
| `app.py`, `main.py`, `personas.py`, `scoring_engine.py` | Retain original entry points and imports |
| `gemini_client.py` | Retain supplied standalone client; relative environment lookup expects this location |
| `API_USAGE_GUIDE.md` | Relocated unchanged to `docs/API_USAGE_GUIDE.md` |
| `test_api.py` | Retain existing HTTP smoke runner and import used by `tests/run_legacy_direct.py` |
| `skintellect_moisturizers.db` | Retain canonical database path used by existing tools |
| `requirements.txt` | Keep dependency installation entry point |

The source comparison uses `backups/before_ux_cleanup_20261023T063025Z/source.zip`,
not Git history (this working directory is not a Git repository). The machine-readable
[file audit](../../reports/latest/workspace-audit.json) lists modified, added, moved and
preserved files; it describes changes since that UX baseline, not earlier release authorship.

## Output organization

26 generated files were relocated from `analysis/` into `reports/latest/`, `reports/history/`,
`reports/previews/`, and `tests/fixtures/`. The manifests in `reports/` preserve original
paths and hashes. Report-path references were updated; several report files therefore
have new hashes even though their recorded evaluation results are unchanged.

24 earlier generated items and two leftover test-browser profiles were quarantined under
`backups/cleanup_quarantine_20261023T071113Z/`. Automatic approval rejected permanent
deletion. Quarantine is reversible and is not deletion. Exact paths are in
[cleanup-result.json](../../reports/cleanup-result.json).

The existing `analysis/outputs/` recommendation deliverables remain because the legacy
exporter actively uses that directory. Source/database restore points are under `backups/`.
Tests use one dedicated temporary workspace and register cleanup before setup can fail.

## Verification and remaining limits

The latest [workspace audit](../../reports/latest/workspace-audit.json) records source syntax,
HTML element/script contracts, documentation links, artifact locations and original-table
preservation. All 82 regression tests and 11 legacy direct-route groups passed. In-process ASGI checks
returned HTTP status 200 for all four pages, five shared/page assets, demo readiness and
progress endpoints. These do not test network transport or browser rendering.

Regression results and the UI limitation are recorded in
[validation](../../reports/latest/ux-cleanup-validation.json) and
[UI smoke status](../../reports/latest/ui-smoke.json).

Installed headless browsers failed before loading the fixture UI in this execution
environment. Visual appearance, browser interactions and mobile overflow are not verified.
The reusable `tests/ui_smoke.py` can run those checks in a working desktop environment.
No Gemini calls are needed for these checks. For commands, see the [workspace guide](../WORKSPACE_GUIDE.md).
