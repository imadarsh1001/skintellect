# Application architecture

See [source layout](SOURCE_LAYOUT.md) for module ownership and migration mapping.

HTTP requests enter `skintellect.api`. Routes validate input and call catalog,
formulation, research or agent modules. The CLI and local MCP adapter reuse those
modules without requiring an HTTP server.

The research assistant coordinates interpretation, deterministic eligibility,
review insights, alternatives, retrieval and supported excerpts. Catalog record
loading lives below that workflow; parsing reviews and building a retrieval
corpus do not depend on the assistant. Provider-backed steps share `gemini.py`
for schema validation, cache identity, retries, budgets and telemetry.

`research/preparation.py` processes bounded review/index batches.
`research/jobs.py` persists scheduling state and handles cancellation/recovery.
`research/upgrades.py` migrates model outputs while preserving prior versions.
`research/study.py` defines the focused demonstration and freshness checks.

SQLite transactions and migrations live in `database.py`. The catalog is external
mutable data. Local settings load through `config.py`; installed UI assets and
reference notes resolve relative to the package. The four web pages remain buildless.

Independent tools under `scripts/` evaluate behavior and audit the workspace.
Tests run against disposable synthetic catalogs. Preparation runs with one API
worker; public hosting and independent worker infrastructure are not implemented.

## Shared domain decisions

The [domain glossary](../GLOSSARY.md) defines the terms used by these modules.

- `catalog/store.py` owns selected-catalog reads, common formula interpretation,
  and a display cache keyed by the selected file and its SQLite WAL state.
  `catalog_scope` provides an explicit context for callers/tests; an explicit
  database argument takes precedence. Routine analysis uses one fresh display
  snapshot for both ingredient evidence and product presentation.
- `formulation/ingredient_facts.py` owns ingredient matching knowledge and
  normalization. Formula, catalog and recommendation classification policies
  preserve existing behavior, including historical matching vocabulary. Scoring
  formulas remain distinct; provided ratings remain distinguishable from name matches.
- `research/review_store.py` owns review cleaning, per-product duplicate identity,
  source hashes, extraction identity, cached-span acceptance and observation writes.
  Preparation, progress, summaries, study readiness and upgrades share these decisions.
  Retrieval keeps duplicate raw-review evidence IDs rather than silently collapsing them.
- `research/passage_index.py` owns saved-vector validation, repair eligibility and
  atomic persistence. Indexing, progress, retrieval, study readiness and activation
  accept the same saved work. Ranking and provider transport remain separate.

These modules use the existing SQLite implementation and injected provider test
doubles; no generic storage hierarchy, external worker or new model provider was added.
