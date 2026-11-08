# Research (Evidence-Backed Product Research)

## Overview
Bounded, evidence-backed research subsystem for the Skintellect catalog. It interprets natural-language queries, enforces deterministic ingredient eligibility, extracts aspect-based review observations (with optional Gemini support), builds a hybrid BM25 + vector retrieval bundle, and assembles a single `assistant_query` workflow response whose answer text is restricted to exact source excerpts. Lower-level modules do not depend on `service.py` ([service.py:module docstring]).

## Interface
- `[service.py:assistant_query]` - master workflow entry point; returns answer, search results, review insights, alternatives, references, evidence bundle, synthesis, and a timing/token `trace`.
- `[search.py:interpret]` / `[search.py:interpret_baseline]` - intent interpretation (Gemini structured intent over an offline rule parser); `[search.py:structured_search]` - deterministic eligibility-filtered product search; `[search.py:eligibility]`, `[search.py:brief]` - per-product constraint checks and canonical product brief.
- `[models.py]` - pydantic contracts: `SearchIntent`, `QueryRequest`, `AlternativeRequest`, `ReviewObservation`, `ReviewExtraction`, `EvidenceSelection`, `ResearchAnswer`, `ResearchPlan`, `ExtractionRequest`, `LabelExtraction`, `DecisionReviewInput`, `ReviewDecisionRequest`, `StrictModel`, `normalize_aspect`, `KNOWN_ASPECTS`. Note: `models.py` concatenates repeated definition blocks; the last definition of each class wins.
- `[evidence.py:check_ingredient]`, `[evidence.py:ingredient_matches]` - three-state (pass/fail/unknown) ingredient constraint checks; `[evidence.py:evidence]` - resolves `product:<id>` / `review:<id>` / `source:<id>` evidence IDs from the database; `[evidence.py:RULE_VERSION]` = `"foundation-1"`.
- `[reviews.py:review_insights]` - aspect summaries and verbatim observations for a product.
- `[review_store.py:ReviewCorpus]` - review source identity, duplicate policy, cached observation storage (`read`, `cached`, `save`); `[review_store.py:extract_review]` - deterministic regex ABSA baseline; `[review_store.py:ASPECTS]`, `[review_store.py:EXTRACTION_VERSION]` (`review-rules-1`).
- `[model_steps.py:extract_intent]`, `[model_steps.py:analyze_review_batch]`, `[model_steps.py:choose_plan]`, `[model_steps.py:select_answer_evidence]`, `[model_steps.py:review_client]` - Gemini-powered steps with deterministic validation; version flags `[model_steps.py:INTENT_VERSION]` (`gemini-intent-4`), `[model_steps.py:REVIEW_VERSION]` (`gemini-aspects-2-open`), `[model_steps.py:PROMPT_BOUNDARY]`.
- `[retrieval.py:retrieve_hybrid]` - BM25 + vector reciprocal-rank fusion; `[retrieval.py:lexical]`, `[retrieval.py:corpus]`, `[retrieval.py:index_embeddings]`, `[retrieval.py:retrieve]`, `[retrieval.py:digest]`.
- `[passage_index.py:PassageIndex]` - acceptance, validation, and persistence of saved passage vectors (`read`, `save`, `_decode`); `[passage_index.py:PassageState]`.
- `[alternatives.py:alternatives]` - weighted recorded-ingredient similarity; `[alternatives.py:get_dupes_for_product]` - legacy dupe response adapter.
- `[connections.py:connections]` - small evidence graph projected from recorded facts and reference topics.
- `[references.py:ingest_references]`, `[references.py:references]`, `[references.py:source_passages]`, `[references.py:SOURCE_FILE]` - attributed reference notes loaded from `reference_sources.json` (entries `fda-label-order`, `aad-dry-skin`, `niacinamide-33038007`).
- `[labels.py:read_label]` - experimental Gemini label-photo transcription (returns comparison only; never changes catalog).
- `[preparation.py:prepare_reviews]` - resumable batched review extraction; `[preparation.py:main]` - module CLI: `python -m skintellect.research.preparation status|reviews|embed|smoke`.
- `[jobs.py:create_job]`, `[jobs.py:execute]`, `[jobs.py:cancel]`, `[jobs.py:snapshot]`, `[jobs.py:history]`, `[jobs.py:recover_interrupted]`, `[jobs.py:initialize]` - durable single-worker preparation queue backed by the `preparation_jobs` table.

