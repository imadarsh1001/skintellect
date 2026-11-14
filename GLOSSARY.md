# Skintellect

One context: the formulation intelligence platform (frontend + FastAPI backend + copilot agents).

## Language

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
Backend term (`verified_complete_products`) for formulations whose INCI list is verified complete. Prefer "formulas with full INCI" in UI copy.

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
