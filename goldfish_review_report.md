# Goldfish Annotated Review Report

Status: resolved & loop closed (2026-11-09 — Round 1: 20/20 applied; Round 2: 9/9 applied; Round 3: targeted verification of all 9 Round-2 edits returned ZERO findings; loop halted by user decision after clean verification; 0 open findings, 0 contested, 0 escalated, 0 declined)

**Target:** Round-0 drift-fix set — 8 EGM.md contracts (`full file` each): `src/skintellect/EGM.md`, `src/skintellect/formulation/EGM.md`, `src/skintellect/research/EGM.md`, `frontend/src/components/ui/EGM.md`, `experiments/EGM.md`, `experiments/formula_lab/EGM.md`, `experiments/specialist_board/EGM.md`, `scripts/EGM.md`

**Round 1 reviewers:** codebase_details (4 findings), comprehension (9), structural (7). **0 Blocker / 5 Major / 15 Nit.**
`codebase_details` verified all 10 Round-0 drift fixes as accurate against source. No CONTEST / ESCALATE / DECLINE below — every finding is valid and has a one-line-class fix; all are **PROPOSE FIX**.

---

## Prioritized Findings & AI Suggestions

### [1] "Peanut" is never defined anywhere in the doc set [`comprehension`] - Severity: Major
*   **Affected Scope:** frontend/src/components/ui/EGM.md#L4 (Overview; term also appears in other contracts)
*   **Discrepancy Description:** "Each package is a self-contained Peanut" — a fresh reader cannot tell whether a Peanut is a packaging convention, a framework, or tooling.
*   **Rationale:** Undefined project jargon carrying structural weight; no README or contract defines it.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Do-not-contest rule for comprehension gaps. Define at the flagged use and once at the doc-set entry point (root blueprint).
*   ***Proposed Edit:***
    *   Location: `frontend/src/components/ui/EGM.md` L4 + `EGM.md` (root) end of System Overview paragraph
    *   Change: ui — "Each package is a self-contained Peanut (EGM term: the leaf contract of a directory of direct source files) exporting its components from an `index.ts`." Root — after "…these code-grounded `EGM.md` contracts." insert "Terminology: a leaf package contract is a *Peanut*; a rollup contract is a *Blueprint* (Hay)."

### [2] `.runtime/` used but never explained (3 files) [`comprehension`] - Severity: Major
*   **Affected Scope:** experiments/EGM.md#L57-59, scripts/EGM.md#L50, src/skintellect/EGM.md#L33
*   **Discrepancy Description:** sys.path/PYTHONPATH claims reference `.runtime/` (and `.runtime/quality`) without saying what it is; "(outside a virtualenv)" conditional also unexplained.
*   **Rationale:** A reader cannot evaluate a bootstrap claim about a directory they can't identify (it is the optional dependency-fallback directory per docs/DEVELOPMENT.md).
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Comprehension gap spanning three contracts; gloss at each load-bearing use.
*   ***Proposed Edit:***
    *   Location: the three lines above
    *   Change: src/skintellect — "adds `<PROJECT_ROOT>/.runtime` paths (optional dependency-fallback directory, see docs/DEVELOPMENT.md) to `sys.path`". experiments — "and for the smoke suite `.runtime/` (optional dependency-fallback directory, see docs/DEVELOPMENT.md)". scripts — "and (outside a virtualenv, i.e. when no venv is active) `.runtime/quality` and `.runtime` (optional dependency-fallback directories, see docs/DEVELOPMENT.md)".

### [3] `fingerprints` returned by `ReviewCorpus.cached()` unexplained [`comprehension`] - Severity: Major
*   **Affected Scope:** src/skintellect/research/EGM.md#L12 (Interface)
*   **Discrepancy Description:** Round-0 fix names `PreparedReviews` (`observations` + `fingerprints`) but never says what a fingerprint is.
*   **Rationale:** Ground truth: `review_store.py:95` appends `(rid, input_hash, sha256(raw))` tuples — duplicate/staleness keys. The duplicate-policy invariant (L29) never connects to the word.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** The fix's whole purpose was closing this gap; half the payload is still an unexplained noun.
*   ***Proposed Edit:***
    *   Location: src/skintellect/research/EGM.md L12
    *   Change: "…`cached` returns a `[review_store.py:PreparedReviews]` dataclass (`observations` dict keyed by review id, plus `fingerprints` — `(review_id, input_hash, sha256(text))` staleness keys)"