## Invariants
- All request/response models derive from `[models.py:StrictModel]` with `extra='forbid'`: unknown fields are rejected.
- `[search.py:structured_search]` returns no products and `needs_clarification` when `intent.unresolved_terms` is non-empty; seed records (`is_seed != 0`) are always excluded; products with `unknown` ingredient checks are withheld rather than guessed.
- `[evidence.py:check_ingredient]` returns status `unknown` when a required/excluded ingredient is absent from a formula whose completeness is unverified; absence is never treated as confirmation.
- `[model_steps.py:extract_intent]` unions the rule baseline's `unresolved_terms`, `excluded_ingredients`, and `required_ingredients` into the model output - a model cannot erase a known blocking issue; excluded ingredients override required ones (`normalize` comparison).
- `[model_steps.py:analyze_review_batch]` raises `GeminiUnavailable('review_evidence_validation_failed')` unless every observation's quote is an exact substring of the allowed review text; `[model_steps.py:select_answer_evidence]` raises `GeminiUnavailable('answer_evidence_validation_failed')` unless each selection quote exists verbatim in the source document.
- `[review_store.py:ReviewCorpus._valid]` accepts only observations whose `span` exactly matches the `cleaned_text[start:end]` slice and whose sentiment is in {positive, negative, neutral, mixed}; `[review_store.py:ReviewCorpus.read]` flags duplicates by identity `(product_id, whitespace-normalized casefolded text)`.
- `[passage_index.py:PassageIndex._decode]` rejects vectors whose stored `content_hash` no longer matches the document or whose L2 norm deviates from 1 by more than 0.001 (stale vectors are never used).
- `[jobs.py]` enforces at most one active preparation job via the partial unique index `one_active_preparation_job` (`jobs.py:initialize`) and the module lock `[jobs.py:_worker_lock]`; `[jobs.py:recover_interrupted]` must run once at startup, marking queued/running jobs `interrupted` with error code `server_restarted`.
- `[references.py:ingest_references]` accepts only `https` URLs whose hostname is in {`www.fda.gov`, `www.aad.org`, `pubmed.ncbi.nlm.nih.gov`} and IDs matching `[a-z0-9-]{1,100}`; `[references.py:references]` skips rows whose sha256 no longer matches `content_hash`.
- `[labels.py:read_label]` never mutates formula verification: the response carries `formula_verification_changed: False` and `human_verified: False`; only `image/png` and `image/jpeg` with matching magic signatures and size caps (8 MB base64 / 6 MB raw) are accepted.
- `[service.py:assistant_query]` always appends `retrieve` to a plan containing `reviews` (review summaries require source passages) and wraps all model work in `run_budget(max_calls=6, max_seconds=120)`.

## Side Effects
- SQLite writes: `review_aspects` (`[review_store.py:ReviewCorpus.save]`), `research_vectors` (`[passage_index.py:PassageIndex.save]`), `preparation_jobs` (`[jobs.py:create_job]`, `[jobs.py:execute]`, `[jobs.py:cancel]`), `source_documents` (`[references.py:ingest_references]`); `migrate()` and `ensure_tables()` schema setup in `[preparation.py:main]`.
- Gemini provider calls (HTTP via `urllib` / Google SDK): `[model_steps.py:extract_intent]`, `[model_steps.py:analyze_review_batch]`, `[model_steps.py:choose_plan]`, `[model_steps.py:select_answer_evidence]`, `[labels.py:read_label]`, `[retrieval.py:index_embeddings]`, `[retrieval.py:retrieve_hybrid]` (query embedding); all recorded in the `gemini_runs` table by `skintellect.gemini`.
- Environment variables read: `RESEARCH_HYBRID_ENABLED` (`[service.py:assistant_query]`), `GEMINI_ABSA_MODEL` (`[model_steps.py:review_client]`).
- File read: `reference_sources.json` (`[references.py:SOURCE_FILE]`).
- In-memory throwaway FTS5 index per call (`[retrieval.py:lexical]`), with a Python-side scoring fallback when the SQLite build lacks FTS5.
- Thread synchronization: `[jobs.py:_worker_lock]`; cooperative cancellation polls `preparation_jobs.cancel_requested` between batches.
- stdout JSON output from the `[preparation.py:main]` CLI (including an explicit `{'status':'unavailable'}` payload and exit code 2 on `GeminiUnavailable`).

## Verification
- Python backend; no pytest configured. From the repository root run:
  `python -m tests.smoke_api`
  `python -m tests.run_legacy_direct`
- Research preparation jobs and the prepared study group exercised by these smoke commands rely on `skintellect.research.jobs` and `skintellect.research.service`.
