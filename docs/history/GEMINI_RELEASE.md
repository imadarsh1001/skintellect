> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Gemini research implementation

The preparation dashboard is now implemented; see [version 2.8.0](PROGRESS_RELEASE.md)
for job controls, current-model coverage, validation and operating limits.

The project environment reconnected and the next release was implemented locally.
The previous release is preserved under `backups/before_gemini_20261022T195254Z/`.

## Configuration and live verification

The three supplied files are present in the project root and have been reviewed. The
application now loads the supplied GOOGLE_API_KEY, GOOGLE_CLOUD_PROJECT,
GOOGLE_CLOUD_LOCATION, API_ENDPOINT and MODEL_ID fields. This configuration selects
Google Cloud's global Gemini 4 Argon endpoint, rather than the Developer API.
The key remains in .env; inline copies in docs/API_USAGE_GUIDE.md were replaced with
placeholders. The supplied demo client's error reporting and billing claims were hardened.

Live checks passed for basic generation, typed review extraction on an authored example,
and a 768-dimensional synthetic query embedding. Native Cloud responseSchema is used
with references flattened and minimal schema keywords; Pydantic still enforces bounds
locally. Gemini 4 Argon uses thinkingLevel=LOW by default for extraction, with no
unsupported sampling controls. Thinking level is configurable.

The Cloud embedding surface uses single-instance predict calls. The pipeline commits
each successful vector before consuming another request budget, so preparation can resume.
Cloud embedding token statistics are recorded, and truncated input is rejected.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) '.runtime'
python -m skintellect.research.preparation status
python -m skintellect.research.preparation smoke
```

The user explicitly authorized sending stored product descriptions, ingredient lists and
cleaned review text to the configured Google Cloud endpoint. This authorization persists
for the project work. Reviewer names and other reviewer identity fields are excluded.
The previously blocked jobs were resumed after approval.

The prepared sample currently includes 34 model-processed reviews across two products
and 13 embedded passages. This is a bounded validation sample, not full-catalog indexing.
Product-scoped embedding preparation is supported with `--product-id`, so a demo product
can include its catalog passage and review evidence without indexing unrelated records.

A live comparison on twelve authored synthetic examples measured exact aspect/sentiment/
negation tuple F1 of 1.000 for the rules and 0.917 for Gemini. Gemini treated "strong scent"
as negative, while the authored label is neutral. These are smoke fixtures, not a held-out
real-review benchmark; they do not establish that either method is better in production.
See `reports/history/live_review_nlp_comparison.json`.

Live testing also exposed a model intent failure: ceramides were treated as ambiguous and
research instructions were confused with filter constraints. The adapter now preserves
known required ingredients, resolves the supported ceramide family, separates follow-up
research instructions, and recovers an explicit category when the model omits it.
Review-summary plans automatically receive their retrieval dependency even if the model
omits that tool. Regressions cover both cases.

The final live assistant check found 25 eligible moisturizers and completed intent
interpretation, review retrieval, alternatives, hybrid RRF retrieval and source-excerpt
selection. Its quote resolved to the retrieved source. That run took about 52 seconds
with cached intent/planning and two provider attempts; cold requests may take longer.
This latency and the small semantic index remain practical limitations.

All 29 observations in the 34 prepared reviews have exact matching source spans.
Original catalog, ingredient, linkage, review, queue and persona tables are unchanged,
and SQLite integrity checks pass. The final regression run passed 59 tests with one
HTTP transport test skipped. See `reports/history/approved_preparation_validation.json` and
`reports/history/live_assistant_result.json` for the recorded checks.

Billing and promotional-credit eligibility are not established by the endpoint; verify
those in the Cloud account. No guaranteed cost or credit-coverage claim is made.

## Implemented capabilities

| Capability | Implementation |
| --- | --- |
| Typed intent extraction | Native JSON Schema output plus local Pydantic validation; known exclusions and clarification blockers survive model parsing |
| Review NLP | Offline batch extraction of aspect, sentiment and negation; exact source quotes and review IDs checked before persistence |
| Grounded answers | Gemini selects passages; only exact excerpts from the current evidence bundle are presented as factual evidence |
| Tool planning | Model selects among reviews, alternatives and retrieval; typed allowlist; no arbitrary SQL, code or write tools |
| Hybrid retrieval | SQLite FTS5 BM25 with stemming, Gemini document/query vectors and reciprocal-rank fusion; lexical fallback is explicit |
| Resumable preparation | Review hashes/extraction versions and document hashes/model IDs skip unchanged work; stale vectors are withheld |
| Usage and reliability | Header-only credentials, redacted error codes, bounded retries, per-run request/time budgets, structured output cache and token/latency events |
| Interface | Actual model configuration status, evidence excerpts and citations, workflow traces, and a bounded review-analysis action |
| Evaluation | Synthetic smoke benchmark runner plus support for an externally annotated JSONL dataset; no fabricated model-quality results |

Gemini is used for language tasks, not to override ingredient checks or certify product
safety. A review quote establishes what was reported, not whether it is representative.
Exact quote matching checks provenance, not semantic entailment; a model can still select
an irrelevant or misleadingly narrow passage. Inspect the cited source and evaluate
selection quality with human judgments.

## Prepare the corpus incrementally

```powershell
# Process a small review sample, then rerun to resume.
python -m skintellect.research.preparation reviews --limit 20 --max-calls 8

