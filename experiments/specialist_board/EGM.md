# Specialist Board

## Overview

Experimental multi-agent deliberation package (`experiments/specialist_board`). A
`BoardOrchestrator` convenes an adversarial 5-round debate between a Lead Cosmetic
Chemist (`FormulatorAgent`), a Clinical Safety Critic (`SafetyCriticAgent`), a
Microbiome Specialist (`MicrobiomeAgent`), and a non-LLM `DeterministicJudgeAgent`
whose verdict is grounded in the shared scoring engine at
`src/skintellect/formulation/scoring.py`. Every agent is LLM-optional: prose is
requested from Gemini through a thin adapter (`llm.py:LLMClient`) when a key is
configured, and otherwise replaced by deterministic rule-based text so the board
always produces a complete, structured debate.

## Interface

- `[board.py:BoardOrchestrator]` — composes `FormulatorAgent`, `SafetyCriticAgent`,
  `MicrobiomeAgent`, `DeterministicJudgeAgent`, and one shared `LLMClient`.
  - `[board.py:BoardOrchestrator.run_deliberation] (ingredients_input, persona_id="uap", user_question=None)` —
    executes all 5 rounds and returns `{"status", "persona", "user_question",
    "rounds_count", "telemetry", "debate", "verdict"}`; `debate` is a list of 5 round
    dicts each tagged with `round` (1..5) and `stage`.
  - `[board.py:BoardOrchestrator.stream_deliberation] (ingredients_input, persona_id="uap", user_question=None)` —
    generator emitting Server-Sent Events frames `data: {json}\n\n` with payload types
    `init`, `typing`, `turn` (rounds 1-5), and `done` (carries the verdict).
  - `[board.py:BoardOrchestrator._resolve_persona] (persona_id="uap")` — resolves a
    persona dict via `src/skintellect/catalog/personas.py:get_all_personas`, matching on
    `id` or `username`, falling back to the first persona, then to a hardcoded
    `uap` / "Universal Combination Profile" default.
- `[formulator.py:FormulatorAgent]` (identity: "Dr. Elena Vance" / "Lead Cosmetic Chemist")
  - `[formulator.py:FormulatorAgent.generate_proposal] (ingredients_input, persona, user_question=None)` —
    returns `{"agent", "role", "badge", "color", "vehicle_type", "active_count",
    "message", "thinking", "key_actives"}`; vehicle detection inspects the first 5
    parsed tokens for `oil`/`butter`, `dimethicone`/`silicone`, `aloe`/`centella`/`water`.
  - `[formulator.py:FormulatorAgent.generate_rebuttal] (critique_concerns, persona)` —
    deterministic counter-defense text; returns `{"agent", "role", "badge", "color",
    "message", "thinking"}`.
- `[safety_critic.py:SafetyCriticAgent]` (identity: "Dr. Marcus Cross" / "Clinical Safety & Toxicology Critic")
  - `[safety_critic.py:SafetyCriticAgent.audit_formulation] (ingredients_input, persona, formulator_statement=None)` —
    returns `{"agent", "role", "badge", "color", "message", "thinking", "flags",
    "irritants", "cloggers", "is_clean"}`; `flags` are built from the analysis
    irritants/cloggers plus fungal triggers only when the persona enforces
    `safety_exclusions.fungal_acne_safe`.
- `[microbiome.py:MicrobiomeAgent]` (identity: "Dr. Nadia Lin" / "Microbiome & Barrier Flora Specialist")
  - `[microbiome.py:MicrobiomeAgent.inspect_microbiome_safety] (ingredients_input, persona)` —
    returns `{"agent", "role", "badge", "color", "message", "thinking",
    "is_fungal_safe", "fungal_triggers"}`; `is_fungal_safe` is true iff the analysis
    reports zero fungal triggers.
- `[judge.py:DeterministicJudgeAgent]` (identity: "Chief Justice Darmeto" / "Deterministic Scoring Engine")
  - `[judge.py:DeterministicJudgeAgent.adjudicate] (ingredients_input, persona, formulator_report, critic_report, microbiome_report)` —
    returns `{"agent", "role", "badge", "color", "predicted_match", "darmeto_points",
    "tier", "status", "verdict_badge", "summary", "thinking", "audit_log",
    "breakdown"}`; delegates all arithmetic to
    `src/skintellect/formulation/scoring.py:predict_skintellect_match` and
    `src/skintellect/formulation/scoring.py:calculate_darmeto_points`.
