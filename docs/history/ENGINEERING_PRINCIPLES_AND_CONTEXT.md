> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Engineering Principles & Architectural Constitution

> **Authoritative Context Document**  
> *Status: Invariant Foundation (Final Trust / Baseline Ground Truth for All Future AI Sessions)*  
> *Rule: This document serves as the architectural bedrock. Future AI agents must treat these principles as binding truth. They cannot be arbitrarily rewritten or reverted, but may be evolved incrementally as new verified learnings are unlocked.*  
> *Last Updated: October 2026*

## Maintenance update — 23 October 2026

The [development guide](../DEVELOPMENT.md) records the current implementation of
these principles. Shared path fallback logic now lives once in `skintellect.config`;
individual modules import it. The live database remains at the project root.
`ingestion/` and `pipeline/` own the former duplicate crawler/queue/migration
implementations; their legacy paths are compatibility bridges. Generated JSON
goes to `data/exports/`, and executable smoke checks live in `tests/`.

HTTPX is now a declared, managed runtime dependency used by the existing offline
contract tests. `python scripts/check.py` is the standard synthetic validation
command. The standard-library `python -m tests.smoke_api` remains the separate live HTTP
check against the supplied catalog. The original principles below are preserved
as historical context; these verified changes refine their implementation.

---

## 1. The Architectural Constitution

When starting a new session or handing off work to a future AI engineer, **adhere strictly to these 8 foundational principles**:

### Principle I: Stage Decoupling by Lifecycle
The codebase is structured around 5 explicit, decoupled lifecycle stages. Code belonging to one stage must never leak randomly into another or sit as loose, ad-hoc files in the project root:

1. **`ingestion/` (Data Harvesting & External Connectors)**:
   - Contains scrapers, REST clients, and queues for external registries (**Skintellect**, **PubChem**, **INCIDecoder**, **CosDNA**, **CurlScan**).
2. **`pipeline/` (Data Processing, Seeding & Auditing)**:
   - Contains data cleaning (`clean_data.py`), integrity audits (`audit_data.py`), schema migrations (`migrations.py`), and benchmark seed scripts (`seed_multidomain.py`).
3. **`core/` (Clinical Formulation Science & Domain Engines)**:
   - Contains the single source of truth for reverse-engineered scoring formulas (`scoring_engine.py`), dynamic clinical personas (`personas.py`), and multi-domain models (`taxonomy.py`).
4. **`analysis/` (Offline Personalized Ranking & Reporting)**:
   - Contains offline ranking models (`recommender.py`), Markdown/HTML report generators (`reports.py`), and generated outputs (`outputs/`).
5. **`backend/` + `static/` + `templates/` (Interactive Web Application & REST API)**:
   - Contains FastAPI routing (`api.py`), Pydantic models (`models.py`), in-memory cached services (`services/`), and the buildless Vue 3 Single Page Application.
6. **`data/` (Storage Tier)**:
   - Houses the master database (`skintellect_moisturizers.db`) and historical raw data snapshots (`data/raw/`).

---

### Principle II: Single Source of Truth (Zero Duplicate Code)
* **Never create duplicate copies of functional logic.**
* The authoritative clinical scoring mathematics resides solely in [`core/scoring_engine.py`](../../src/skintellect/formulation/scoring.py).
* The authoritative persona models reside solely in [`core/personas.py`](../../src/skintellect/catalog/personas.py).
* All other packages (`backend/`, `analysis/`, `pipeline/`, CLI) MUST import directly from `core`.
* Root proxy files (`scoring_engine.py` and `personas.py`) exist strictly as 1-line re-export bridges (`from skintellect.formulation.scoring import *`) to preserve backward compatibility for legacy callers without duplicating code lines.

---

### Principle III: Data Tier Integrity (No Dumping into Archive)
* **Do NOT create an `archive/` folder to hide operational files or raw datasets.**
* Raw baseline data snapshots belong in [`data/raw/`](../../data/raw).
* The live relational database is [`skintellect_moisturizers.db`](../../skintellect_moisturizers.db) (26.4 MB, indexed across domains, targets, categories, and match scores).
* Never delete, wipe, or overwrite the master database without verified backups.

---

### Principle IV: Zero-Build Frontend Standard
* **No Node.js, Webpack, Vite, npm, or node_modules.**
* The frontend is intentionally engineered as a lightweight, zero-maintenance Single Page Application running natively on **Vue 3 Composition API** via a single local vendor script (`static/vendor/vue.global.prod.js`) and Tailwind CSS.
* Instant client-side reactivity (`setup()`, `reactive()`, `computed()`, `watch()`) handles debounced searches, active tabs, modal deep-dives, and domain switching with sub-millisecond responsiveness.
* Future AI sessions must preserve this zero-build architecture. Do not suggest or initiate npm build steps.

---

### Principle V: Resilient Database & Path Resolution
Every script must be executable from the project root (`python -m skintellect`), from within its stage directory (`python -m skintellect.ingestion.pubchem`), or via external CLI without failing on relative paths.
- **Rule**: Always resolve paths dynamically using candidate fallbacks:
  ```python
  _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
  _CANDIDATE_PATHS = [
      os.path.join(_THIS_DIR, "skintellect_moisturizers.db"),
      os.path.join(os.path.dirname(_THIS_DIR), "skintellect_moisturizers.db"),
      os.path.join(os.getcwd(), "skintellect_moisturizers.db"),
      os.path.join(os.getcwd(), "data", "skintellect_moisturizers.db")
  ]
  DB_PATH = next((p for p in _CANDIDATE_PATHS if os.path.exists(p) and os.path.getsize(p) > 1000), _CANDIDATE_PATHS[0])
  ```

---

### Principle VI: Windows UTF-8 Terminal Safety
On Windows systems, Python `sys.stdout` defaults to `cp1252` encoding, which crashes when printing unicode checkmarks (`✓`), medals (`🏆`, `⭐`), or chemistry symbols.
- **Rule**: Every script printing to console must include:
  ```python
  import sys
  if sys.stdout.encoding != 'utf-8':
      try:
          sys.stdout.reconfigure(encoding='utf-8')
      except Exception:
          pass
  ```

---

### Principle VII: Master Orchestration via `main.py`
All distinct subsystem operations must be accessible through the unified root orchestrator [`main.py`](../../src/skintellect/cli.py):
* `python -m skintellect stats` $\rightarrow$ Catalog metrics, category & domain breakdowns.
* `python -m skintellect audit` $\rightarrow$ Database integrity, missing field & linkage audit.
* `python -m skintellect clean` $\rightarrow$ Canonicalize fragmented categories & standardize routine steps.
* `python -m skintellect crawl` $\rightarrow$ Multi-category scraping with rate-limit jitter.
* `python -m skintellect recommend` $\rightarrow$ Personalized multi-category recommendations.
* `python -m skintellect report` $\rightarrow$ Markdown & HTML dashboard generation.
* `python -m skintellect web` $\rightarrow$ Launch the FastAPI web application.

---

### Principle VIII: Zero-Dependency Verification Suite
* **Never use third-party test clients (e.g. `httpx` or `starlette.testclient.TestClient`) that introduce unmanaged pip dependencies.**
* The test suite [`test_api.py`](../../tests/smoke_api.py) uses Python's standard library `urllib.request` and `json`.
* Every session modification MUST conclude with running `python -m tests.smoke_api` and verifying that all 11 test checks pass with status code 200.
