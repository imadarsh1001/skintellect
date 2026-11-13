# PRODUCT.md — Skintellect

*Inferred from the repository README and the shipped frontend; assumptions are labeled. Last reviewed 2026-11-13.*

## What it is

Skintellect is an open-source **cosmetic formulation intelligence and personalized skincare research engine**: users search a curated formulation catalog and get scores, safety audits, and evidence attributed to real review text — never unsourced claims.

## Who uses it

Skincare shoppers and ingredient-literate enthusiasts — typically acne-prone, sensitive-skin, or fungal-acne-aware users auditing products for comedogenic ingredients, Malassezia triggers, drying alcohols, fragrance, and allergens. *(Assumption: the audience mirrors the README's capability list; no user research exists in the repo.)*

## The promises the UI must keep

1. **Personalization is deterministic** — 0–100 match scores and clinical fit come from the user's skin profile (skin type, goals, strict exclusions) via a canonical scoring engine. Every score must be traceable to the persona.
2. **Safety claims are auditable** — pore-cloggers, fungal-acne triggers, drying alcohols, fragrance, allergens are detected and flagged with verifiable proof, not vibes.
3. **Reviews are evidence, not summaries** — community insights carry exact supporting text spans (attributed NLP); a claim without its span is not shippable.
4. **Deliberation is visible** — the multi-agent copilot (Formulator, Safety Critic, Microbiome Analyst, Clinical Judge) shows its reasoning steps and sources.
5. **Breakout diagnosis is differential** — Ingredient CSI compares problematic products against safe benchmarks to isolate suspect ingredients.

## Voice

Evidence-first, calm, zero hype. The product explains *why* (match reasons, quote spans, agent deliberation) instead of asserting. Personality lives in precision — no marketing superlatives, no filler enthusiasm.

## Surfaces (Operate mode)

- **Explore** — the primary browsing surface: URL-owned filters (domain/category strips, quick chips, sidebar), persona-scored product grid.
- **Product detail** — the dossier: safety certifications, INCI list, alternatives, attributed reviews, raw payload.
- **Copilot** — multi-domain research chat with session history and evidence output.
- **Compare / Study / Progress / Graph** — tray matrix, prepared studies, data-collection progress, ingredient relationships.

## Non-goals

Marketing claims without spans; auto-applying personas without user action; hiding the raw payload behind abstractions.