- `[llm.py:LLMClient] (mode="auto")` — Gemini adapter; `has_any_key`, `key_summary`,
  `last_telemetry` properties/attribute; `[llm.py:LLMClient.chat_complete] (messages, system_prompt=None, temperature=0.3, max_tokens=800)`
  returns `str` or `None`. `[llm.py:TextResponse]` is the pydantic response contract
  (`text` capped at 12000 chars). Transport comes from `src/skintellect/gemini.py:GeminiClient.structured`
  under task name `legacy_agent`.
- `[__init__.py]` — package marker only ("Skintellect agents package."); no re-exports,
  so consumers must import from submodules (e.g. `experiments.specialist_board.board`).

External dependencies (repository paths): `src/skintellect/formulation/scoring.py`
(`parse_ingredients_input`, `analyze_ingredients`, `calculate_darmeto_points`,
`predict_skintellect_match`), `src/skintellect/catalog/personas.py:get_all_personas`,
`src/skintellect/gemini.py` (`GeminiClient`, `GeminiUnavailable`).

## Invariants

- Fixed round order 1-5: Formulator proposal, Safety Critic audit, Microbiome
  inspection, Formulator rebuttal, Deterministic Judge adjudication, in both
  `[board.py:BoardOrchestrator.run_deliberation]` and
  `[board.py:BoardOrchestrator.stream_deliberation]`.
- Every agent result dict carries the identity keys `agent`, `role`, `badge`,
  `color`, `message` (or `summary` for the judge), and `thinking`;
  `[board.py:BoardOrchestrator.run_deliberation]` reads `p1["message"]` directly, so
  proposals must always include `message`.
- The judge never calls the LLM: `[judge.py:DeterministicJudgeAgent.adjudicate]` is
  purely deterministic and grounded in `skintellect.formulation.scoring`; role prose
  must never replace the score calculation.
- Consensus thresholds in `[judge.py:DeterministicJudgeAgent.adjudicate]`:
  `predicted_match >= 90` → "Approved — High Compatibility", `>= 75` →
  "Conditionally Approved — Moderate Fit", otherwise "Rejected / High Friction —
  Incompatible".
- LLM-first, deterministic fallback: agents call the LLM only when
  `[llm.py:LLMClient.has_any_key]` is true; `[llm.py:LLMClient.chat_complete]` returns
  `None` when mode is offline, the key is missing, or `GeminiUnavailable` is raised,
  and each agent then substitutes rule-based prose. A missing/failed LLM must never
  abort deliberation.
- Telemetry is single-slot: `[llm.py:LLMClient.last_telemetry]` is overwritten on each
  `chat_complete` call and read once by `run_deliberation` to build the `telemetry`
  block (mode/provider/model/latency_ms/key_summary/error).
- Safety-critic fungal flagging is persona-gated: the Malassezia flag is appended only
  when `persona.safety_exclusions.fungal_acne_safe` is truthy
  (`[safety_critic.py:SafetyCriticAgent.audit_formulation]`).

## Side Effects

- stdout: `[board.py:BoardOrchestrator.run_deliberation]` prints a delimited
  deliberation banner (persona, engine provider/model/latency, per-round counters) to
  standard output on every call.
- Timing delays: `[board.py:BoardOrchestrator.stream_deliberation]` sleeps 0.3 s after
  the init frame and 0.4 s between rounds to pace the SSE stream.
- Network: `[llm.py:LLMClient.chat_complete]` performs live Gemini API calls via
  `GeminiClient.structured('legacy_agent', ...)` when a key is configured; each of the
  three LLM-capable agents may trigger such calls per round.
- Environment read: `[llm.py:LLMClient.__init__]` reads the `AGENT_LLM_MODE` environment
  variable (falling back to the constructor `mode="auto"`); `"offline"` disables all
  LLM calls.
- In-memory state mutation: `[llm.py:LLMClient.last_telemetry]` is rewritten on every
  call attempt (success, offline, or error). The package writes no files; persona and
  scoring data are read from `skintellect` modules. In offline/mock mode no database
  writes occur, but live LLM calls write `gemini_runs` telemetry and `gemini_cache`
  rows through the shared transport (`src/skintellect/gemini.py:GeminiClient.structured`).

## Verification

From the repository root:

```
python -m experiments.smoke_agents
```

Runs the board/CSI smoke checks (`experiments/smoke_agents.py:test_individual_agents`,
`experiments/smoke_agents.py:test_board_orchestrator`) with `AGENT_LLM_MODE=offline` forced, so
they need no API key or network. The experiments unittest file also exercises this
package (`python -m unittest experiments.test_experimental_features`). Repo-level API
smoke: `python -m tests.smoke_api`. No pytest is configured for this repository.
