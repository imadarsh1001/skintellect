# Audience & Voice Brief — add-ui-personality-and-motion

Change: add-ui-personality-and-motion · group 1.4 · 2026-11-16
Derived from: README.md (capability list), PRODUCT.md (promises, voice, surfaces), the persona feature (skin types, goals, strict exclusions), frontend/DESIGN.md @ 974ae98 (Furrow identity, mono-as-material rule), and the shipped ledger voice ("never a number without its unit").
Rule (per tasks 1.4): every dealt moment and every state copy in groups 2–5 must trace to a dimension below — never agent taste.

## Who the user is

Skincare shoppers and ingredient-literate enthusiasts auditing products before they buy — typically managing acne, sensitive skin, or fungal-acne triggers. They are not browsing for delight; they are auditing for risk. (PRODUCT.md notes the honest limit: this audience mirrors the README's capability list; no user research exists in the repo.)

## User dimensions (the 5 that motion and state copy must serve)

1. **The ingredient auditor** — reads INCI lists and comedogenic ratings line by line. Needs: traceability from any signal back to its source; motion may never obscure the data they are reading. Trace: README "Audit Safety & Comedogenicity"; PRODUCT promise 2.
2. **The trigger-sensitive shopper** — acne-prone, sensitive, or fungal-acne-aware; scanning for pore-cloggers, drying alcohols, fragrance, allergens. Needs: verdicts that are instant to read and instant to trust; a movement that arrives calmly, not one that startles a stressed scan. Trace: README persona examples; PRODUCT "who uses it".
3. **The deterministic-persona user** — sets skin type, goals, strict exclusions and expects the 0–100 match to be traceable to that persona via the canonical engine. Needs: the moment the score appears, the *reason* is present — a reveal that shows the number without its trace is slop. Trace: PRODUCT promise 1; persona feature.
4. **The evidence-demanding researcher** — wants exact review-text spans and visible multi-agent deliberation (Formulator, Safety Critic, Microbiome Analyst, Clinical Judge); a claim without its span is not shippable, so a state that hides its process is not shippable either. Needs: loading states that show real work (which agent, which source), not generic spinners. Trace: PRODUCT promises 3–4.
5. **The breakout-diagnosis user** — often stressed, comparing a problem product against safe benchmarks (Ingredient CSI). Needs: calm differential clarity; error states that explain and recover, never dead-end. Trace: README "Investigate Breakouts via Ingredient CSI"; PRODUCT promise 5.

## Voice guide (the product's spoken register — state copy inherits it)

- **Evidence-first**: say the *why*; every figure carries its unit and its source. The ledger voice: "never a number without its unit".
- **Calm**: no exclamation, no urgency theater, no marketing superlatives. Empty and error states state facts and offer the next action.
- **Precise**: concrete nouns from the domain (comedogenic, Malassezia, INCI, span, verdict) — never "stuff", "things", "oops".
- **Verdict-shaped**: verified / source / unknown / negative / mixed — reuse the five meanings rather than inventing new moods for states.
- **Motion speaks the same voice**: motion serves meaning (feedback, state change, spatial continuity, visible deliberation); it settles and never bounces (`--ease-*` family has no overshoot); a dealt moment explains the product, it does not perform. Zero purely decorative motion — if a movement explains nothing a dimension above needs, it does not ship.

## How this brief gates later groups (updated post-delivery, 2026-11-16 — the mappings below record what actually shipped)

- Group 2 (feedback): identical hover/press on every interactive primitive, ≤ `--duration-feedback`; **focus is deliberately instant, not on the feedback tier** (Floor 15/26a) — serves dimension 2's unstartling scan.
- Group 3 (deep moments): Explore match-score reveal shows score *with* its reason on `:title` (dim 3); the dossier carries the **score continuity count** ("the score follows you in", dim 3) — the evidence-span highlight originally planned here re-homed to ResearchView in group 4 after the dossier proved to render no attributed spans; Copilot deliberation arrival makes agent reasoning visible, not decorative (dim 4).
- Group 4 (light moments): the re-homed **span sweep** on ResearchView synthesis quotes (dims 1, 4); Study/Progress arrivals serve dim 4, Compare serves dim 3, Graph serves dim 1.
- Group 5 (async states): shaped loading names the real work (dim 4); error states recover, wired to the actual failing fetch — page-level and nested (dim 5); copy follows the voice guide verbatim rules.
- Group 7 (audit): every moment/state in the shipped code must cite a dimension number from this file.
