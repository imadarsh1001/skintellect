# Evaluations, recommendations and reports

Recommendation logic, report generation and developer evaluations have different owners:

| Location | Responsibility |
| --- | --- |
| [catalog/recommendations.py](../../src/skintellect/catalog/recommendations.py) | Existing CLI/report recommendation and filtering logic |
| `reporting.py` (retired in favor of web UI) | Recommendation Markdown and standalone HTML output |
| [scripts/](../../scripts/README.md) | Parser checks, review/retrieval evaluations and workspace audit |
| [reports/](../../reports/README.md) | Generated outputs and preserved evaluation snapshots |

```powershell
python -m skintellect recommend --help
python -m skintellect report --format markdown
python -m skintellect report --format html
python -m scripts.check_query_parser
python -m scripts.evaluate_release --offline
```

Report exports now go to `reports/exports/`, not the retired `analysis/outputs/`.
Original generated reports were preserved during the source move.

The query-parser check uses authored smoke cases. Review evaluation measures either
agreement with supplied labels or agreement between imperfect methods. Prepared-study
retrieval labels are weak, surface-derived labels. These checks do not establish clinical
performance or representative model accuracy. Live evaluation can incur provider calls;
see [tool effects and options](../../scripts/README.md).
