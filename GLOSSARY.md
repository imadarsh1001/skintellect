# Domain vocabulary

| Term | Meaning in this project |
| --- | --- |
| Catalog | A selected SQLite dataset containing products, ingredients, reviews and research metadata. Selection and display-cache lifetime belong to `catalog/store.py`. |
| Recorded formula | The ingredient list actually stored for a product. It may be missing or incomplete. |
| Verified complete formula | An exact recorded formula with a matching human-reviewed hash, source and date. This attests to completeness, not safety. |
| Ingredient facts | Ingredient-name matches and separately retained source-provided flags/ratings, owned by `formulation/ingredient_facts.py`. Neither establishes clinical performance. |
| Classification policy | The named formula, catalog or recommendation matching profile. Historical differences are explicit and preserved; classification is separate from final score policy. |
| Review source | A review's raw text, visible cleaned text, source identity, product and duplicate status. Raw text and evidence IDs remain preserved. |
| Review corpus | The selected review sources and shared eligibility rules. Preparation/counts use unique nonempty sources per product; retrieval preserves individual raw-review evidence IDs. |
| Prepared review | A saved observation list matching the source hash and active extraction/model identity, with valid exact source spans. An accepted empty list means no observations, not missing preparation. |
| Passage | A retrievable catalog fact or visible review text with a stable evidence ID and content hash. |
| Passage index | Saved passage vectors accepted for the selected source hash, model, dimensions, numeric payload and normalization. Invalid rows are unready and remain eligible for repair. |
| Prepared study | The bounded selected product cohort and its current review/passage readiness. It is a demonstration, not representative market coverage. |

See [architecture](docs/ARCHITECTURE.md) for module ownership and
[source layout](docs/SOURCE_LAYOUT.md) for locations.
