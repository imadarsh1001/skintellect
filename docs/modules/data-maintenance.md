# Catalog maintenance and preparation

Maintenance writes to stored data. Use `SKINTELLECT_DB_PATH` to select an existing
catalog and retain a database backup before running modifying commands.

| Owner | Responsibility |
| --- | --- |
| [database.py](../../src/skintellect/database.py) | SQLite transactions, domain schema upgrades, research metadata and quality audit |
| [ingestion/maintenance.py](../../src/skintellect/ingestion/maintenance.py) | Audit, cleaning, demonstration seeding and human completeness verification |
| [research/preparation.py](../../src/skintellect/research/preparation.py) | Resumable review extraction and embedding preparation |
| [research/jobs.py](../../src/skintellect/research/jobs.py) | Job state, cancellation and restart recovery |
| `research/upgrades.py` (retired) | Model-output migration, validation and optional activation |
| [research/study.py](../../src/skintellect/research/study.py) | Prepared cohort selection and readiness |

```powershell
python -m skintellect.ingestion.maintenance --help
python -m skintellect.database --help
python -m skintellect.research.preparation --help
python -m skintellect.research.upgrades --help
python -m skintellect.research.study --help
```

Maintenance exposes `audit`, `clean`, `seed` and `verify`. Verification requires a
product ID, `--source` and `--reviewer`; it records an exact formula hash and does
not certify safety. Seeding adds demonstration products, not collected evidence.

The database command exposes `schema`, `metadata` and `audit`. Its quality audit
can initialize metadata; use `scripts.audit_workspace` for read-only integrity checks.
Preparation/provider upgrades may make billable calls and persist partial results.
The `/progress` dashboard provides bounded job controls. Run it with one API worker.

Raw inputs are preserved under [data/raw/](../../data/raw/); generated outputs belong
in [data exports](../../data/README.md) or [reports](../../reports/README.md).