### [4] `[maintenance.py:BENCHMARK_PRODUCTS]` has no module locant [`comprehension`] - Severity: Major
*   **Affected Scope:** src/skintellect/EGM.md#L28 (Invariants)
*   **Discrepancy Description:** Citation implies a package-root `maintenance.py`; the file actually lives in the `ingestion` child package.
*   **Rationale:** A reader searching beside `database.py` finds nothing; no child-package hint is given.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Ambiguous referent inside the invariant that carries the seed-isolation contract.
*   ***Proposed Edit:***
    *   Location: src/skintellect/EGM.md L28
    *   Change: "[maintenance.py:BENCHMARK_PRODUCTS]" → "[ingestion/maintenance.py:BENCHMARK_PRODUCTS]"

### [5] "a hard 100/35 for `fungal_safe`" notation ambiguous [`comprehension`] - Severity: Major
*   **Affected Scope:** experiments/formula_lab/EGM.md#L57 (Interface)
*   **Discrepancy Description:** "100/35" admits two parses (ceiling/floor vs binary values).
*   **Rationale:** Ground truth: `formulas.py:257` — `fa_score = 100 if is_fungal_safe else 35`; other types clamp to floors (combination 30, oily 25, dry 30, sensitive 20) with ceiling 100.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** The contract promises score values; both readings must not survive.
*   ***Proposed Edit:***
    *   Location: experiments/formula_lab/EGM.md L57
    *   Change: "…score floors are 30 (combination), 25 (oily), 30 (dry), and 20 (sensitive) with a 100 ceiling; `fungal_safe` is binary — exactly 100 when free of fungal triggers, 35 otherwise."

### [6] Round-0 edit misstates `check.py`'s no-install mechanism [`codebase_details`] - Severity: Nit
*   **Affected Scope:** scripts/EGM.md#L66 (Verification)
*   **Discrepancy Description:** New clause says all three commands "self-insert `src` on `sys.path`" — `check.py` never touches its own `sys.path` (stdlib-only; it builds the child-process environment, `check.py:32-35`).
*   **Rationale:** True conclusion (runs without installation), wrong mechanism for one of the three.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** My own Round-0 over-generalization; the pre-fix wording ("manages its own environment") was accurate for check.py.
*   ***Proposed Edit:***
    *   Location: scripts/EGM.md L66
    *   Change: "…except `python scripts/check.py` (stdlib-only; builds its own child environment), `python -m scripts.audit_workspace`, and `python scripts/test_copilot_intents.py` (these two self-insert `src` on `sys.path`) — all run without installation."

### [7] CLI-drift invariant conflates two call sites [`codebase_details`] - Severity: Nit
*   **Affected Scope:** src/skintellect/EGM.md#L29 (Invariants)
*   **Discrepancy Description:** `min_match`/`limit` are valid for `search_products`; `cmd_filter` passes `fungal_safe=` (valid), not `require_fungal_safe=`. Enumerated kwargs read as applying to both signatures.
*   **Rationale:** Verified signatures — `get_recommendations` (recommendations.py:77+) takes `country/min_match_score/must_be_*/max_pore_cloggers` and no `limit`; `search_products` (recommendations.py:244+) takes `country/min_match/fungal_safe/active_term/max_pore_cloggers/limit`. Real mismatches: cmd_recommend → `brand_country, min_match, limit, max_cloggers, require_*`; cmd_filter → `brand_country, active_ingredient, max_cloggers`. TypeError conclusion is correct.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** The invariant's example list is partially false as written, even though its conclusion holds.
*   ***Proposed Edit:***
    *   Location: src/skintellect/EGM.md L29
    *   Change: "`[cli.py:cmd_recommend]` calls `get_recommendations` with kwargs it does not accept (`brand_country`, `min_match`, `limit`, `max_cloggers`, `require_fungal_safe`, `require_oil_free`, `require_fragrance_free`, `require_alcohol_free`), and `[cli.py:cmd_filter]` calls `search_products` with (`brand_country`, `active_ingredient`, `max_cloggers`); invoking either subcommand raises `TypeError` until reconciled. `cmd_recommend` also prints `p['analysis']['soothers']` while the analysis groups are named `smoothers`."

