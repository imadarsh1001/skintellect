# Glossary

Two vocabularies share this file: the backend's domain decisions (data guarantees and module ownership) and the UI copy rules for user-facing text.

## Backend domain vocabulary

| Term | Meaning in this project |
| --- | --- |
| Catalog | A selected SQLite dataset containing products, ingredients, reviews and research metadata. Selection and display-cache lifetime belong to `catalog/store.py`. |
| Recorded formula | The ingredient list actually stored for a product. It may be missing or incomplete. |
| Verified complete formula | An exact recorded formula with a matching human-reviewed hash, source and date. This attests to completeness, not safety. |
| Ingredient facts | Ingredient-name matches and separately retained source-provided flags/ratings, owned by `formulation/ingredient_facts.py`. Neither establishes clinical performance. |
| Classification policy | The named formula, catalog or recommendation matching profile. Historical differences are explicit and preserved; classification is separate from final score policy. |
| Compatibility & clinical fit | Algorithmic persona match percentage (0–100%) and clinical Darmeto points (0–130 pts), owned canonically by `formulation/scoring.py` and shared across catalog, recommendations, and studio lab. |
| Review source | A review's raw text, visible cleaned text, source identity, product and duplicate status. Raw text and evidence IDs remain preserved. |
| Review corpus | The selected review sources and shared eligibility rules. Preparation/counts use unique nonempty sources per product; retrieval preserves individual raw-review evidence IDs. |
| Prepared review | A saved observation list matching the source hash and active extraction/model identity, with valid exact source spans. An accepted empty list means no observations, not missing preparation. |
| Passage | A retrievable catalog fact or visible review text with a stable evidence ID and content hash. |
| Passage index | Saved passage vectors accepted for the selected source hash, model, dimensions, numeric payload and normalization. Invalid rows are unready and remain eligible for repair. |
| Prepared study | The bounded selected product cohort and its current review/passage readiness. It is a demonstration, not representative market coverage. |

## UI copy vocabulary

**Formulation**:
A product record in the catalog (the code calls it `Product`). One formulation = one sellable cosmetic product with its INCI list.
_Avoid_: item, listing, product-name-only references

**Indexed formulations**:
Total formulations in the catalog (`stats.total_products`). Shown in the Explore hero stat row.

**Formulas with full INCI**:
The subset whose ingredient list is completely parsed (backend `enriched_products`; `verified_complete_products` when the API provides it). Subset of indexed — do not call these "Enriched Formulations".
_Avoid_: Enriched Formulations

**Matching formulations**:
The filtered result set the grid paginates over ("36 of 2,492 matching"). Always qualified by current filters; never compared to indexed without saying so.

**Verified Complete Formulas**:
Backend term (`verified_complete_products`, defined in the table above as *verified complete formula*). Prefer "formulas with full INCI" in UI copy.

## Evidence verdicts

**Verified**:
Full verified INCI present (teal badge family).

**Source**:
Claim backed by an attributed source (blue).

**Unknown**:
Claim that could not be verified (amber).

**Negative**:
Contraindication or flagged trigger (rose).

**Mixed**:
Conflicting evidence (purple).

## Copilot

**Session**:
A named copilot conversation with stored history; deletable via confirmed affordance.

**Compare tray**:
The 1–4 formulations in active comparison; also the copilot's `product_ids` context.

**Persona**:
The user's skin profile (skin type, goals, strict exclusions) driving deterministic scoring. Presets apply instantly; custom personas save via `POST /api/personas`.

See [architecture](docs/ARCHITECTURE.md) for module ownership and
[source layout](docs/SOURCE_LAYOUT.md) for locations.
