> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Formulation Studio — Project Scope, Vision & Strategic Roadmap

> **Authoritative Context Document**  
> *Status: Active Living Standard (Baseline Ground Truth for Future AI Sessions)*  
> *Last Updated: October 2026*

---

## 1. Executive Summary & Vision

**Formulation Studio** was conceived to solve a critical limitation in consumer cosmetics and dermatological tools: **reliance on opaque, subscription-gated platforms that analyze only facial skincare while ignoring the interconnected biology of the human body (Scalp/Hair, Body/Bacne/KP, and Makeup/Complexion).**

Our mission is to build a **fully transparent, mathematically verifiable, offline-capable formulation intelligence engine** that:
1. **Reverse-engineers and demystifies proprietary scoring models** (such as Skintellect's personalized match percentage and clinical dermatological fit scores).
2. **Breaks beyond facial skincare** into a unified cross-body architecture spanning **🧴 Skin (Face)**, **💇 Hair & Scalp (Trichology)**, **🧼 Bath & Body (KP & Bacne)**, and **💄 Makeup (Non-Acnegenic Cosmetics)**.
3. **Cross-references multi-source ingredient intelligence** across scientific authorities (**Skintellect**, **INCIDecoder**, **CosDNA**, **CIR Expert Panels**, and **NCBI PubChem**).
4. **Validates 5-step synchronized routines** for active chemical conflicts (e.g. Retinoids + High-dose AHA/BHA) and lipid barrier synergies.
5. **Operates with zero build overhead and zero vendor lock-in** (native Python backend, SQLite relational storage, and buildless Vue 3 Single Page Application).

---

## 2. What We Have Built (Current State)

| Subsystem | Current State | Verification / Metrics |
| :--- | :--- | :--- |
| **Catalog Database** | Indexed relational SQLite store (`skintellect_moisturizers.db`, 26.4 MB) | **2,502 verified formulations**, 1,507 unique cosmetic ingredients, 12,216 product-ingredient links, 4,062 user reviews. |
| **Multi-Domain Taxonomy** | Complete architectural support across 4 domains & anatomical targets | **Skin (Face)**, **Hair (Scalp & Strands)**, **Body (Arms/KP & Back/Bacne)**, and **Makeup (Complexion & Lips)** with benchmark seed products. |
| **Multi-Source Ingredient Explorer** | In-memory O(1) registry with 50 cosmetic functions | Searchable by name, cosmetic function, 0–5 comedogenicity, Malassezia safety, and cross-references to PubChem CID/formula. |
| **Formula Lab & Mathematical Engine** | 29-step real-time execution trace | Evaluates any raw ingredient text against reverse-engineered formulas; calculates base scores, avoidance deductions, and Darmeto points. |
| **Routine Conflict Engine** | Synchronized 5-step validator | Detects active ingredient clashes (acids vs. retinoids) and lipid barrier synergies (ceramide:cholesterol:fatty acid equimolar balance). |
| **Dupe & Formula Twin Matcher** | Algorithmic twin finder | Identifies budget-friendly alternatives that replicate active ingredient concentrations without compromising safety. |
| **Zero-Build Web UI** | Vue 3 Single Page Application (`static/` + `templates/`) | Sub-2ms cached catalog queries, debounced search, responsive layout, dark terminal theme, zero node_modules. |
| **Unified CLI Orchestrator** | Master terminal tool (`main.py`) | Orchestrates `stats`, `audit`, `clean`, `crawl`, `recommend`, `report`, and `web` across all pipeline stages. |

---

## 3. The Future Vision & What We Have Discussed to Build

### A. Multi-Source Ingestion & External Crawling Connectors
* **INCIDecoder Deep Scraper**: Systematically crawl all 15,000+ scientific ingredient monographs on INCIDecoder to expand chemical mechanisms, CAS numbers, and CIR safety panel determinations.
* **CosDNA Toxicology Indexer**: Ingest historical acnegenicity and irritancy ratings (0–5 scales) to create a weighted hazard consensus across every ingredient.
* **CurlScan / CGM Connector**: Ingest curly-girl method approval datasets, silicone classifications (soluble vs. non-soluble), and drying alcohol flags for hair care.
* **NCBI PubChem Chemical Pipeline**: Automated batch enrichment script to resolve PubChem CIDs, molecular weights, Canonical SMILES, and 2D chemical structure SVGs for all ingredients.
* **EWG Skin Deep Benchmark**: Ingest EWG hazard ratings (1–10 hazard scale) as an additional comparative safety reference.

### B. Full Expansion of Multi-Body Care Categories
1. **💇 Hair & Scalp Care**:
   * Expand from benchmark products to a **1,000+ product catalog** covering Shampoos (sulfate-free vs clarifying), Conditioners, Scalp Serums, Hair Masks, Leave-In Treatments, and Hair Oils.
   * Specific trichological algorithms:
     * *Scalp Malassezia Safety*: Detect fatty acid triggers that feed seborrheic dermatitis and dandruff yeast.
     * *Protein-Moisture Balance*: Calculate ratio of hydrolyzed proteins (wheat, keratin, silk) vs. humectants (glycerin, aloe) to prevent protein overload and strand brittleness.
     * *Silicone Buildup Potential*: Differentiate between water-soluble silicones (Dimethicone Copolyol) and non-soluble silicones requiring sulfates for removal (Dimethicone, Cyclopentasiloxane).
2. **🧼 Bath & Body Care**:
   * Expand catalog to **Body Washes, Body Lotions, Exfoliating Scrubs, Hand Creams, Foot Creams, and Body Sunscreens**.
   * Specific body dermatological algorithms:
     * *Bacne Comedogenicity*: Stricter threshold for comedogenic lipids on sebaceous back and chest areas.
     * *Keratosis Pilaris (KP) Score*: Score products based on optimal keratolytic concentrations (Urea 10–20%, Lactic Acid 10–12%, Salicylic Acid 2%) to soften keratin plugs on arms and legs.
     * *Body Xerosis & Eczema Relief*: Detect ceramide-to-cholesterol barrier repair complexes for atopic body dermatitis.
3. **💄 Makeup & Complexion**:
   * Expand catalog to **Foundations, Concealers, Primers, Tinted Moisturizers, Setting Powders, and Lip Balms**.
   * Specific cosmetic formulation algorithms:
     * *Non-Acnegenic Base Verification*: Ensure cosmetic foundations do not combine heavy occlusives with high-comedogenic binders (e.g. Isopropyl Isostearate, Ethylhexyl Palmitate).
     * *Hybrid Skincare-Makeup Score*: Reward formulas that infuse skincare actives (SPF, Niacinamide, Hyaluronic Acid, Squalane) into color cosmetics.
     * *Sensitive Eye / Periorbital Safety*: Ensure non-migrating binders and ophthalmologist-safe pigments near tear ducts.

### C. Advanced Algorithmic Intelligence & AI Synthesis
* **Formula Reverse-Engineering & Concentration Estimation**: Predict likely percentage concentrations of actives based on ingredient list order (1% line heuristics: ingredients after Phenoxyethanol or Xanthan Gum are typically $\le 1\%$).
* **Clinical Persona Customizer UI**: Allow users to create custom personas through an interactive quiz (Skin type, sensitivity rating, specific allergens, target concerns, budget preference).
* **Automated Patch Test & Allergy Matrix**: Given a user's known contact allergens, instantly screen entire 2,500+ product catalog and raw formula decks for molecular relatives.
* **Generative Formula Synthesis**: Suggest complementary ingredients to stabilize or improve a user-submitted formula (e.g. suggesting adding Ferulic Acid and Vitamin E to stabilize L-Ascorbic Acid).

---

## 4. Architectural Rules for Future AI Sessions

1. **Maintain Stage Decoupling**: Code MUST reside in its designated stage package (`ingestion/`, `pipeline/`, `core/`, `analysis/`, `backend/`, `data/`). Never place operational business logic into `archive/` or root ad-hoc scripts.
2. **Single Source of Truth**: The clinical scoring formulas and persona models live in [`core/`](../../src/skintellect). Never create duplicate scoring functions in other packages.
3. **Zero-Build Frontend Mandate**: Keep the frontend buildless. Do NOT introduce Node.js, Webpack, Vite, or npm build pipelines unless explicitly commanded by the user. Vue 3 Composition API via local vendor scripts is the chosen standard.
4. **Data Tier Safety**: Never delete, truncate, or overwrite [`skintellect_moisturizers.db`](../../skintellect_moisturizers.db) without a confirmed backup. Baseline raw data resides in [`data/raw/`](../../data/raw).
5. **Continuous Verification**: Any structural modification must be validated by running [`test_api.py`](../../tests/smoke_api.py).
