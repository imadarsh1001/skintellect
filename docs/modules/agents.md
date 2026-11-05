# Experimental board and Ingredient CSI

The implementations live in [experiments/specialist_board/](../../experiments/specialist_board/);
HTTP input validation and routes live in [api/app.py](../../src/skintellect/api/app.py).

| Module | Responsibility |
| --- | --- |
| `board.py` | Coordinates specialist turns and the final deterministic score |
| `formulator.py` | Ingredient/vehicle-oriented commentary |
| `safety_critic.py` | Rule-based flags and optional generated critique |
| `microbiome.py` | Heuristic ingredient-trigger commentary |
| `judge.py` | Uses the canonical scoring implementation |
| `detective.py` | Compares problematic/tolerated ingredient sets and ranks candidate ingredients |
| `llm.py` | Shared-provider adapter, fallback behavior and telemetry |

The named specialists are software roles. Their discussion, likelihood-style scores
and ingredient differences do not establish clinical validation or allergy causation.
The CSI implementation uses ingredient sets and predefined family patterns; it is
not a live PubChem molecular investigation. Offline commentary remains heuristic.

| Endpoint | Method |
| --- | --- |
| `/api/agents/meta` | GET |
| `/api/agents/board/deliberate` | POST |
| `/api/agents/board/stream` | GET, server-sent events |
| `/api/agents/csi/investigate` | POST |

```powershell
python -m skintellect agent --help
python -m tests.smoke_agents
```

The documented smoke command forces offline mode. Normal agent commands can use
the configured provider. See [development](../DEVELOPMENT.md) for settings and checks.
