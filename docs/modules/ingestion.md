# Catalog Ingestion and Data Management

Catalog management and scientific biochemical enrichment live in [src/skintellect/ingestion/](../../src/skintellect/ingestion/) and [src/skintellect/database.py](../../src/skintellect/database.py).

## Architectural Decoupling

The collection layer is cleanly decoupled:
- **Web Crawling & Queue Workers:** Moved to the private `skintellect-collector` repository to isolate scraping heuristics, session cookies, and rate limiters.
- **In-Tree Ingestion & Chemistry:** The public repository retains scientific PubChem biochemical enrichment (`pubchem.py`) and catalog data quality maintenance/benchmarking (`maintenance.py`).
- **Database & Exports:** Schema initialization, metadata migrations, reproducible audits, and clean JSON exports are managed by `skintellect.database`.

| Module | Implemented behavior |
| --- | --- |
| `skintellect.database` | SQLite schema creation (`init_db`), migrations, audit, and clean JSON export |
| `pubchem.py` | Official NCBI PubChem PUG REST client for molecular weight, SMILES, and CAS resolution |
| `maintenance.py` | Database integrity audit, category canonicalization, and benchmark product seeds |

## In-Tree Commands

```powershell
# Catalog quality and integrity audit
python -m skintellect audit

# Clean and standardize categories and ratings
python -m skintellect clean

# Biochemical ingredient enrichment via PubChem
python -m skintellect.ingestion.pubchem --help

# Export catalog and reviews to JSON
python -m skintellect export
```

## Coverage & Reference Sources

Real catalog coverage is primarily skincare. Hair, body and makeup support includes
schema/taxonomy and demonstration seeds. Source names shown by the app are configured registries
backed by [reference_sources.json](../../src/skintellect/research/reference_sources.json).

See [maintenance](data-maintenance.md) and [local data](../../data/README.md).
