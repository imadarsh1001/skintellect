# Formulation rules and personas

| Location | Responsibility |
| --- | --- |
| [formulation/ingredient_facts.py](../../src/skintellect/formulation/ingredient_facts.py) | Shared ingredient patterns, name normalization and explicit classification policies |
| [formulation/scoring.py](../../src/skintellect/formulation/scoring.py) | Ingredient parsing, raw-formula match penalties and fit points |
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

```powershell
python -m skintellect score --help
```

The app exposes Formula Lab and routine analysis through `/api/formula-lab/analyze`
and `/api/routine/analyze`. Persona routes use `/api/personas`.

Human completeness verification belongs to [data maintenance](data-maintenance.md).
It attests to an exact stored formula and source, not product safety.
The retired `core/` package is documented in the [migration map](../SOURCE_LAYOUT.md).
