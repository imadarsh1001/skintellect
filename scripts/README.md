# Developer checks and evaluations

These tools run from the checkout root after installing the project with
`pip install -e ".[dev]"` (or `uv pip install -e ".[dev]"`). They are not part of the installed
runtime package. CI invokes `check.py`; tests import the release evaluator.

| Tool | Purpose | Data/provider effects |
| --- | --- | --- |
| `check.py` | Ruff, disposable-catalog regressions, agent smoke and available Node UI checks | Uses synthetic data; disables real provider calls |
| `audit_workspace.py` | Imports, syntax, HTML assets, documentation links and SQLite integrity | Reads the configured catalog; writes the workspace audit report |
| `check_query_parser.py` | 20 authored baseline-query parser smoke cases | No model calls; not a ranking or accuracy benchmark |
| `evaluate_review_nlp.py` | Rule/model aspect-extraction comparison against authored or supplied labels | Default rules mode; Gemini modes can make calls and persist cache entries |
| `evaluate_release.py` | Prepared-study retrieval comparison, review-method agreement and latency | Saves evaluation metadata in the catalog and a JSON report; live mode can make calls |
| `__init__.py` | Package marker for module commands and shared evaluation imports | No behavior |

```powershell
python scripts/check.py
python -m scripts.audit_workspace
python -m scripts.check_query_parser
python -m scripts.evaluate_review_nlp --mode rules
python -m scripts.evaluate_release --offline
```

The release evaluator defaults to live mode when `--offline` is omitted.
Use a disposable catalog copy through `SKINTELLECT_DB_PATH` for evaluations you do
not want to save into the working database. Rule/model agreement and synthetic
smoke results are not human-reviewed evidence of product or model accuracy.

The main suite needs local socket access for asynchronous HTTP tests. It recreates
`.test-work/` and Ruff may recreate `.ruff_cache/`; both are disposable generated
folders. The optional standalone Node command is `node tests/check_ui_semantics.js`.

See [development setup](../docs/DEVELOPMENT.md) and
[evaluation/reporting ownership](../docs/modules/evaluations-and-reporting.md).
