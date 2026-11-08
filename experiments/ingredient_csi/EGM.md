# Ingredient CSI

## Overview

Experimental forensic package (`experiments/ingredient_csi`). `CSIDetective`
("Inspector INCI") performs set-theoretic differential analysis between products or
decks that caused reactions ("problematic") and tolerated benchmarks ("safe"), then
clusters the remaining candidate ingredients into chemical families and ranks them
with a heuristic suspect score. Results are candidate attributions only — the module
is a study tool and never mutates stored data.

## Interface

- `[detective.py:CHEMICAL_FAMILIES]` — ordered dict of six chemical-family regex
  pattern groups used for clustering: "Fatty Acid Esters & Comedogenic Lipids",
  "Fragrance Sensitizers & Essential Oils", "Preservatives & Biocides", "Fatty
  Alcohols & Heavy Emulsifiers", "Ferments & Yeasts (Malassezia Stimulants)",
  "Volatile Drying Alcohols". Unmatched ingredients fall back to
  "Other Cosmetic Excipient / Active".
- `[detective.py:CSIDetective.__init__(db_path=None)]` — defaults the database path to
  `src/skintellect/config.py:DB_PATH`; identity fields `name="Inspector INCI"`,
  `role="Forensic Formulation Detective"`, `badge="🔍 Ingredient CSI"`.
- `[detective.py:CSIDetective._resolve_deck(item)]` — resolves one input into
  `(label, ingredient_list)`; accepts, in order:
  1. `int` or all-digit `str` → product id lookup;
  2. `dict` → label from `name`/`title`, ingredients from `ingredients`/
     `ingredients_text`;
  3. `str` shorter than 80 chars without `,`, `\n`, or `;` → case-insensitive
     `products` lookup by `name LIKE` or `brand || ' ' || name LIKE` (first match);
  4. any other string → parsed as a raw ingredient deck with label
     "Custom Ingredient Deck".
  Parsing always goes through
  `src/skintellect/formulation/scoring.py:parse_ingredients_input`.
- `[detective.py:CSIDetective.investigate(problematic_items, safe_items, reaction_type="breakouts_acne")]` —
  returns the report dict:
  - Success keys: `detective`, `badge`, `total_problem_products`,
    `total_safe_products`, `problem_product_names`, `safe_product_names`,
    `safe_molecules_count`, `suspects_count`, `top_suspects` (at most 15),
    `recommended_exclusions`, `thinking`, `forensic_summary`.
  - Suspect keys: `ingredient` (title-cased), `frequency`
    (`"<count>/<total> problematic formulas"`), `recurrence_rate` (0-100),
    `suspect_score` (0-99), `chemical_family`, `is_pore_clogger`, `is_irritant`,
    `is_fungal_trigger`.
  - Suspect score model (`[detective.py:CSIDetective.investigate]`):
    `round(frequency_ratio * 40)` + `25` if absent from all safe decks + `20` if a
    pore clogger + `15` if an irritant + `15` if a fungal trigger, capped at `99`.
    Flag lookups use `src/skintellect/formulation/ingredient_facts.py`
    (`KNOWN_PORE_CLOGGERS`, `IRRITANTS_ALLERGENS`, `FUNGAL_ACNE_TRIGGERS`).
  - `recommended_exclusions` is derived only from the top 5 suspects and is drawn
    from `pore_clogger_free`, `fungal_acne_safe`, `fragrance_free`, `alcohol_free`.
  - Failure contract: returns `{"error": "No valid problematic products provided. ..."}`
    when no problematic item resolves to a non-empty deck.

## Invariants

- Candidates are a strict set difference: only ingredients present in at least one
  problematic deck and absent from the union of all safe decks
  (`safe_universe`) become suspects
  (`[detective.py:CSIDetective.investigate]`). Shared ingredients are never reported.
- At least one problematic deck is required; zero problematic decks can only produce
  the `error` dict, never a report (`[detective.py:CSIDetective.investigate]`).
- Suspects are sorted by `(suspect_score, recurrence_rate)` descending and truncated
  to the top 15 in `top_suspects`.
- `[detective.py:CSIDetective.investigate]` accepts `reaction_type` but never reads it
  in the scoring body; the returned report is identical for
  `breakouts_acne`, `contact_dermatitis`, and `fungal_acne`.
- Family classification is first-match-wins over the
  `[detective.py:CHEMICAL_FAMILIES]` insertion order.
- Deck ingredient names are lower-cased before analysis; report ingredient names are
  `.title()`-cased (`[detective.py:CSIDetective.investigate]`).

## Side Effects

- SQLite reads: `[detective.py:CSIDetective._resolve_deck]` opens
  `sqlite3.connect(self.db_path)` and runs read-only `SELECT` queries against the
  `products` table (by `id`, or `LIKE` on name/brand) for product-id and short-name
  inputs; each connection is closed immediately after the single query. No writes.
- No network calls, no LLM calls, no filesystem writes. All classification is local
  regex work plus the shared ingredient-facts tables.

## Verification

From the repository root:

```
python -m experiments.smoke_agents
```

`[smoke_agents.py:test_csi_detective]` verifies the differential isolation of
"Isopropyl Myristate" with `recurrence_rate == 100` and `is_pore_clogger is True`
(`AGENT_LLM_MODE=offline` is forced; no key or network needed). The experiments
unittest file also exercises this package
(`python -m unittest experiments.test_experimental_features`). Repo-level API smoke:
`python -m tests.smoke_api`. No pytest is configured for this repository.
