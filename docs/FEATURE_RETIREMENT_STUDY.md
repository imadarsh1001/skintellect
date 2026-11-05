# MVP+ feature retirement study

Reviewed November 4, 2026 against the [confirmed project spec](PROJECT_SPEC.md).
This is an implementation inventory and proposed reduction plan. No runtime
code has been moved, disabled or deleted by this study.

## Recommendation

Yes: the application exposes more features than the current buyer-facing MVP+
needs. Reduce the active product to **Explore, persona matching, comparison,
ingredient education, attributed reviews, research and ingredient relationships**.
Keep ingestion, RAG, review NLP, bounded preparation and evaluation underneath.

Use three treatments:

- **Move to experiments:** the specialist board, label-image transcription,
  Ingredient CSI and Standalone Formula Lab, the four requested study tracks.
- **Retire from the active application:** unrelated legacy features. Preserve a
  recoverable source checkpoint before removal; do not create another live
  legacy package that still needs imports, configuration and maintenance.
- **Simplify:** mixed modules containing both required and extra behavior.
  Keep the required implementation and remove only the unrelated entry points.

Hiding buttons alone will not reduce the code, routes or default checks you
maintain. Conversely, deleting complete feature-named directories would remove
some required behavior. Remove each vertical feature slice together: UI,
client methods, routes, orchestration, exclusive models, commands and tests.

## Implemented features outside the main release

The paths below identify current code, not proposed new files. “Retire” is a
recommendation for a later implementation change, not a claim that the code is
unused or safe to delete without the listed integration work.

| ID | Existing feature and purpose | Current implementation and callers | Recommended treatment |
| --- | --- | --- | --- |
| E1 | Specialist board: specialist commentary, critique, rebuttal and judging. | [agents package](../experiments/specialist_board/), `src/skintellect/api/app.py`, `agent` CLI command, AI Board UI and `experiments/smoke_agents.py`. | Move the board-specific implementation to the agreed experiment track. The current board is sequential; a LangGraph implementation is planned, not already present. Retain shared domain/provider code in the main package. |
| E2 | Label-image transcription: ingredient-photo extraction and comparison with recorded names. | [label reader](../src/skintellect/research/labels.py), `LabelRequest` and `/api/research/label` in [research routes](../src/skintellect/api/research.py), label tab/form in [study page](../src/skintellect/web/templates/study.html) and [study controller](../src/skintellect/web/static/js/study.js), label cases in [release tests](../tests/test_release.py). | Move the existing behavior to the second agreed experiment track. Preserve image validation and uncertainty handling. Remove its upload form and route from the default buyer application when that migration is implemented. |
| E3 | Ingredient CSI: compares tolerated/problematic formulas and ranks candidate ingredients. | `experiments/specialist_board/csi_detective.py`, `/api/agents/csi/investigate`, agent CLI and shared AI Board/CSI modal. | Move into experiments at the project owner's request. Preserve the set-comparison behavior and explainable candidate rankings, while identifying them as hypotheses rather than established allergy or breakout causes. Detach the study from the default buyer interface. |
| E4 | Standalone Formula Lab: accepts arbitrary ingredient text and generates a formula score, compatibility matrices and audit explanations. | [formula analysis](../src/skintellect/formulation/formulas.py), [legacy formula scoring](../src/skintellect/formulation/scoring.py), Formula Lab models, `/api/formula-lab/analyze`, CLI `score`, lab state/modal in the catalog UI. | Move the standalone lab and raw-formula scoring interface into experiments. Preserve its heuristic baseline and shared scoring used by E1/E3. Keep core ingredient facts, recorded-formula inspection and catalog persona matching in the main product; do not duplicate those modules. |
| R3 | Five-step Routine Studio: slots products into a routine and reports co-occurrence/conflicts. | `src/skintellect/formulation/routines.py`, Routine models, `/api/routine/analyze`, routine state, card actions, progress strip and modal in the catalog UI. | Retire from the active product. Preserve ordinary product selection for comparison; routine state is not a substitute for the planned comparison flow. |
| R4 | Standalone HTML/Markdown report generator: produces another interactive product dashboard and routine report. | `src/skintellect/reporting.py`, CLI `report`, plus report-generation calls in `cmd_crawl`, `cmd_enrich`, `cmd_crawl_top`, `cmd_run_suite`, `cmd_clean` and `cmd_worker`. The module contains 3,872 source lines at review time, including its own browser scoring/UI. | High-value retirement candidate: remove this alternative product interface and its callers. Keep engineering evaluation JSON/reports, provenance and source data. Detach report-generation side effects from every retained command, especially maintenance commands. |
| R5 | Local MCP adapter: exposes research operations to external AI clients. | `src/skintellect/mcp.py`, `run-mcp.cmd`, `skinsort-mcp` package entry point, MCP cases in release/architecture tests. | Retire this optional transport from the current deliverable. Keep the domain operations it calls. Remove the launcher and packaging entry point together if the adapter is removed. External client compatibility is not established by this study. |
| R6 | Hosted-model upgrade/activation commands: re-prepare with another model and activate after coverage checks. | `src/skintellect/research/upgrades.py`, model-selection setters, upgrade tests in Gemini/dynamic-decision suites. | Retire the advanced migration/activation workflow. Keep configured model selection, extraction identities, valid-vector checks, stale-result rejection and ordinary preparation. |
| R7 | Standalone raw-review decision endpoint: accepts a small list of caller-supplied review texts and returns typed model observations. | `/api/decisions/reviews`, request models in [research models](../src/skintellect/research/models.py), `decide_reviews` in [model steps](../src/skintellect/research/model_steps.py), dedicated dynamic-decision HTTP cases. No buyer-page caller was found. | Consolidate with the core NLP workflow rather than maintaining another public input surface. Its orchestration wrapper can be retired; retain shared review extraction, open-aspect support, exact-span validation and relevant tests. |

