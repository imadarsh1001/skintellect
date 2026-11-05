> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Dynamic review decisions and Google SDK embeddings

## Open aspect discovery

The previous Gemini extraction schema restricted aspect and answer-topic names to eight
enum values. The current schema accepts concise validated aspect identifiers instead.
The original categories are starter hints, not an exhaustive list. Exact known synonyms
are normalized conservatively; unknown labels remain available for discovery.

Sentiment remains a fixed enum: positive, negative, neutral or mixed. Every observation
still requires a valid review ID and exact supporting source quote. Source offsets are
computed by Python. New themes are marked provisional with `is_discovered_aspect` and
shown in summaries, product previews, filters and source cards. No numeric confidence
is invented. Label discovery does not establish that the taxonomy or classification is
correct; it requires in-domain annotation and consolidation.

New extraction results use `gemini-aspects-2-open:<model>`. Legacy rows and response caches
are preserved. `skintellect.research.upgrades` selects only previously processed reviews
whose source hashes still match, saves batches, validates quotes, and activates the chosen
review model only after all selected results validate. The completed migration validated all 58 selected reviews and activated
`gemini-3.5-flash-lite` for extraction, preserving 58 prior Argon results. It discovered
13 labels outside the starter list, including oil control, breakouts, ingredients and
soothing. Overlapping names such as effectiveness/overall_effectiveness and
redness/redness_and_irritation remain provisional, not silently merged. The report is
`reports/latest/dynamic-absa-migration.json`.

## Structured decision endpoint

`POST /api/decisions/reviews` accepts 1–5 review objects with unique positive integer IDs
and nonblank text (up to 12,000 characters per review). It invokes the configured Gemini
review model with structured output and a three-attempt, 120-second provider budget.

Example request:

```json
{"reviews":[{"id":1,"text":"The pump broke, but the cream absorbs quickly."}]}
```

The normalized response includes schema version, model, observations, discovered aspect
names, source-validation status and provider attempts. Each observation has an input-source
reference, source span and offsets. Confidence is null with status `not_calibrated`; no
probability is fabricated. Input source IDs are scoped as `input:review:<id>` and do not
pretend to reference a catalog evidence record. The endpoint does not add these reviews
to the catalog. Hosted requests may be billed and are subject to the existing cache.
Jev and DecisionAPI were not integrated; this contract uses the existing Gemini service.

The live HTTP smoke discovered `white_cast` and validated the returned source spans,
but omitted a broken-pump experience in the same synthetic review. Structured output
constrains response shape; it does not guarantee exhaustive or correct extraction.
The exact smoke output is `reports/latest/dynamic-decision-smoke.json`.

## Why the SDK call worked

The user's `genai.Client(vertexai=True).models.embed_content(...)` worked in this environment.
The environment-based SDK client returned a 3,072-dimensional Embedding 2 vector. An
explicit API-key SDK client returned HTTP 404, while the previous project-scoped REST
API-key request returned HTTP 401. The SDK source confirms that project/location from
the environment take precedence over an implicit API key, selecting Cloud credentials.
The earlier blanket authentication-blocker conclusion was therefore too broad.

Embedding 2 now defaults to the official Google Gen AI SDK, using configured project and
embedding location with environment-based Cloud authentication. It requests the configured
output size (768 by default) and preserves our document/query retrieval formatting. A
custom REST transport remains available for contract tests and explicit compatibility use.
The legacy Embedding 001 REST path remains available for rollback.

SDK retries are limited to one attempt per outer attempt so application budgets and retry
telemetry remain meaningful. Credentials and provider bodies are not logged. The SDK is a
normal runtime dependency (`google-genai`); SOCKS support is installed for this environment's
proxy. No model server, vector database, GPU service or new deployment was introduced.

## Migrations and checks

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = "$PWD\.runtime"
python -m skintellect.research.upgrades embeddings --activate
python -m skintellect.research.upgrades reviews --model gemini-3.5-flash-lite --activate
python -m unittest discover -s tests -q
node tests/check_ui_semantics.js
```

The completed embedding migration validated all 35 selected passages at 768 dimensions
and activated Embedding 2. It preserved all 35 legacy vectors and did not embed the full
catalog. Commands are resumable; run budgets limit provider work.
The prepared-study evaluation was rerun after both migrations and its fingerprint is
current. All 104 regression tests, 31 UI semantic checks and the live legacy API suite
passed. Source spans validated for all 28 study reviews and all five selected answer
quotes. The seven weak-label queries gave hybrid MRR 1.0 and recall@3 0.9524; these
surface labels favor lexical retrieval and do not prove an embedding accuracy gain.
The model and rule extractor had low exact-set agreement (1/28), partly because they
now have different taxonomies; agreement is not accuracy. Human annotations are still
needed. Historical evaluation output is preserved in reports/history.

The updated local preview is http://127.0.0.1:8001/study. The earlier instance at port
8000 retains old code until restarted. Browser layout checks were unavailable.

References: [Google SDK](https://googleapis.github.io/python-genai/),
[embedding task formatting](https://ai.google.dev/gemini-api/docs/embeddings), and
[structured output](https://ai.google.dev/gemini-api/docs/structured-output).