### [8] "prefix" should be "suffix" [`codebase_details`] - Severity: Nit
*   **Affected Scope:** src/skintellect/formulation/EGM.md#L15 (Invariants)
*   **Discrepancy Description:** "overwrites every concern mechanism with a 'Product efficacy is unverified' prefix" — the phrase is appended at the end (`formulas.py:512-514`).
*   **Rationale:** Direction-of-composition error; the compatibility-status half of the sentence is accurate.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** One word, verifiable at the cited lines.
*   ***Proposed Edit:***
    *   Location: src/skintellect/formulation/EGM.md L15
    *   Change: "prefix" → "suffix"

### [9] Local `scoring.py` described as "re-exported" but is a diverged fork [`codebase_details`] - Severity: Nit
*   **Affected Scope:** experiments/formula_lab/EGM.md#L84-86 (Interface, External dependencies)
*   **Discrepancy Description:** "`src/skintellect/formulation/scoring.py` (re-exported here for `experiments` consumers)" — the local `scoring.py` imports nothing from src scoring and redefines all functions; the real cross-import is `formulas.py:20-26` importing four src-scoring functions; copies diverged (src's `score_any_product` also returns a legacy `skinsort_match` key, src scoring.py:400).
*   **Rationale:** "Re-export" wrongly implies identical behavior.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Misleading dependency claim in the Interface section.
*   ***Proposed Edit:***
    *   Location: experiments/formula_lab/EGM.md L84-86
    *   Change: "`src/skintellect/formulation/scoring.py` (imported by the local `formulas.py`; the local `scoring.py` is a diverged fork of it, not a re-export)"

### [10] `export_personas_json` / `cli.py:cmd_report` citations lack module locant / brackets [`comprehension` + `structural`] - Severity: Nit
*   **Affected Scope:** src/skintellect/EGM.md#L36 (Side Effects)
*   **Discrepancy Description:** "personas JSON (`cli.py:cmd_report` via `export_personas_json`)" — no brackets on `cli.py:cmd_report`, and `export_personas_json`'s owning module (`catalog/personas.py:196`) is never named.
*   **Rationale:** Breaks the file's citation convention and strands the function without a locant.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Two reviewers flagged the same line; one edit resolves both.
*   ***Proposed Edit:***
    *   Location: src/skintellect/EGM.md L36
    *   Change: "personas JSON (`[cli.py:cmd_report]` via `[catalog/personas.py:export_personas_json]`)"

### [11] "ABSA" acronym never expanded [`comprehension`] - Severity: Nit
*   **Affected Scope:** src/skintellect/EGM.md#L19 (child-package list; also used in research contract)
*   **Discrepancy Description:** "review ABSA" used as a load-bearing domain label with no expansion.
*   **Rationale:** Reader must connect "aspect-based review observations" (research/EGM.md L4) to the acronym unaided.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Expand once at the parent's first use.
*   ***Proposed Edit:***
    *   Location: src/skintellect/EGM.md L19
    *   Change: "review ABSA (aspect-based sentiment analysis)"

### [12] `analyze_ingredients` entry doesn't name what it wraps [`comprehension`] - Severity: Nit
*   **Affected Scope:** src/skintellect/formulation/EGM.md#L11 (Interface)
*   **Discrepancy Description:** Round-0 addition says "rule-table classifier wrapper returning the groups dict" without naming the wrapped function; sibling contract (experiments/formula_lab L116-118) shows the intended clarity.
*   **Rationale:** Delegation chain must be reconstructed by inference.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** One clause.
*   ***Proposed Edit:***
    *   Location: src/skintellect/formulation/EGM.md L11
    *   Change: "…`[scoring.py:analyze_ingredients]` - thin wrapper over `[ingredient_facts.py:classify_ingredients]` returning the groups dict (imported cross-module by `[formulas.py]`)"

### [13] "the prepared study group" has no antecedent [`comprehension`] - Severity: Nit
*   **Affected Scope:** src/skintellect/research/EGM.md#L49 (Verification)
*   **Discrepancy Description:** Entity introduced with no definition or pointer.
*   **Rationale:** Vague referent in the reproduce-it section; the concept is owned by `skintellect.research.study`.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Add the owning module as the pointer.
*   ***Proposed Edit:***
    *   Location: src/skintellect/research/EGM.md L49
    *   Change: "Research preparation jobs and the prepared study cohort (defined by `skintellect.research.study`) exercised by these smoke commands rely on…"

### [14-16] Verification smoke commands are lazy continuation lines (3 files) [`structural`] - Severity: Nit
*   **Affected Scope:** src/skintellect/EGM.md#L41-43, src/skintellect/formulation/EGM.md#L30-33, src/skintellect/research/EGM.md#L46-48
*   **Discrepancy Description:** Two commands indented under one bullet render as one run-on paragraph; experiments/* contracts use fenced blocks.
*   **Rationale:** Copy-paste of the rendered line yields one invalid command; cross-file inconsistency.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Mechanical formatting fix matching the existing experiments style.
*   ***Proposed Edit:***
    *   Location: the three Verification sections
    *   Change: keep the bullet's lead sentence, then a fenced block (indented inside the list item):
      "```\npython -m tests.smoke_api\npython -m tests.run_legacy_direct\n```"

### [17] `jobs.py:initialize` citation lacks brackets [`structural`] - Severity: Nit
*   **Affected Scope:** src/skintellect/research/EGM.md#L31 (Invariants)
*   **Discrepancy Description:** Bare `jobs.py:initialize` beside bracketed `[jobs.py:_worker_lock]` in the same sentence.
*   **Rationale:** Citation-convention consistency (tooling greps `[...]`).
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** One-character-class fix.
*   ***Proposed Edit:***
    *   Location: src/skintellect/research/EGM.md L31
    *   Change: "(`jobs.py:initialize`)" → "(`[jobs.py:initialize]`)"

### [18] `[service.py:module docstring]` merges prose into the symbol slot [`structural`] - Severity: Nit
*   **Affected Scope:** src/skintellect/research/EGM.md#L4 (Overview)
*   **Discrepancy Description:** Descriptor inside the citation brackets; other contracts keep it outside.
*   **Rationale:** Not greppable as a symbol reference.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Convention alignment.
*   ***Proposed Edit:***
    *   Location: src/skintellect/research/EGM.md L4
    *   Change: "([service.py:module docstring])" → "([service.py] module docstring)"

### [19] `[smoke_agents.py:…]` citations imply a local file that doesn't exist there [`structural`] - Severity: Nit
*   **Affected Scope:** experiments/specialist_board/EGM.md#L125-126 (Verification)
*   **Discrepancy Description:** `smoke_agents.py` lives in the parent `experiments/`, not in `experiments/specialist_board/`.
*   **Rationale:** The bracket convention implies the cited file is local to the documented package.
*   ***AI Suggestion:*** PROPOSE FIX
*   ***Justification:*** Qualify with the owning package.
*   ***Proposed Edit:***
    *   Location: experiments/specialist_board/EGM.md L125-126
    *   Change: "(`experiments/smoke_agents.py:test_individual_agents`, `experiments/smoke_agents.py:test_board_orchestrator`)"

---

**Round status:** Round 1 is NOT clean (5 unsettled Majors). After fixes are applied, the loop needs a Round 2 review; convergence = 2 consecutive clean rounds (cap 5).

---

# Round 2 (2026-11-09)

Reviewers: codebase_details (3), comprehension (3), structural (3). **0 Blocker / 1 Major / 8 Nit.** All Round-1 fixes re-verified: 19/20 correct; the one failure is finding R2-1 below (re-opened). All categorized **PROPOSE FIX**; all applied.

- **R2-1 [Major] [codebase_details]** research/EGM.md L52 — the Round-1 fix (finding 13) kept the false claim that the smoke commands "exercise" the research jobs/study cohort; neither `tests/smoke_api.py` nor `tests/run_legacy_direct.py` touches `skintellect.research.service`/`study` (verified: zero "research" references in both test files). → Rewritten: smoke commands exercise only the catalog API surface; jobs enter via API startup lifespan (`recover_interrupted`); the study cohort is exercised by `python -m scripts.evaluate_release`.
- **R2-2 [Nit] [codebase_details]** research/EGM.md L30 — content-hash staleness rejection is in `[passage_index.py:PassageIndex.read]` (passage_index.py:47), not `_decode` (which validates JSON/dimensions/L2 norm, :32). → Attribution split correctly.
- **R2-3 [Nit] [codebase_details]** formulation/EGM.md L11 — `parse_ingredients_input` also accepts semicolons (`re.split(r'[,;\n]')`, scoring.py:55); sibling contract already documented this. → "comma/semicolon/newline".
- **R2-4 [Nit] [comprehension]** EGM.md (root) L13 — Round-1 gloss planted an undefined token: "*Blueprint* (Hay)". → "(Hay)" dropped.
- **R2-5 [Nit] [comprehension]** src/skintellect/EGM.md L27 — `[response_model].model_validate_json` used bracket syntax for a conceptual placeholder. → unbracketed prose.
- **R2-6 [Nit] [comprehension]** formulation/EGM.md L21 — `get_catalog()` stranded without module locant. → "the catalog stamp from `[catalog/store.py:get_catalog]`".
- **R2-7 [Nit] [structural]** experiments/formula_lab/EGM.md (10 spots) — full parameter signatures inside bracket citation slots. → moved outside: `[scoring.py:fn] (args…)`.
- **R2-8 [Nit] [structural]** experiments/specialist_board/EGM.md (9 spots) — same pattern with dotted symbols. → moved outside.
- **R2-9 [Nit] [structural]** scripts/EGM.md L18 — bare `check.py:67` fit neither citation style. → `[scripts/check.py:67]`.

**Round status:** Round 2 is NOT clean (1 Major, re-opened from Round 1; now fixed). Next: Round 3; convergence = 2 consecutive clean rounds (cap 5).

---

# Round 3 (2026-11-09) — targeted verification, loop closure

Full R3+R4 swarms were waived by user decision (karpathy-guidelines review: predicted yield ~0-3 nits; R2 already clean at blocker/major per comprehension + structural). In their place, a single `codebase_details` reviewer verified ONLY the 9 Round-2 applied edits against source.

**Result: ZERO findings.** All 9 verified with line-level evidence — smoke-surface/lifespan/study claims (app.py:26-29, evaluate_release.py:21,59,109, zero research refs in both smoke tests), passage_index attribution (:47 read / :32 _decode), `re.split(r'[,;\n]')` (scoring.py:55), root terminology sentence, unbracketed response-model prose (gemini.py:300-302), get_catalog locant (store.py:163, formulas.py:35-37), all 10 formula_lab citation signatures exact (scoring.py:35,61,65,192,289; formulas.py:76,162,272,348,456), all 9 specialist_board citation signatures exact (board.py:28,44,113; formulator.py:23,118; safety_critic.py:23; microbiome.py:23; judge.py:26; llm.py:14,27), check.py:67 Node child confirmed.

**Loop final:** 3 rounds · 29 findings raised (0 blockers, 6 majors, 23 nits) · 29/29 fixed and verified · 0 open. Round 3 counted as the first clean round; second clean round waived by user acceptance.
