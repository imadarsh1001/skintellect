# Workspace guide

Start with [development setup](DEVELOPMENT.md) and [source ownership](SOURCE_LAYOUT.md).

Run `run-research.cmd` on this workstation, or install the project and use
`python -m skintellect web`. The default address is http://127.0.0.1:8000.

| Page | Purpose |
| --- | --- |
| `/study` | Prepared three-product demonstration |
| `/research` | Ingredient-constrained research with source excerpts |
| `/progress` | Coverage and bounded preparation jobs |
| `/` | Catalog, ingredient explorer, personas, formula/routine tools and agents |
| `/docs` | Interactive HTTP documentation |

| Location | Contents |
| --- | --- |
| `src/skintellect/` | Runtime Python and packaged web assets |
| `tests/` | Regressions, fixtures, HTTP/direct/agent smoke checks |
| `scripts/` | Offline checks, evaluations and workspace audit |
| `experiments/` | Advanced-study plans: LangGraph board, label transcription, Ingredient CSI and Formula Lab |
| `data/raw/` | Preserved collection snapshots |
| `data/exports/` | Generated catalog, ingredient, review and persona JSON |
| `reports/latest/` | Saved current validation/evaluation snapshots |
| `reports/history/` | Earlier experiments and validation |
| `reports/exports/` | Generated Markdown and standalone HTML reports |
| `docs/` | Current guides and historical design/release notes |
| `backups/` | Local source/data restore points |

The live database remains `skintellect_moisturizers.db` at the checkout root.
No database, credentials, dependencies, reports or backups belong in `src/`.
