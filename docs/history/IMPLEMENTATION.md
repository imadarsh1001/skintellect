> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Evidence-backed research release

This document records the first release. The subsequent Gemini integration, new pipeline
commands and current key-import limitation are documented in [GEMINI_RELEASE.md](GEMINI_RELEASE.md).

Implemented in the existing project. The pre-change source archive, consistent SQLite
backup, archive checksum and restore mapping are in
`backups/before_implementation_20261022T183541Z/`.
The backup database passed `PRAGMA integrity_check` before changes.

## Launch

On this computer, run `./run-research.ps1`, then open
`http://127.0.0.1:8000/research`. The script uses the isolated `.runtime` dependencies
prepared from already downloaded packages. That directory is not application source.
For another computer, install `requirements.txt` into a virtual environment and run
`python -m uvicorn skintellect.api.app:app --host 127.0.0.1 --port 8000`.

## Implemented behavior

| Area | Behavior |
| --- | --- |
| Foundation metadata | Additive, idempotent migration; quality status, exact seed IDs, alias registry, source-document storage, review cache and rule registry |
| Formula unknowns | No substring identity guessing; missing ratings remain null; unknown ingredient status survives API serialization |
| Completeness | Presence is separate from verified completeness; verification requires a matching formula hash, source reference and review date |
| Search | Required/excluded ingredients, domain/category, approximate price preferences, pass/fail/unknown checks; unknown hard constraints withheld |
| Seed records | Excluded by default; legacy catalog can explicitly request `include_seeds=true` and returns `is_seed` |
| Provenance | Configured sources cannot generate verified source profiles or fabricated CIR verdicts |
| Routine checks | Normalized recorded formula names drive qualified co-occurrence observations; no certified-safe routine claims |
| Similarity | Weighted ingredient-frequency overlap alongside Jaccard, actual shared/added/removed ingredients; no concentration-equivalence claims |
| Review NLP | Rule baseline with clause-local negation, offsets, exact supporting spans, truncation flags, duplicate removal and unique-review denominators |
| Review cache | Input hash and extraction version invalidate old observations; raw review text remains intact |
| Retrieval | Lexical baseline over catalog facts and visible review text; stable resolvable evidence IDs |
| Research workflow | Interpret → deterministic search → up to three review analyses → retrieve → source-backed output, bounded execution and timing trace |
| Interface | Editable filters, clarification notices, product cards, expandable review/source/alternative panels; untrusted text inserted using DOM text APIs |

The migration does **not** automatically certify any formula. The current audit reports
576 recorded formulas and zero verified complete formulas. Thus a strict fragrance
exclusion can legitimately yield zero eligible records. Positive ingredient-presence
queries still work against the recorded formulas.

To record a human review after checking the full manufacturer label:

```powershell
python -m skintellect.ingestion.maintenance verify PRODUCT_ID --source LABEL_REFERENCE --reviewer REVIEWER_NAME
```

This attests to completeness of the exact stored text, not product safety. Formula
changes invalidate the attestation automatically. No catalog product was manually
certified as part of this implementation.

The fragrance policy includes Parfum/Fragrance and six explicitly listed fragrance
allergen names. It is a limited ingredient policy, not an exhaustive allergy detector.
`core/evidence.py` defines the exact policy. Other exclusions use exact canonical names.

## Model configuration

By default the feature makes **zero model calls**. Its parser and review extraction are
explicit rule baselines; generated clinical simulation output is not used as evidence.

Set `RESEARCH_LLM_ENABLED=1` to opt into model-based intent extraction through the existing
`skintellect.agents.llm.LLMClient` provider configuration. A provider key must be configured.
Invalid/unavailable output falls back to the labeled baseline. Baseline exclusion checks
and clarification blockers survive model extraction. This optional network path has not
been tested with a live provider. Review text extraction and final answers remain
deterministic. Query text is sent to the configured provider only when this is enabled.

## Validation

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) '.runtime'
python -m unittest discover -s tests -v
python tests/run_legacy_direct.py
python -m scripts.check_query_parser
python -m skintellect.database
node --check src/skintellect/web/static/js/research.js
```

The execution sandbox blocks the loopback socket used by Windows asyncio, so its HTTP
test must be skipped here with `$env:SKINTELLECT_SKIP_HTTP='1'`. That produces an explicit
skip, not a passing HTTP result. Direct route/schema checks and existing service assertions
run without sockets. On an unrestricted local session, unset that variable and run the
suite, then run `python -m tests.smoke_api` against the launched application.

The 20 parser cases are developer-written smoke checks, not a human-reviewed held-out
evaluation. No ranking-quality, model-accuracy, or clinical-performance improvement is claimed.

## Remaining roadmap

Validation recorded for this implementation: 23 regression tests passed, one live HTTP
test explicitly skipped in the sandbox, 20/20 parser smoke cases passed, and all 11
existing API assertion groups passed in direct route mode. JavaScript syntax and Python
compilation checks passed. The backup archive checksum and archive integrity passed;
both databases passed SQLite integrity checks. Original products, ingredients, links,
reviews, crawl queue and personas compare unchanged against the backup. See
`reports/history/baseline_preservation.json`, `reports/history/foundation_audit.json` and
`reports/history/parser_smoke_results.json`.

A live browser/server preview has not been verified because the sandbox blocks loopback
sockets. Temporary fixture directories from interrupted HTTP checks remain in the project;
their cleanup was rejected by the environment's approval policy.

This is the foundation and first integrated research baseline. It does not complete the
entire staged roadmap. Remaining releases include human annotations and held-out evaluation,
model review-aspect extraction, embedding retrieval and measured hybrid fusion, relevance
judgments for ranking, source-document retrieval with cited passages, stateful model-driven
tool orchestration and bounded recovery, and broader verified catalog collection.

Knowledge-graph experiments, MCP, OCR, reformulation history, personalized feedback and
expanded routine planning remain optional follow-on work. Existing experimental agents
are preserved; their simulated outputs are not scientific evidence.
