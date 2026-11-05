# Skintellect 🔬

> **Explainable Cosmetic Formulation Intelligence & Personalized Skincare Research Engine**  
> *Reverse-engineered ingredient compatibility, clinical fit scoring, attributed review NLP, and multi-agent formulation deliberation.*

---

## 📌 Overview

**Skintellect** is an open-source formulation intelligence and cosmetic research platform. Built with Python 3.12+, FastAPI, SQLite, and a buildless Vue 3 interface, it bridges cosmetic chemistry heuristics with modern AI orchestration. 

It empowers users to:
- **Reverse-Engineer Compatibility:** Calculate 0–100% personalized formulation match scores and clinical fit points based on specific skin profiles (e.g. acne-prone, oily, sensitive) via a unified canonical scoring engine.
- **Audit Safety & Comedogenicity:** Detect pore-clogging comedogenic ingredients, Malassezia (*fungal acne*) triggers, drying alcohols, synthetic fragrances, and allergens.
- **Synthesize Community Insights:** Extract granular sentiment aspects from thousands of user reviews with exact supporting text spans using Gemini NLP and passage indexing.
- **Convene Multi-Agent Deliberation:** Coordinate specialist agent boards (Formulator, Safety Critic, Microbiome Analyst, and Clinical Judge) to debate ingredient efficacy, vehicle delivery, and barrier safety.
- **Investigate Breakouts via Ingredient CSI:** Perform differential set comparison between problematic products and safe benchmarks to isolate prime suspect ingredients.

---

## 🏛️ Architecture: Public Intelligence vs. Private Collector

Skintellect is architected with a strict separation between **data collection** and **scientific intelligence**:

```
├── 🔒 PRIVATE REPOSITORY: skintellect-collector
│   ├── src/collector/          # Turbo-Frame HTML streams, scrapers, rate limiters
│   ├── queue.py                # Prioritized SQLite queue worker with exponential backoff
│   └── data/raw/               # Raw HTML/JSON snapshots (~37 MB)
│
└── 🌐 PUBLIC REPOSITORY: skintellect (This Repository)
    ├── src/skintellect/
    │   ├── api/                # FastAPI application, OpenAPI schema & REST endpoints
    │   ├── catalog/            # Catalog store, recommendation algorithms, persona registry
    │   ├── formulation/        # Scoring algorithms, clinical fit points, compatibility rules
    │   ├── research/           # Gemini RAG, review NLP, passage indexing, evidence attribution
    │   ├── agents/             # LangGraph copilot, specialist deliberation, CSI detective
    │   ├── database.py         # Schema creation (init_db), migrations, reproducible audits, exports
    │   └── web/                # Vue 3 reactive UI + Tailwind CSS interface
    ├── tests/                  # 128 unit/architecture tests, synthetic fixture bootstrap
    └── frontend/               # Modern Vue 3 + Vite SPA client
```

*The public repository is 100% self-contained: it runs out-of-the-box using deterministic synthetic catalogs (`tests/bootstrap_catalog.py`) or local SQLite databases (`skintellect_moisturizers.db`) with zero external scraping dependencies.*

---

## 🚀 Quickstart