# Optionally restrict review processing to one catalog product.
python -m skintellect.research.preparation reviews --product-id 12345 --limit 20

# Embed a bounded sample. Repeat to extend the index without repeating unchanged text.
python -m skintellect.research.preparation embed --product-id 10256 --limit 5 --max-calls 5

# Compare authored smoke examples; repeat with --mode both after configuring Gemini.
python -m scripts.evaluate_review_nlp --mode rules --output reports/history/review_nlp_smoke.json
python -m scripts.evaluate_review_nlp --mode both --output analysis/review_nlp_comparison.json
```

Reviews are sent as ID + visible cleaned text, without author names or skin-type fields.
Embedding preparation sends catalog descriptions/formulas and visible review text.
Provider calls occur only when Gemini is enabled and a key exists. The browser review
action processes at most 20 reviews per request; normal review-panel reads make no
extraction calls. Interactive research has a shared budget of six provider attempts and
120 seconds. Pipeline commands also have explicit call and time budgets.

The embedding index is intentionally partial until preparation has been run. Responses
expose `semantic_coverage`, `scoped_documents` and `semantic_status`, so a small vector
index cannot masquerade as a fully indexed catalog. Unchanged document embeddings are
reused; query vectors are generated on demand.

`gemini_cache` stores successful schema-valid outputs using model/task/prompt/schema/input
hashes. `gemini_runs` stores safe task usage metadata; `research_vectors` stores vectors.
No original product, ingredient, review or persona data is rewritten.

## Validation and limitations

Provider behavior is exercised using deterministic mock responses, including invalid
JSON schemas, invented citations, wrong review IDs, truncated generation, retry budgets,
credential redaction, cache invalidation and resumed indexing. These checks validate the
integration logic; they do not establish live provider compatibility or model accuracy.

Validation for this release: 59 regression tests passed; one HTTP transport test was
explicitly skipped for sandbox loopback restrictions. The existing direct API assertion
suite and legacy offline agent suite passed. JavaScript syntax and Python compilation
checks passed. Original data tables compare unchanged against the pre-Gemini snapshot,
and SQLite integrity checks passed (`reports/history/gemini_preservation.json`). The twelve
synthetic review fixtures pass the rule baseline; the live synthetic comparison above has now completed. The Cloud adapter checks also passed.

Run the tests with the documented local runtime:

```powershell
$env:SKINTELLECT_SKIP_HTTP = '1' # Needed only in the restricted execution sandbox.
python -m unittest discover -s tests -v
python tests/run_legacy_direct.py
python agents/test_agents.py
node --check src/skintellect/web/static/js/research.js
```

Live HTTP/browser checks remain blocked by sandbox loopback networking. Live Gemini
connectivity is verified; approved sample preparation has completed; the remaining corpus is intentionally unindexed. The existing
foundation still records zero verified complete formulas; strict exclusions continue
to withhold unknown results.

## Portfolio experiments for Abhi

1. Annotate real reviews with aspects, polarity, negation and source spans; separate
   development and test splits by product/duplicate group.
2. Compare rules with Gemini using per-aspect precision, recall, F1 and attribution errors.
3. Judge retrieval examples blindly and compare lexical, vector and fused rankings.
4. Compare fixed tool plans with Gemini-selected plans using task quality, cost and latency.
5. Record failure cases: contradictory reviews, incomplete formulas, unknown exclusions,
   stale sources, partial embedding coverage and provider unavailability.

Optional graph, MCP, multimodal label OCR and formulation-version workflows remain later
experiments. This release does not imply that these have been implemented.

## Official interface references

- https://ai.google.dev/gemini-api/docs/generate-content/structured-output
- https://ai.google.dev/api/embeddings

Generation uses Google's REST endpoints. Embedding 2 uses the official Google Gen AI SDK
with environment-based Cloud authentication. Structured output receives local schema and
identity/span validation.

For the Embedding 2 adapter, migration status and independent ABSA model routing, see
[Embedding 2 and ABSA](EMBEDDING2_AND_ABSA.md) and
[Dynamic aspects and SDK](DYNAMIC_ASPECTS_AND_SDK.md). The SDK resolved the earlier REST
authentication blocker; migration reports record completion and activation. Historical
test counts and transport limitations above describe the initial release.
