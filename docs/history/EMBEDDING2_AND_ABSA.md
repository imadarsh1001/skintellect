> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Embedding 2 upgrade and ABSA model routing

## Implemented

- `gemini-embedding-2` uses one `embedContent` call per document, preserving document
  boundaries instead of aggregating unrelated reviews.
- Retrieval queries use `task: search result | query: ...`; documents use
  `title: none | text: ...`, as documented by Google.
- Cloud requests use `embedContentConfig.outputDimensionality`; Developer API requests
  use `outputDimensionality`. The legacy `predict` path remains available for rollback.
- Dimensions are configurable through `GEMINI_EMBEDDING_DIMENSIONS` (default 768).
  Preparation, retrieval, coverage and readiness check the configured dimension.
- Vector caches remain separated by model. Query caches include task, dimensions and
  format version. Old model vectors are retained. Invalid/truncated outputs are rejected.
- `GEMINI_ABSA_MODEL` routes review extraction independently of the generation model.
  Review preparation, cached-insight reads, progress, readiness and agreement evaluation
  all use that model identity. Leaving it unset retains the existing extractor.

## Migration and authentication update

The initial REST/API-key attempt was blocked, but the user's Google SDK example worked
with environment-based Cloud credentials. The Embedding 2 adapter now uses that SDK path.
The old blocker is no longer the current conclusion. See [dynamic aspects and SDK](DYNAMIC_ASPECTS_AND_SDK.md)
for the implemented request path and current migration procedure. Exact completion and
activation states are recorded in `reports/latest/embedding2-migration.json`.

The migration preserves legacy vectors and activates only after all selected replacements
validate. It does not re-embed the full catalog. The optional access-token setting and old
REST path remain available, but no token is required when the SDK's Cloud credentials work.

## Lower-cost ABSA candidates

| Candidate | Useful role | Important limitation |
| --- | --- | --- |
| `yangheng/deberta-v3-base-absa-v1.1` | Local aspect-conditioned polarity classifier | Requires a supplied aspect; three-class polarity is not our full extraction schema |
| SetFitABSA | Few-shot aspect filtering and polarity pipeline | Needs domain labels and taxonomy mapping; published restaurant/laptop results are not cosmetics accuracy |
| `gemini-3.5-flash-lite` | Hosted structured extraction with existing quote validation | Candidate compatibility can be tested, but human-reviewed cosmetics labels are still needed |

ABSA includes aspect discovery, category mapping, sentiment, and source-span extraction.
A classifier that takes `(text, aspect)` does not replace all those stages. For a local
pipeline, identify the aspect and source clause first, classify its polarity, then combine
clause observations carefully when experiences conflict. Do not infer reliable confidence
thresholds without a labeled calibration set.

No Hugging Face weights or heavyweight inference dependencies were installed. No local
model accuracy or performance was claimed. ABSA model activation is recorded in the dynamic migration report; earlier Argon outputs
remain preserved. The hosted smoke report is
`reports/latest/absa-flash-lite-smoke.json`; it uses authored synthetic examples, not a
held-out cosmetics benchmark. Its F1 matches joint `(review, aspect, sentiment, negation)`
tuples, not sentiment accuracy alone.

Compare hosted candidates without replacing cached extraction results:

```powershell
python -m scripts.evaluate_review_nlp --mode both --model gemini-3.5-flash-lite --model gemini-4-argon --max-calls 12 --output reports/latest/absa-model-comparison.json
```

Supply `--dataset path/to/annotations.jsonl` for independently labeled reviews. The original
JSONL format is documented in `analysis/evaluate_review_nlp.py`. Synthetic examples can
catch integration errors but cannot determine the best production model. Bulk reprocessing
with a different model is intentionally not automatic.

## Official references

- [Google embedding task instructions and migration](https://ai.google.dev/gemini-api/docs/embeddings)
- [Cloud embedContent request and response](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest/v1/projects.locations.publishers.models/embedContent)
- [Cloud multimodal embeddings](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/get-multimodal-embeddings)
- [DeBERTa ABSA model card](https://huggingface.co/yangheng/deberta-v3-base-absa-v1.1)
- [SetFitABSA benchmark and training](https://huggingface.co/blog/setfit-absa)
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)

## Historical fixed-taxonomy ABSA smoke result

Before the open-aspect schema upgrade, `gemini-3.5-flash-lite` successfully completed all 12 authored smoke fixtures with exact
quote validation. Joint aspect/sentiment/negation tuple precision, recall and F1 were each
0.9167. The single mismatch was the fixture “The scent is strong.”: the authored policy
labels scent neutral, whereas the model labeled it negative. This is a useful annotation-
policy example, not a measured error rate for real cosmetics reviews. The run reused two
cached batches and made one new provider request after an earlier two-call budget stopped
before the final batch. These results do not replace independent in-domain labels.