We recommend **[uv](https://github.com/astral-sh/uv)** for fast, reproducible package management.

### Option A: Using `uv` (Recommended)

```powershell
# 1. Clone repository
git clone https://github.com/imadarsh1001/skintellect.git
cd skintellect

# 2. Create virtual environment and install package in editable mode with dev tools
uv venv
.\.venv\Scripts\Activate.ps1    # macOS/Linux: source .venv/bin/activate
uv pip install -e ".[dev]"

# 3. Configure local environment (copy example)
Copy-Item .env.example .env    # macOS/Linux: cp .env.example .env

# 4. Launch Formulation Studio Web UI
uv run skintellect web --port 8000
```

### Option B: Using Standard Python `venv`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m skintellect web --port 8000
```

Once running, open:
- 🌐 **Formulation Studio:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 🔬 **Prepared Three-Product Study:** [http://127.0.0.1:8000/study](http://127.0.0.1:8000/study)
- 📚 **Interactive OpenAPI Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💻 Command Line Interface (CLI)

Skintellect includes a master CLI interface:

```powershell
# Display catalog metrics, category counts, and ingredient safety stats
uv run skintellect stats

# Get personalized top recommendations (e.g. Korean sunscreens, min 85% match)
uv run skintellect recommend --category sunscreens --country "South Korea" --min-match 85

# Granular filter for fungal acne safe, fragrance-free serums
uv run skintellect filter --category serums --fungal-safe --fragrance-free --min-match 90

# Score any custom ingredient deck or recorded catalog product
uv run skintellect score --ingredients "Water, Niacinamide, Glycerin, Ceramide NP"
uv run skintellect score --product "Barrier Restoring Cream"

# Convene Multi-Agent Formulation Board deliberation
uv run skintellect agent --formula "Water, Salicylic Acid, Glycolic Acid" --persona acne_prone

# Run Ingredient CSI Detective to isolate breakout triggers
uv run skintellect agent --csi --csi-problems "Problem Cream A; Breakout Gel B" --csi-safes "Safe Benchmark Lotion"

# Audit catalog integrity, schema consistency, and formula completeness
uv run skintellect audit

# Clean and standardize category names and rating distributions
uv run skintellect clean

# Export products and personas to clean, formatted JSON
uv run skintellect export

# Synchronize/import updated formulations from private collector JSON export
uv run python -m skintellect.ingestion.maintenance import <path-to-catalog.json>
```

---

## 📦 Package Management with `uv`

This project uses modern PEP 621 metadata configured in `pyproject.toml`:

```powershell
# Add a new runtime dependency
uv add <package-name>

# Add a development tool
uv add --dev <tool-name>

# Run lint checks with Ruff in the managed environment
uv run ruff check .

# Execute full verification suite
uv run python scripts/check.py
```

---

## 🧪 Testing & Verification

Skintellect adheres to strict verification-before-completion standards:

```powershell
# 1. Run full verification suite (Ruff, 128 tests, UI semantic contracts)
uv run python scripts/check.py

# 2. Run developer query-intent parser validation (20/20 benchmark cases)
uv run python -m scripts.check_query_parser

# 3. Run workspace contract & document integrity audit (0 broken links)
uv run python -m scripts.audit_workspace

# 4. Run UI semantics & WCAG contrast check
node tests/check_ui_semantics.js
```

---

## 🗺️ Project Structure

```
├── src/skintellect/
│   ├── api/                   # FastAPI route definitions (catalog, formulation, research, study)
│   ├── catalog/               # Catalog models, persona store, recommendations, taxonomy
│   ├── formulation/           # Heuristic scoring, Darmeto clinical fit points, ingredient facts
│   ├── research/              # RAG pipeline, Gemini extraction, passage indexing, evidence
│   ├── agents/                # LangGraph copilot, specialist deliberation, CSI detective
│   ├── database.py            # SQLite schema, transactions, migrations, reproducible audits
│   ├── config.py              # Environment variable resolution & dynamic path discovery
│   └── web/                   # Fast HTML templates, static CSS/JS, and bundled Vue 3
├── tests/                     # 128 unit and architecture tests with synthetic fixtures
├── experiments/               # Specialist board, Ingredient CSI, Formula Lab experiments
├── frontend/                  # Vue 3 + Tailwind CSS modern SPA interface
├── docs/                      # Architectural specs, module guides, and engineering logs
├── scripts/                   # Automated check suites, audits, and evaluation runners
└── data/                      # Data storage contract documentation & JSON exports
```

---

## ⚖️ Scientific & Ethical Disclaimer

Skintellect is a formulation research prototype. Its match scores, Darmeto fit points, and safety flags are **algorithmic heuristics**, not medical advice or clinical validation. Review excerpts reflect consumer sentiment and do not prove dermatological causation. Always consult a certified dermatologist for medical skin conditions.

---

## 📄 License

Licensed under the [MIT License](LICENSE).
