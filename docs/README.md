# Documentation

Use the current guides for supported commands and module ownership. Historical
notes are preserved separately and may describe superseded behavior.

## Current guides

| Guide | Purpose |
| --- | --- |
| [MVP+ specification](PROJECT_SPEC.md) | Confirmed buyer journey, relationship graph, AI goals and acceptance criteria |
| [Feature retirement study](FEATURE_RETIREMENT_STUDY.md) | Implemented extras, shared dependencies and a staged reduction plan |
| [Advanced-study experiments](../experiments/README.md) | LangGraph board, label transcription, Ingredient CSI and Formula Lab study |
| [Development](DEVELOPMENT.md) | Installation, configuration, CLI, checks and contribution rules |
| [Workspace](WORKSPACE_GUIDE.md) | Pages, launchers and file locations |
| [Source layout](SOURCE_LAYOUT.md) | Package ownership and old-to-new migration map |
| [Architecture](ARCHITECTURE.md) | Request flow, feature dependencies and persistence |
| [Visual evidence](UX_VISUAL_GUIDE.md) | Color meanings, review excerpts and visual-verification limits |

## Feature and tool guides

- [Collection and ingredient enrichment](modules/ingestion.md)
- [Catalog maintenance and preparation](modules/data-maintenance.md)
- [Formulation rules and personas](modules/formulation-and-personas.md)
- [Experimental agents and Ingredient CSI](modules/agents.md)
- [Evaluations and reporting](modules/evaluations-and-reporting.md)
- [Developer tools](../scripts/README.md), [local data](../data/README.md),
  and [saved reports](../reports/README.md) (historical backups are archived in the private collector repository)

## Historical context

The [history index](history/README.md) contains prior release notes, provider
experiments, domain plans and reverse-engineering notes. Their metrics and claims
are records of those documents, not current validation. Application endpoints are
listed by the running server at `/docs`; the archived Gemini provider reference
is not an application API guide.