## Mixed features to simplify rather than delete wholesale

| ID | Existing surface | What can leave this phase | What must remain |
| --- | --- | --- | --- |
| S1 | Dedicated prepared-study workspace: `/study`, [study module](../src/skintellect/research/study.py), page/controller and `/api/research/demo`. | Separate study navigation, fixed preferred-product IDs and release-cohort restrictions as the default buyer experience. | A reproducible interview cohort and evaluation support. The study controller currently renders ingredient relationships and references: migrate that required behavior into main product/research views before retiring the page. Move its label-upload behavior to E2. |
| S2 | Dedicated preparation dashboard: `/progress`, [page](../src/skintellect/web/templates/progress.html), [controller](../src/skintellect/web/static/js/progress.js), [jobs](../src/skintellect/research/jobs.py). | A separate full operational destination and extra buyer navigation. Simplify to basic preparation state/usage where needed. | Bounded jobs, progress facts, cancellation/recovery already protecting preparation, and provider usage. Application startup currently calls job recovery; deleting the jobs module would break that path and remove required controls. |
| S3 | Multi-domain/catalog taxonomy: skin, hair, body, makeup and many categories. | Hair/body/makeup browsing, non-moisturizer category choices and unsupported source/guardrail marketing in the initial UI. | Moisturizer filtering, source attribution, existing stored data, seed exclusion and any normalization still used by the core. Metadata describing a possible source is not proof it was collected. |
| S4 | Broad Skintellect crawling and its prioritized background crawl queue. | CLI `crawl`, `crawl-reviews`, `enrich`, `crawl-top`, `run-suite`, `queue-status` and `worker` as current-phase operational workflows; `skintellect-collector/queue.py` after callers are detached. | Existing collected data, required schema initialization, normalization and the explicit Nykaa batch-import path. `skintellect-collector/crawler.py` also owns `init_db` used by test bootstrap and other commands; extract the retained pieces before retiring collection code. The crawl queue is distinct from review/index preparation jobs. |
| S5 | Bulk PubChem enrichment command. | Treat [PubChem enrichment](../src/skintellect/ingestion/pubchem.py) as an optional parked acquisition tool rather than a required MVP+ pipeline. No runtime Python importer was found, but it is an explicit module command. | The core ingredient-science evidence requirement and attribution. Removing a bulk enrichment command must not remove source records or become an excuse to generate unsupported scientific explanations. |
| S6 | Separate CLI recommendation/search implementation. | Duplicate ranking/search behavior in [catalog recommendations](../src/skintellect/catalog/recommendations.py), used by CLI `recommend`/`filter` and the standalone report generator. | Core [catalog product](../src/skintellect/catalog/products.py) selection/persona scoring. Either retain thin CLI calls into the core or retire optional CLI commands; avoid maintaining two changing definitions of buyer matching. |

## Required code that can look like an extra

- **Ingredient relationship projection stays.** [connections](../src/skintellect/research/connections.py)
  and `/api/products/{product_id}/connections` are main-scope behavior. The current
  study view shows related-product paths and technical graph data; completing
  the agreed graph UX is still work, not a reason to discard this implementation.
- **The main research workflow stays.** Assistant coordination, planning,
  retrieval, alternatives, model steps, review corpus and passage index support
  the agreed LangGraph/RAG/NLP goal. LangGraph itself is not implemented yet;
  do not confuse the old specialist board with the main research workflow.
