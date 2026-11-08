# Experiments

## Overview

Advanced-study experimental track for the `skintellect` repository. This package
hosts four self-contained study modules (specialist agent board, ingredient CSI
detective, label OCR transcription, standalone formula lab) plus a standalone CLI and
an offline smoke suite. Experimental code here imports the shared domain engine from
`src/skintellect/` (scoring, ingredient facts, personas, Gemini transport) but is
kept out of the main release path. A human-maintained overview lives in `README.md`
alongside this contract; that file is developer documentation and is not generated or
modified by this contract.

## Interface

- `[run_agent_cli.py:main]` — standalone argparse CLI for the two interactive
  experiments. Flags: `--formula` (raw ingredient deck), `--persona` (default `uap`),
  `--question`, `--csi` (switch to CSI mode), `--csi-problems` and `--csi-safes`
  (semicolon-separated product names or decks), `--reaction`
  (`breakouts_acne` | `contact_dermatitis` | `fungal_acne`, default
  `breakouts_acne`).
  - `[run_agent_cli.py:run_board(args)]` — prints a
    `experiments.specialist_board.board.BoardOrchestrator.run_deliberation` debate
    transcript and final verdict.
  - `[run_agent_cli.py:run_csi(args)]` — prints an
    `experiments.ingredient_csi.detective.CSIDetective.investigate` suspect report.
- `[smoke_agents.py]` — offline verification suite ("Stage 6: Multi-Agent System &
  CSI Detective").
  - `[smoke_agents.py:test_individual_agents]` — proposal, audit, microbiome, and
    adjudication contract checks against a fixed sample deck.
  - `[smoke_agents.py:test_board_orchestrator]` — full 5-round deliberation, verdict
    and telemetry assertions.
  - `[smoke_agents.py:test_csi_detective]` — differential isolation of a known pore
    clogger at 100% recurrence.
  - `[smoke_agents.py:test_decoupled_router]` — skipped gracefully when
    `skintellect.api.agents` is unavailable (retired router).
- Subdirectory contracts (generated, EGM-compliant):
  - [specialist_board](./specialist_board/EGM.md) — 5-round adversarial agent board
    with a deterministic judge grounded in `skintellect.formulation.scoring`.
  - [formula_lab](./formula_lab/EGM.md) — reverse-engineered heuristic scoring
    engine, deep formula analysis service, and pydantic request/response contracts.
  - [ingredient_csi](./ingredient_csi/EGM.md) — set-differential breakout/allergy
    investigator with chemical-family clustering and suspect scoring.
  - [label_ocr](./label_ocr/EGM.md) — experimental Gemini label transcription with
    image validation; never changes formula verification.

External dependencies (repository paths): `src/skintellect/formulation/scoring.py`,
`src/skintellect/formulation/ingredient_facts.py`, `src/skintellect/catalog/personas.py`,
`src/skintellect/catalog/store.py`, `src/skintellect/gemini.py`,
`src/skintellect/config.py`.

## Invariants

- Experiments are opt-in study tracks and are not main-release acceptance
  requirements; the track scope is defined by the human-maintained `README.md` in
  this directory.
- `[run_agent_cli.py]` and `[smoke_agents.py]` self-bootstrap `sys.path` (repository
  root, `src/`, and for the smoke suite `.runtime/` — the optional
  dependency-fallback directory, see docs/DEVELOPMENT.md) before importing
  `experiments.*` or `skintellect.*`, so both run standalone from the repository root.
- `[smoke_agents.py]` forces `os.environ["AGENT_LLM_MODE"] = "offline"` at import
  time; the smoke checks are deterministic, key-free, and make no network calls.
- The CLI defaults are deliberate: board mode without `--csi`, persona `uap`, and a
  fixed default question ("Evaluate barrier safety and active balance");
  `[run_agent_cli.py:run_board]` substitutes a fixed sample deck when `--formula` is
  omitted.
- Child packages never write catalog/product tables; `CSIDetective` lookups and the
  Formula Lab ingredient cache are read-only, but `label_ocr` and live-mode Specialist
  Board LLM calls write Gemini telemetry/cache rows (`gemini_runs`/`gemini_cache`)
  through the shared transport (`src/skintellect/gemini.py:GeminiClient.structured`).

## Side Effects

- `sys.path` mutation at import in `[run_agent_cli.py]`, `[smoke_agents.py]`, and
  `[test_experimental_features.py]` (test file; see Verification).
- Environment mutation: `[smoke_agents.py]` sets `AGENT_LLM_MODE=offline` at import
  and never restores it in that process.
- stdout: banners and reports from `[run_agent_cli.py:main]`,
  `[smoke_agents.py]` (progress and summary lines), and the board's own
  deliberation banner ([specialist_board](./specialist_board/EGM.md)).
- Network: live Gemini calls occur only when `AGENT_LLM_MODE` is not `offline` and a
  key is configured (board agents, [specialist_board](./specialist_board/EGM.md));
  [label_ocr](./label_ocr/EGM.md) `read_label` always performs one Gemini call.
- SQLite reads: product/ingredient lookups via
  [ingredient_csi](./ingredient_csi/EGM.md) and [formula_lab](./formula_lab/EGM.md).

## Verification

From the repository root:

```
python -m experiments.smoke_agents
python -m tests.smoke_api
```

- `experiments.smoke_agents` runs the board/CSI smoke checks offline (no API key, no
  network). Note: `docs/DEVELOPMENT.md` and `docs/modules/agents.md` still reference
  `python -m tests.smoke_agents`, but no `tests/smoke_agents.py` exists — the runnable
  module is `experiments/smoke_agents.py`.
- `tests.smoke_api` runs the repository API smoke check.
- `test_experimental_features.py` in this directory is a `unittest`-based test file,
  not production code; run it with
  `python -m unittest experiments.test_experimental_features`. It covers Formula Lab,
  Ingredient CSI, and the Specialist Board, forcing `AGENT_LLM_MODE=mock` per test.
- No pytest is configured for this repository (`pyproject.toml` defines no pytest
  settings).
