# Advanced-study experiments

This area is for four explicit learning tracks alongside the
[buyer-facing MVP+](../docs/PROJECT_SPEC.md). Experiments are opt-in and are not
main-release acceptance requirements. Future experimental implementations and
their study notes belong here; the files currently added are specifications,
not runnable implementations.

The [feature retirement study](../docs/FEATURE_RETIREMENT_STUDY.md) maps the
existing runtime callers that must be detached when these tracks are isolated.

| Track | Current baseline | Planned advanced study |
| --- | --- | --- |
| Specialist agent board | The application has a sequential specialist board and deterministic judge. It does not currently use LangGraph. | Implement a separate board using LangGraph state, role nodes, bounded branching and inspectable execution. |
| Label-image transcription | The application has an experimental Gemini label reader with image validation, uncertainty fields and recorded-formula comparison. | Study its behavior on readable, incomplete, blurred and misleading images, with explicit human review of transcription quality. |
| Ingredient CSI | The application compares tolerated/problematic ingredient sets and ranks candidate ingredients using heuristic patterns. | Preserve this as a separate study of explainable set comparisons, attribution and uncertainty; do not present candidates as established causes. |
| Standalone Formula Lab | The application analyzes raw ingredient text with legacy heuristic scores, compatibility matrices and audit explanations. | Preserve this as an interactive formula-analysis study, with visible limitations and independently inspectable scoring reasons. |

## Specialist agent board using LangGraph

**Purpose:** learn and demonstrate multi-agent coordination on a concrete
ingredient/formula assessment, then evaluate whether the board adds value over
the main research workflow.

- Use a shared graph state containing the question, recorded formula, persona,
  evidence, specialist findings, remaining budget and final result.
- Represent evidence gathering, formulator commentary, critique, microbiome
  heuristics and deterministic judging as explicit stages. The specialists are
  software roles, not independent clinical authorities.
- Ground role outputs in available evidence and existing domain facts. Retain
  exact attribution, conflicting findings and insufficient-evidence outcomes.
- Permit a bounded rebuttal when a critique needs an answer; otherwise finish.
  Terminate on the agreed turn, call or time budget rather than debating indefinitely.
- Reuse existing domain operations and provider transport. Preserve deterministic
  scoring; role-generated prose must not replace the score calculation.
- Expose selected paths, role outputs, stop reason, latency and usage for study.
- Compare supported conclusions, unsupported claims, disagreement handling and
  resource use against the main research workflow on the same bounded cases.

The baseline implementations are documented in the
[agent module guide](../docs/modules/agents.md). They remain in their current
runtime locations until a separately verified migration is needed.

## Label-image transcription

**Purpose:** study how reliably an ingredient declaration can be transcribed
from a photograph and reconciled with a recorded formula.

- Reuse the existing [label reader](../src/skinsort/research/labels.py) as the
  starting point; avoid creating a duplicate transcription service.
- Accept validated PNG/JPEG inputs, preserve printed ingredient order, and
  report unreadable or uncertain text explicitly. Do not reconstruct hidden text.
- Compare transcribed names with the selected recorded formula and show shared,
  image-only and catalog-only names, with possible variant/version differences.
- Keep extraction separate from human verification. A complete-looking photo
  must not automatically update the catalog or certify formula completeness.
- Use a small labeled image set to inspect ingredient omissions, additions,
  ordering errors and uncertainty handling. Store fixture images only when
  needed for a concrete check; avoid empty fixture or test folder scaffolding.
- Retain the current provider-backed approach initially. LangGraph is required
  for the board track; add orchestration to image study only when a real
  multi-step workflow warrants it.

## Ingredient CSI

**Purpose:** explore differences between ingredient lists from products a user
reports tolerating and products they report reacting to.

- Reuse the existing [detective](../src/skinsort/agents/detective.py) and its
  ingredient normalization/pattern logic rather than building another engine.
- Show shared and differing ingredients and the reasons for candidate rankings.
  Preserve source attribution and explicitly identify missing formula data.
- Treat results as hypotheses from reported experiences, not diagnoses or proof
  of allergy, irritation or breakout causation.
- Evaluate overlapping ingredients, equivalent ingredient names, missing lists
  and cases with no distinguishing candidates using synthetic inputs.
- Keep the study separate from the buyer preference-match score. LangGraph is
  required for the specialist board; this track can retain its existing
  deterministic approach.

## Standalone Formula Lab

**Purpose:** inspect an arbitrary ingredient declaration and study how its
classification and heuristic scoring produce an explanation.

- Reuse existing [formula analysis](../src/skinsort/formulation/formulas.py),
  [legacy scoring](../src/skinsort/formulation/scoring.py) and validation models.
  Preserve the raw-input interface and inspectable audit explanations.
- Label compatibility matrices, concern scores and final scores as unvalidated
  heuristics. A list of names does not establish concentrations, pH, finished-
  product performance or individual suitability.
- Keep name matching and provided ingredient flags distinguishable. Reuse core
  ingredient facts; avoid copying the matching knowledge into the experiment.
- Check parsing, missing/unrecognized ingredients and score/explanation
  consistency on small fixed cases. Compare changes against the preserved
  baseline before changing historical scoring policies.
- Keep core catalog persona matching and recorded-formula explanations in the
  main product. The standalone raw-text lab is the experiment, not those shared
  buyer capabilities.

## Execution and verification boundaries

- The main application must not import experimental implementations. Experiments
  can call public runtime operations, keeping dependency direction one-way.
- Existing runtime routes and tests remain functional; creating this area does
  not move or remove their implementations.
- Use disposable catalogs and synthetic inputs for development. Keep source
  Nykaa files read-only and review authors' personal information out of fixtures
  and presentation traces.
- Use the project's existing test suite for automated regressions; avoid adding
  another test tree simply because the study has its own folder.
- Provider calls require explicit execution with a bounded budget. Default
  verification uses injected provider doubles; importing a study must not make
  calls, read the working catalog or start jobs.
- The relationship graph stays in the main MVP+ and is not an experiment here.