- **Core persona scoring stays.** Product preference scoring in the catalog
  differs from the standalone Formula Lab/board score. Keep ingredient facts,
  aliases, recorded-formula interpretation and source-provided flags.
- **Shared web helpers stay.** [workspace helpers](../src/skintellect/web/static/js/workspace.js)
  and shared workspace CSS support review excerpts, source rendering, filters and
  research UI. Retiring a page does not make its shared assets obsolete.
- **Maintenance integrity stays.** [database migration](../src/skintellect/database.py)
  imports `BENCHMARK_PRODUCTS` from maintenance to identify seeds. Keep seed
  identity metadata, migrations, auditing and explicit formula verification even
  if seed-generation or unrelated acquisition commands are removed.
- **Evaluation stays.** Saved-source checks, parser regressions, review NLP
  evaluation and a manually reviewed interview set are current scope. The
  [release evaluator](../scripts/evaluate_release.py) depends on study readiness:
  make cohort selection explicit or preserve the necessary helper before moving
  study code. Generated evaluation reports are different from R4's buyer dashboard.

## Dependency and verification work for removal

1. Take a verified source checkpoint and record the affected commands/routes.
   Preserve catalogs, Nykaa inputs, credentials, reports and historical backups.
2. Move E1–E4 as complete opt-in experiments, reusing core operations. The
   default application must not import or initialize their implementations.
   Currently `src/skintellect/api/app.py` instantiate the board
   and CSI during import and [app startup](../src/skintellect/api/app.py) always
   registers that router. Detach both, not only the visible buttons.
3. Remove the R3–R7 feature slices after resolving their shared callers. The
   [formulation router](../src/skintellect/api/formulation.py) mixes Formula Lab,
   routine analysis and `/api/dupes/{product_id}`: keep/consolidate the core
   alternatives behavior rather than deleting the router blindly.
4. Simplify S1–S6. Migrate relationship/reference browsing out of the study page;
   retain only needed initialization from old collection code and basic
   preparation/evaluation behavior. Keep one active buyer interface.
5. Update all affected UI state, callbacks, API clients, CLI imports/parsers,
   package entry points, launchers, guides and links in the same change. Removing
   a module while leaving its eager CLI import can break even unrelated commands.
6. Preserve core regression cases in mixed test modules. [release tests](../tests/test_release.py)
   combine core graph/evidence cases with MCP, label and study cases;
   [architecture tests](../tests/test_deep_architecture.py) combine core catalog
   behavior with MCP/routine checks. Do not delete those files wholesale.
   [The standard runner](../scripts/check.py) explicitly runs agent smoke checks;
   move experiment execution out of the default path. Keep one project test tree.
7. Verify public domain operations against disposable catalogs, focused API
   serialization, ordinary browsing/research/graph interactions, installed assets
   and CLI help/imports. Verify experiments separately using provider doubles.
   Check that default imports contain no dependency on the experiments area.

## Small cleanup found alongside the feature inventory

[Catalog models](../src/skintellect/catalog/models.py) contain `AgentBoardRequest`
and `CsiInvestigateRequest` definitions duplicated in the agent routes. Source
and test searches found the active callers using the route-owned definitions,
not these catalog definitions. Remove the unused duplicates with the feature
cleanup; retain the product/persona/ingredient models in that shared file.

## Suggested implementation order

1. Move the four approved experiments and their exclusive code out of the main
   buyer flow. Preserve AI Board, CSI and Formula Lab interfaces within their
   opt-in studies; retire Routine Studio separately.
2. Retire the standalone report dashboard and its duplicate scoring/UI. This
   removes a substantial alternative implementation without sacrificing main
   buyer browsing. Consolidate or retire its legacy recommendation callers.
3. Remove the MCP and advanced model-upgrade transports/workflows, along
   with their exclusive launchers, models and default checks.
4. Migrate the useful study-page graph/reference content, simplify operational
   UI, and detach old collection workflows after retaining required schema code.
5. Continue implementing the agreed Nykaa ingestion, comparison, plain-language
   science and LangGraph research gaps in the smaller active product.

The best next change is a few coherent removals with passing checks, not another
general directory reorganization. The detailed implementation inventory belongs
here; keep the product spec's future-scope note short.

## What was checked

Static inspection covered runtime modules, Python importers including local
imports, HTTP registration, CLI dispatch, catalog/study/research UI callers,
packaging entry points and affected tests/scripts. It excludes dependency internals,
backup copies and generated reports from active-source ownership.

No live provider calls, data imports, browser execution or runtime test run was
performed for this documentation-only study. External callers of removed
interfaces and dynamically constructed references still need verification during
implementation; this is not a blanket safe-delete list.
