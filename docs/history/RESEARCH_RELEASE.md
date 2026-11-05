> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Prepared research release (3.0.0)

Open http://127.0.0.1:8000/study after starting `run-research.cmd`. The study page is
the shortest route through a complete demonstration. It links to scoped research,
product evidence, ingredient relationships, automated evaluation, references, and
experimental label transcription. `/progress` still shows full-catalog preparation.

## Delivered scope

| Capability | Behavior |
| --- | --- |
| Prepared study | Three real products; all 28 current reviews processed; all 31 product/review passages indexed |
| Conversational research | Explicit prepared-group scope or full catalog; deterministic hard constraints; exact evidence excerpts |
| Latency improvements | Reuse validated query embeddings; skip model planning for explicit review/alternative requests; per-stage timing |
| Reference library | Three attributed notes from FDA, AAD and a primary-study abstract; URLs, check dates, source types and limitations |
| Evidence graph | Product–ingredient–product paths and reference-topic edges, computed from current records |
| MCP | Five bounded read tools over local stdio; no SQL, shell, arbitrary file paths or write tools |
| Label images | Gemini transcription of visible PNG/JPEG ingredient declarations; optional catalog comparison; no formula mutation |
| Evaluation | Synthetic rule fixtures, real-review method agreement, generated-label retrieval comparisons, source-span checks, first/repeat latency |

The study group contains Thank You Farmer Phyto Relieful Cica Cream (10256),
Dr. Sheth's Oil-Free Moisturizer (21620), and iUNIK Tea Tree Relief Serum (37102).
Selection is a convenience sample with substantial recorded ingredients and a bounded
number of reviews; it is not a representative product benchmark. Coverage is recalculated
from current hashes and model/version identity. Changed or corrupt vectors cannot count
as ready. Evaluation reports are marked stale after relevant source/model changes.

## Reproduce preparation and evaluation

On this workstation set `$env:PYTHONPATH = "$PWD\.runtime"`, then run:

```powershell
python -m skintellect.research.study status
python -m skintellect.research.study prepare --max-calls 60 --max-seconds 1200 --output reports/latest/prepared_cohort_run.json
python -m scripts.evaluate_release --output reports/latest/research_release_evaluation.json
python -m unittest discover -s tests -q
```

Preparation saves each batch, skips unchanged completed work, and stops at its explicit
provider-attempt/time budget. It does not automatically process the entire catalog.
The evaluation permits up to 30 retrieval attempts plus two assistant runs bounded at
six attempts/120 seconds each. The first latency measurement may already have cached
steps; the report does not label it an entirely cold request.

Reference notes are imported at application startup from `data/reference_sources.json`.
They are concise attributed notes, not a full-paper scientific corpus. They are displayed
separately from catalog/review evidence. The PubMed abstract entry discloses full-text
access limitations and commercial affiliations. Published ingredient research does not
validate any product in this catalog.

## MCP connection

Use an MCP client supporting stdio and launch the included `run-mcp.cmd`, or launch
Python with `-m skintellect.mcp` from the project directory. The local workstation
runtime must be on PYTHONPATH. Tool discovery lists:

- `search_products`: typed ingredient constraints with explicit unknowns.
- `get_evidence`: current catalog, review or reference attribution.
- `get_review_insights`: cached model observations with rule fallback.
- `get_connections`: evidence-attributed ingredient relationship paths.
- `retrieve_passages`: local lexical retrieval, without paid provider calls.

The adapter supports MCP initialization, ping, tool discovery and calls over UTF-8
newline-delimited JSON-RPC (protocol 2025-11-25). It opens no network listener and
does not claim support for every optional MCP feature. No external client was connected
automatically. Protocol references:

- https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- https://modelcontextprotocol.io/specification/2025-11-25/server/tools

## What the automated checks establish

Real-review agreement compares two imperfect methods; it is not accuracy against a gold
standard. Generated retrieval labels use catalog identity and literal term matches, which
favor lexical matching. The report preserves poor results and disagreements. Small-sample
MRR, recall and nDCG do not establish gains on open-ended research questions. Synthetic
labels test transcription plumbing, not photo OCR accuracy. Clinical performance, individual
tolerance and formula concentrations are not established by these checks.

Formula verification remains conservative. The image reader's `appears_complete` is only a
model impression. It cannot set `verified_complete`, overwrite ingredients or certify safety.
No fabricated human review or clinical approval is recorded. Manual labels can be added later
without blocking use of this engineering prototype.

The local web server is intended for one user/worker. Authentication and a dedicated queue
worker are required before public hosting. Files in `.env` are never returned through the UI.

## Validation artifacts

82 regression tests pass, including cache, scope, provenance, graph, MCP, OCR-contract,
cohort-freshness and HTTP-route checks. Legacy direct API checks pass. The live synthetic
label smoke returned the expected four ingredient names. Current warm-cache latency is
recorded alongside earlier slow/provider-failure measurements; no uncached SLA is claimed.

- `reports/latest/prepared_cohort_run.json`: approved live preparation and provider usage.
- `reports/latest/research_release_evaluation.json`: retrieval, review agreement and latency.
- `reports/history/research_release_initial_evaluation.json`: preserved initial timings and failures.
- `reports/latest/mcp_smoke.json`: real local stdio discovery and read-tool calls.
- `reports/latest/live_label_smoke.json`: live synthetic image transcription check.
- `reports/latest/research_release_validation.json`: regression, provenance and integrity checks.

Source and a consistent database backup were saved under
`backups/before_research_release_20261023T044429Z/` before changes.
