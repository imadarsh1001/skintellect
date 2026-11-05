# Formulation rules and personas

| Location | Responsibility |
| --- | --- |
| [formulation/ingredient_facts.py](../../src/skintellect/formulation/ingredient_facts.py) | Shared ingredient patterns, name normalization and explicit classification policies |
| [formulation/scoring.py](../../src/skintellect/formulation/scoring.py) | Canonical persona compatibility match score (0–100%) and clinical Darmeto fit points (0–130 pts) |
| [formulation/formulas.py](../../src/skintellect/formulation/formulas.py) | Formula Lab ingredient interpretation, score explanations and audit output |
| `formulation/routines.py` (retired) | Recorded acid/retinoid and ceramide/panthenol co-occurrence observations |
| [formulation/models.py](../../src/skintellect/formulation/models.py) | Formula/routine request and response validation |
| [catalog/personas.py](../../src/skintellect/catalog/personas.py) | Presets, persona persistence and export |
| [catalog/taxonomy.py](../../src/skintellect/catalog/taxonomy.py) | Domain and configured-source metadata |

These rules are heuristic. Matching ingredient names does not reveal concentration,
pH, delivery, finished-product stability or individual response. Ingredient presence
alone does not establish a balanced lipid ratio or a compatible routine. Unknown
ratings and incomplete formulas must remain distinguishable from verified absence.

Classification consolidation preserves the historical formula, catalog and report
profiles; it does not force their final scores to agree. The legacy report's
matching vocabulary is retained explicitly. Policy changes require their own
characterization and validation rather than an incidental scoring change.

## Unified Compatibility & Darmeto Scoring

Formulation scoring and clinical fit calculations are consolidated into [src/skintellect/formulation/scoring.py](../../src/skintellect/formulation/scoring.py), serving as the single source of truth across Catalog listing (`catalog/products.py`), Recommendation ranking (`catalog/recommendations.py`), and Formula Lab:

1. **Personalized Match Score (0–100%):** Evaluates persona skin type and safety exclusions:
   - Malassezia / fungal acne safe violations hard-cap the score at 40%.
   - Fragrance penalties: -15% (sensitive) or -20% (very sensitive).
   - Drying simple alcohol penalties: -10% (normal) or -15% (dry/very sensitive).
   - Oil-free & pore-clogging comedogenic lipid deductions (-5% to -10%).
   - Active concern targeting adjustments (brighteners, barrier lipids, BHA/zinc).

2. **Darmeto Fit Points (0–130 pts):** Computes dermatological clinical fit points:
   - Baseline match score + active bonuses (brighteners up to +9, barrier up to +8, smoothing up to +6).
   - Safety formulation bonuses: Fungal safe (+4), Non-comedogenic (+3), Oil-free (+2).
   - Community consensus boost: +3 pts when rating &ge; 4.0.
   - Deductions: High pore cloggers (-4 per active) and sensitizing irritants (-6 per active).
   - Tiers: Holy Grail (120+ pts), Highly Targeted (105–119 pts), Everyday Base (90–104 pts), Suboptimal (&lt;90 pts).

```powershell
python -m skintellect score --help
```

The app exposes Formula Lab and routine analysis through `/api/formula-lab/analyze`
and `/api/routine/analyze`. Persona routes use `/api/personas`.

Human completeness verification belongs to [data maintenance](data-maintenance.md).
It attests to an exact stored formula and source, not product safety.
The retired `core/` package is documented in the [migration map](../SOURCE_LAYOUT.md).
