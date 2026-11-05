# Source layout and migration

Runtime code is owned by one installable package:

```text
src/skintellect/
  __main__.py, cli.py       command parsing and dispatch
  config.py                local environment and paths
  database.py              transactions, migrations, quality metadata
  gemini.py                shared provider transport, budgets and cache
  api/                     startup and HTTP routes
  catalog/                 products, ingredients, personas, recommendations, models
  formulation/             scoring, formula analysis, routine checks, models
  research/                assistant, search, alternatives, reviews, retrieval,
                           evidence, references, connections, labels, preparation,
                           jobs, study, upgrades, models and provider-backed steps
  ingestion/               PubChem compound lookup and catalog maintenance (crawlers decoupled)
  agents/                  board, specialist implementations, detective, model adapter
  reporting.py             Markdown and standalone HTML reporting
  mcp.py                   local read-only MCP transport
  web/templates/           four served HTML pages
  web/static/              live JavaScript, CSS and vendored Vue
```

Shared decisions now have explicit owners: `catalog/store.py` for selected-catalog
reads and cache lifetime; `formulation/ingredient_facts.py` for matching facts;
`formulation/scoring.py` for canonical persona match and clinical Darmeto fit scoring;
`research/review_store.py` for review preparation identity and accepted observations;
and `research/passage_index.py` for usable saved vectors and repair eligibility.
See [architecture](ARCHITECTURE.md) and the [domain glossary](../GLOSSARY.md).

Tests, developer/evaluation scripts, docs, mutable data, reports and backups remain
outside `src/`. Reference notes are immutable package data under `research/`.
The root [experiments/](../experiments/README.md) area holds advanced-study plans
and future opt-in implementations for the LangGraph specialist board,
label-image transcription, Ingredient CSI and Standalone Formula Lab.
The runtime package does not depend on this area;
the ingredient relationship graph remains part of the main buyer-facing scope.
The existing database stays at its original location; no catalog migration or
preparation job is run as part of this source reorganization.

## Replaced locations

| Previous location | Current owner |
| --- | --- |
| `agents.csi_detective` | `skintellect.agents.detective` |
| `agents.formulator_agent` | `skintellect.agents.formulator` |
| `agents.judge_agent` | `skintellect.agents.judge` |
| `agents.llm_client` | `skintellect.agents.llm` |
| `agents.mcp_server` | `skintellect.mcp` |
| `agents.microbiome_agent` | `skintellect.agents.microbiome` |
| `agents.models` | `skintellect.api.agents` |
| `agents.orchestrator` | `skintellect.agents.board` |
| `agents.router` | `skintellect.api.agents` |
| `agents.safety_critic_agent` | `skintellect.agents.safety_critic` |
| `analysis.audit_workspace` | `scripts.audit_workspace` |
| `analysis.evaluate_release` | `scripts.evaluate_release` |
| `analysis.evaluate_research` | `scripts.check_query_parser` |
| `analysis.evaluate_review_nlp` | `scripts.evaluate_review_nlp` |
| `analysis.recommender` | `skintellect.catalog.recommendations` |
| `analysis.reports` | `skintellect.reporting` |
| `backend.api` | `skintellect.api.app` |
| `backend.models` | `skintellect.catalog.models` |
| `backend.research_api` | `skintellect.api.research` |
| `backend.services.catalog_service` | `skintellect.catalog.products` |
| `backend.services.dupe_service` | `skintellect.research.alternatives` |
| `backend.services.formula_service` | `skintellect.formulation.formulas` |
| `backend.services.gemini_research` | `skintellect.research.model_steps` |
| `backend.services.hybrid_retrieval` | `skintellect.research.retrieval` |
| `backend.services.ingredient_service` | `skintellect.catalog.ingredients` |
| `backend.services.label_reader` | `skintellect.research.labels` |
| `backend.services.preparation_jobs` | `skintellect.research.jobs` |
| `backend.services.reference_library` | `skintellect.research.references` |
| `backend.services.relationship_graph` | `skintellect.research.connections` |
| `backend.services.research_service` | `skintellect.research.service` |
| `backend.services.routine_service` | `skintellect.formulation.routines` |
| `core.config` | `skintellect.config` |
| `core.environment` | `skintellect.config` |
| `core.evidence` | `skintellect.research.evidence` |
| `core.gemini` | `skintellect.gemini` |
| `core.personas` | `skintellect.catalog.personas` |
| `core.research_models` | `skintellect.research.models` |
| `core.scoring_engine` | `skintellect.formulation.scoring` |
| `core.taxonomy` | `skintellect.catalog.taxonomy` |
| `ingestion.pubchem_connector` | `skintellect.ingestion.pubchem` |
| `ingestion.queue_worker` | `skintellect.ingestion.queue` |
| `ingestion.skinsort_collector` | `skintellect.ingestion.crawler` |
| `pipeline.ai_pipeline` | `skintellect.research.preparation` |
| `pipeline.audit_data` | `skintellect.ingestion.maintenance` |
| `pipeline.clean_data` | `skintellect.ingestion.maintenance` |
| `pipeline.enrich_ingredients` | `skintellect.ingestion.pubchem` |
| `pipeline.foundation` | `skintellect.database` |
| `pipeline.migrations` | `skintellect.database` |
| `pipeline.research_release` | `skintellect.research.study` |
| `pipeline.seed_multidomain` | `skintellect.ingestion.maintenance` |
| `pipeline.upgrade_embeddings` | `skintellect.research.upgrades` |
| `pipeline.upgrade_review_aspects` | `skintellect.research.upgrades` |
| `pipeline.verify_formula` | `skintellect.ingestion.maintenance` |

`research_service.py` was split: catalog record loading belongs to catalog;
interpretation/eligibility to search; review parsing/insights to reviews;
similarity to alternatives; evidence resolution to evidence; lexical retrieval to
retrieval. Only assistant coordination remains in `research/service.py`.

The domain and research metadata migrations share `database.py` but retain their
separate functions. The two model upgrade workflows share `research/upgrades.py`
and are exposed as `upgrade_embeddings` and `upgrade_reviews`.

Retired code includes the unused DOM frontend (`main.js`, `state.js` and six old
component scripts), placeholder INCIDecoder/CosDNA connectors and their unused
base class, the standalone reference Gemini client, and Python compatibility
bridges. The pre-move source archive is under `backups/before_src_reorganization_*/`.
Historical reports and raw data are retained. Generated report exports moved from
`analysis/outputs/` to `reports/exports/`.

This move preserves the existing scientific and coverage limitations. It does not
turn heuristic scores or demonstration products into validated product evidence.
