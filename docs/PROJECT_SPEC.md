# Formulation Studio: project specification

Status: MVP+ scope confirmed with the project owner; local specification, not
published to an issue tracker. Implementation and data imports remain pending.

This specification synthesizes the existing application, the buyer-facing MVP+
scope agreed through the scope interview, and essential verification work.
Existing capabilities are distinguished from planned work and advanced-study tracks.
Updating this document does not execute provider calls, data collection, imports
or backup deletion.

## Problem Statement

An analytical buyer needs to browse moisturizers, compare recorded formulas,
prices and review experiences, and understand ingredient science without domain
expertise. The interface must make a useful first explanation easy to read while
allowing deeper inspection of evidence, limitations and unfamiliar terms.
Incomplete data, heuristic scores, review anecdotes and generated summaries must
remain distinguishable from scientific evidence about ingredients or products.

The project owner also needs a useful interview portfolio demonstrating
LangGraph, agentic tool coordination, RAG, review NLP, repeatable data pipelines
and evaluation. Those capabilities must serve the buyer workflow and have
observable outcomes and failure cases.

The maintainer also needs a project whose runtime modules, regression tests,
developer tools, generated outputs and restore points have clear ownership.
The recent reorganization established those boundaries, but several verification
and ingestion gaps remain. Newly crawled products can lack quality metadata and
fail catalog response validation. The browser smoke runner depends on the live
catalog and a saved report. Shared test setup is coupled to another test class,
and several developer command names obscure their purpose.

## Solution

Deliver a local, single-user MVP+ with two primary buyer journeys:

- **Explore:** browse moisturizer listings, apply filters, edit a skin persona,
  inspect explained preference matches, and select products for comparison.
- **Research and learn:** compare selected products or ask a question, inspect
  source-backed review and ingredient explanations, and expand simple language
  into deeper scientific detail when desired. Explore an ingredient relationship
  graph connecting recorded products, ingredients and attributed references.

Advanced study has four separate experimental tracks: a LangGraph specialist
agent board, label-image transcription, Ingredient CSI and Standalone Formula
Lab. These experiments have their own
evaluation and do not block the buyer-facing MVP+.

The existing prepared-study, progress and experimental interfaces are not
additional release requirements. Their implemented capabilities may remain.

Expose what the catalog actually supports: recorded ingredients, explicit
constraint outcomes, attributed review excerpts, explainable heuristic scores,
and preparation readiness. Missing information must remain visible. Optional
model operations must use bounded budgets and report their mode and usage.

Use the existing Nykaa dataset through the configured NYKAA_DATA_DIR as a
read-only input to deliberate import batches. Preserve store attribution,
product/formulation identity, source prices and collection dates. Keep store
ratings, persona preference matches and evidence coverage visibly separate.

Implement one LangGraph research workflow coordinating product lookup,
ingredient evidence, review analysis and comparison. Deterministic domain
operations retain responsibility for eligibility and preference scoring.
RAG and review NLP support explanations; a manually reviewed evaluation set
demonstrates usefulness, evidence support and limitations.

The MVP foundation is browsing, personas, comparison, reliable ingestion and
transparent ingredient matching. The MVP+ release adds educational explanations,
the LangGraph research workflow, RAG/review NLP and evaluated interview evidence.
Keep the current module ownership and essential regression protection. Further
folder reorganization and cosmetic command renames are optional housekeeping.

## User Stories

These stories define the target MVP+; listing a story does not claim it is
implemented. Existing functionality is reused where it meets the contract.

1. As an analytical buyer, I want to browse moisturizer listings, so that I can explore products without first composing a research question.
2. As an analytical buyer, I want search and useful product filters, so that I can narrow the listings to my preferences.
3. As an analytical buyer, I want prices, sizes, store ratings and review counts visible, so that I can assess an offer in context.
4. As an analytical buyer, I want the source and last-updated date of an offer, so that I can judge whether its price and availability are current.
5. As an analytical buyer, I want demonstration seeds excluded by default, so that examples are distinguishable from collected listings.
6. As an analytical buyer, I want an editable skin persona covering skin type, concerns, sensitivities and ingredient preferences, so that matching reflects my stated needs.
7. As an analytical buyer, I want contributing reasons beside my persona match, so that I understand why a product is suggested.
8. As an analytical buyer, I want store ratings, persona matches and evidence coverage shown separately, so that I do not confuse popularity, preference and evidence.
9. As an analytical buyer, I want a partial or unknown match when important ingredient data is missing, so that a precise-looking score does not conceal uncertainty.
10. As an analytical buyer, I want strict ingredient requirements to produce pass, fail or unknown, so that missing data does not establish ingredient absence.
11. As an analytical buyer, I want to inspect a recorded formula and its completeness status, so that I know what information supports an explanation.
12. As an analytical buyer, I want to select products for comparison, so that I can understand differences without switching repeatedly between detail views.
13. As an analytical buyer, I want comparison to distinguish formulation differences from offer-size differences, so that reviews and explanations refer to the intended product.
14. As an analytical buyer, I want ingredient explanations in familiar language, so that I can understand their relevance without scientific training.
15. As an analytical buyer, I want deeper detail and definitions on demand, so that I can learn without overwhelming the initial view.
16. As an analytical buyer, I want scientific statements linked to supporting sources, so that I can inspect their basis.
17. As an analytical buyer, I want ingredient-level evidence distinguished from evidence about a finished product, so that I do not assume the same result applies to every formulation.
18. As an analytical buyer, I want review anecdotes distinguished from scientific evidence and marketing descriptions, so that I can weigh each appropriately.
19. As an analytical buyer, I want attributed review summaries with exact supporting excerpts, so that I can inspect what reviewers actually reported.
20. As an analytical buyer, I want duplicate review handling to be consistent, so that repeated text does not inflate experience summaries.
21. As an analytical buyer, I want a research question to use relevant product and evidence tools, so that I receive an explanation grounded in available information.
22. As an analytical buyer, I want unresolved requirements and insufficient evidence surfaced, so that unsupported assumptions do not become recommendations.
23. As an analytical buyer, I want bounded ingredient-overlap alternatives when useful, so that I can explore nearby candidates without assuming equal performance.
24. As an analytical buyer, I want basic browsing and ingredient matching available without model calls, so that provider availability does not prevent catalog exploration.
25. As an operator, I want deliberate import batches from the configured Nykaa dataset, so that collection and application ingestion can be inspected separately.
26. As an operator, I want imports to preserve source identities, dates and raw-source references, so that catalog transformations remain traceable.
27. As an operator, I want uncertain cross-source product matches kept separate, so that one formula is not explained using another product's reviews.
28. As an operator, I want repeat imports to avoid duplicate products, offers and reviews, so that refreshing data does not inflate the catalog.
29. As an operator, I want all ingested products to have quality metadata, so that browsing remains valid immediately after an import.
30. As an operator, I want bounded review and index preparation with basic status and usage, so that I can control resource consumption.
31. As an operator, I want stale or malformed prepared reviews and passage vectors excluded from usable coverage, so that readiness agrees with retrieval.
32. As an operator, I want invalid saved work eligible for repair, so that a failed preparation step does not require discarding valid work.
33. As an AI engineering learner, I want one LangGraph workflow with explicit state and meaningful tool-selection decisions, so that I can explain agentic orchestration through a useful use case.
34. As an AI engineering learner, I want RAG to retrieve attributable ingredient and review evidence, so that generated explanations can be evaluated for support.
35. As an AI engineering learner, I want a repeatable review-NLP pipeline with extraction identity and source spans, so that I can compare methods and inspect errors.
36. As an AI engineering learner, I want inspectable workflow traces and bounded retries, so that I can demonstrate decisions, failure handling and provider usage.
37. As an interview presenter, I want a reproducible local moisturizer demonstration, so that I can show the complete buyer experience and explain its engineering tradeoffs.
38. As an interview presenter, I want a small manually reviewed evaluation set, so that quality claims are supported by explicit examples and outcomes.
39. As a maintainer, I want tests through public domain operations with disposable catalogs, so that behavior is verified without coupling tests to implementation details.
40. As a maintainer, I want focused API and browser checks, so that valid domain results are also correctly exposed and usable.
41. As a maintainer, I want browser fixtures isolated from working data, so that verification does not modify the research catalog.
42. As a maintainer, I want one active test suite with shared fixture setup and discoverable parser cases, so that the verification entry point is clear.
43. As an analytical buyer, I want to explore a product's ingredient relationships, so that I can discover shared recorded ingredients, related products and supporting references visually.
44. As an analytical buyer, I want graph connections to explain their relationship and expose supporting evidence, so that I do not mistake ingredient overlap for proven efficacy or causation.

The number of stories describes the contract; it is not a count of new features
or separate implementation projects.

## Implementation Decisions

### Existing foundations to preserve

- One installable application package owns runtime behavior and bundled web assets. Feature ownership remains catalog, formulation, research, ingestion, agents and interface adapters.
- The selected catalog owns dataset selection, common recorded-formula interpretation and display-cache lifetime. Explicit catalog selection takes precedence over the default.
- Ingredient facts own normalization and name matching. Formula, catalog and recommendation classification policies retain their documented differences. Final scoring policies remain separate.
- The review corpus owns cleaning, source identity, per-product duplicate handling and prepared-review acceptance. Preparation counts use unique nonempty sources; retrieval preserves raw-review identities.
- Prepared reviews require matching source hashes, extraction/model identity and valid exact spans. A valid empty observation list counts as prepared.
- The passage index owns vector acceptance and atomic persistence. Acceptance requires matching source identity, model, dimensions, finite numeric values and normalization. Invalid rows remain pending for repair.
- SQLite remains the persistence mechanism. Existing HTTP, CLI and MCP adapters reuse domain behavior without introducing a generic storage hierarchy.
- The browser interface remains buildless. Installed resources resolve from the package; mutable catalogs, credentials, generated reports and restore points remain external.
- Preparation jobs remain in one API process with one worker. Existing provider transport owns validation, retries, budgets, cache identity and telemetry.

### Planned buyer and AI capabilities

- Keep Explore and Research as the two primary navigation areas. Browsing and persona editing must be usable without entering a chat. Comparison connects the two areas.
- Lead with plain-language ingredient explanations and reveal deeper science and source excerpts on demand. Explain unfamiliar terminology in context.
- Include an ingredient relationship graph in the main buyer experience, accessible from product detail and comparison. Reuse the existing recorded-facts projection and its stable evidence identities. Show product, ingredient and reference nodes with labeled, inspectable relationships; represent unavailable references honestly. Ingredient overlap is not evidence of equal performance or causation.
- Keep the relationship graph an optional exploration view so buyers can complete ordinary browsing and comparison without navigating it. Provide a readable list of the same relationships for keyboard and nonvisual access. This buyer-facing graph is distinct from LangGraph workflow orchestration.
- Treat store descriptions, store-attributed reviews, ingredient science and finished-product evidence as distinct source types. Store attribution does not independently establish reviewer identity, authenticity or purchase verification.
- Retain deterministic ingredient eligibility and persona preference scoring. Display partial or unknown matching where required inputs are missing; do not present a complete match percentage for incomplete evidence. Keep store ratings and evidence coverage separate from preference matches.
- Read Nykaa source data from the configured NYKAA_DATA_DIR without rewriting its files. An import is a separate explicit operation targeting the selected application catalog.
- Normalize source products, formulation identity, offers, reviews and import provenance through additive persistence changes where needed. Preserve source product and review identifiers, sizes, prices, availability and supporting source references when supplied.
- Merge cross-source products only when their identity and formulation can be established. Keep uncertain matches separate and keep store offers separately attributable. Do not infer one variant's formula or review applicability from another variant's shared name.
- Make repeated imports idempotent. Review identifiers may recur across product records; preserve their source identity and distinguish deduplication from product-review associations before computing counts.
- Record import time separately from source collection time. Do not substitute import time for a missing collection date or invent a currency not established by source metadata. Unknown freshness must remain visible.
- Add LangGraph as planned workflow orchestration; it is not currently present in the declared dependencies or runtime imports. Reuse current domain operations as tools rather than rebuilding ingredient matching, scoring, review acceptance or index persistence inside the graph.
- Give the graph explicit question, selected-product, tool-result, evidence and completion/error state. Use meaningful tool-selection branches, bounded execution and inspectable traces. Retain existing provider transport for model calls and usage reporting.
- Build RAG on attributable product, review and a small curated ingredient-science source collection. Existing configured reference labels alone do not establish retrieved scientific evidence. Keep lexical fallback, and report actual retrieval/generation modes.
- Reuse the review-NLP pipeline with product-scoped deduplication, exact spans and model/extraction identity. Prepare a bounded demonstration cohort first; possession of a large raw dataset does not require model-processing every review for the release.
- Support reproducible local demonstration and a small manually reviewed evaluation set. Present supported results, failure cases, latency and usage honestly; no particular accuracy or latency target has yet been agreed.
- Keep specialist-board, label-transcription, Ingredient CSI and Standalone Formula Lab study in a separate experimental area, with isolated fixtures and explicit opt-in execution. Experimental implementations may reuse public domain operations and provider transport; the main application must not depend on the experimental area. Existing live experimental endpoints remain intact until a deliberate migration is implemented and verified. LangGraph is required for the specialist board; it is not an additional requirement for the other studies.

### Remaining implementation work

- Make product ingestion and quality metadata consistent. A newly committed product must have explicit seed classification and an honest formula status. Preserve human verification only when its recorded-formula identity and provenance remain valid.
- Normalize the catalog's seed indicator to its declared boolean response contract. Apply a consistent policy for legacy records without metadata; do not silently classify an unknown record differently across catalog and research views.
- Prefer additive metadata repair over changes to the base product schema. Do not infer formula completeness during repair.
- Keep regressions in one project test suite. Extract a shared synthetic catalog fixture helper without inheriting another suite's test methods.
- Convert the authored parser smoke cases into discoverable regressions. Preserve their coverage and describe them as authored examples rather than an accuracy benchmark.
- Initialize browser-test fixtures explicitly when the check runs. Replace live-catalog lookups, fixed real-product identities and saved-report dependencies with disposable synthetic data and controlled responses.
- Add a catalog response-contract check to the standard automated verification command, including a product newly saved through ingestion.
- Keep developer commands separate from application runtime and regression assertions. Clearer names for the project check runner and evaluators are optional housekeeping rather than MVP+ release requirements.
- Update command references, CI invocation and evaluator imports together when names change. Retain the package marker required by module invocation and evaluator imports.
- Report omitted optional checks explicitly. A skipped browser or JavaScript check must not be represented as executed verification.
- Do not remove vendor test directories as part of project test consolidation. Archived test copies remain part of their restore points. Unused manual image fixtures and quarantined bytecode are separate optional cleanup candidates.

## Testing Decisions

- Confirmed primary seam: exercise existing public domain operations against a disposable synthetic SQLite catalog. The project owner selected this boundary over HTTP as the primary seam. Assert returned domain outcomes and persisted state without requiring an HTTP server or adding new test-only interfaces.
- A good test describes observable behavior and fails for a meaningful regression. Avoid assertions about helper call counts, private cache layout or source-file arrangement unless packaging itself is the contract.
- Cover ingestion through domain operations: a newly saved product has quality metadata, seed classification has the declared type, formula status is honest and catalog and research selection treat the product consistently.
- Exercise catalog selection, ingredient constraints, routine consistency, review attribution, preparation readiness and invalid-index repair through existing public domain operations.
- Include malformed prepared-review and vector payloads at their existing domain boundaries. Use the existing injected provider doubles; make no real provider calls.
- Keep focused HTTP adapter checks as a secondary layer for request validation, response serialization and error translation. Include a newly ingested product's catalog response; avoid repeating the full domain behavior matrix through HTTP.
- Reuse prior art from disposable-catalog research tests, asynchronous HTTP regressions, preparation-job tests and architecture behavior regressions. Reuse the existing standalone catalog smoke assertions where their data assumptions can be made synthetic.
- Keep browser interaction checks as a separate necessary surface check. They validate page behavior and source rendering against controlled fixtures; HTTP and JavaScript semantic checks alone do not establish rendering quality.
- Check the browser harness itself for isolation: it must run without the working catalog or saved evaluation reports and must leave the working catalog unchanged.
- Run parser cases in the normal discovery path. Keep evaluations separate: method agreement, generated relevance labels and small latency samples do not establish independent accuracy or production performance.
- Retain wheel/resource checks from an unrelated working directory after packaging or ownership changes. Update the CI command together with developer command renames.
- Add import contract cases for repeated rows, shared source review IDs, uncertain product/formulation matches, missing timestamps, and source-price provenance. Use representative synthetic shapes rather than copying reviewer personal information into fixtures.
- Evaluate the LangGraph workflow through observable tool selection, supported outputs, stop conditions and error recovery. Do not require exact generated wording or an exact internal graph structure.
- Manually review evaluation examples for product identity, ingredient constraint outcomes, source support, understandable language and appropriate uncertainty. Include insufficient evidence and provider-unavailable cases. Model agreement alone is insufficient.
- Test ingredient relationship projection through its existing domain boundary using recorded overlap, unrelated products, missing products and absent references. Add focused browser checks for graph selection, relationship explanations and the equivalent accessible list. Test the four advanced-study experiments independently of main release acceptance.

### MVP+ acceptance criteria

1. A buyer can browse and filter moisturizers, inspect product details, edit a persona and select products for comparison without using chat.
2. Listings expose attributable offer information when available, including size, price, rating, review count and honest freshness. Missing or ambiguous fields remain visible.
3. Persona match explanations show contributing preferences and limitations. Store ratings, preference match and evidence coverage are distinguishable.
4. A missing recorded formula produces partial or unknown matching. A strict exclusion remains unknown when absence cannot be established.
5. Comparison distinguishes product/formulation identity from offer size and source, and does not silently mix uncertain variants.
6. A research question can invoke the relevant tools through one LangGraph workflow and produce a plain-language response with inspectable evidence and deeper detail on demand.
7. Ingredient explanations distinguish ingredient-level science, finished-product evidence, marketing descriptions and review anecdotes. Unsupported conclusions are identified as unknown.
8. Review summaries retain exact supporting excerpts and product/source attribution. Preparation and displayed coverage use consistent duplicate rules.
9. Nykaa batch imports preserve source inputs, can be repeated without inflating identities, and leave newly ingested products immediately valid for catalog responses.
10. Provider-backed work is bounded and inspectable. Basic catalog exploration remains available when model operations are unavailable.
11. The interview demonstration uses a documented, bounded moisturizer cohort and a manually reviewed evaluation set covering the agreed quality dimensions. Results and known failures are reproducible and reported without unsupported accuracy claims.
12. Domain tests, focused API serialization checks and isolated browser checks cover the buyer journey. Verification does not modify working source data or the live catalog, and skipped checks are reported explicitly.
13. From product detail or comparison, a buyer can explore recorded ingredient relationships, inspect the evidence behind each supported edge, and use an equivalent readable list. Missing data and unsupported relationships do not become invented graph edges.

## Out of Scope

- Rebuilding the implemented application or repeating the completed source reorganization.
- Continuous scraping, automatic refresh scheduling and model-processing the full raw dataset as a prerequisite to release.
- New model providers and large-scale annotation campaigns. A small curated ingredient-science source collection and manually reviewed evaluation set are in scope. Paid runs require a separately chosen bounded execution plan; this specification does not execute them.
- Clinical safety claims, efficacy guarantees, concentration or pH inference, and automatic certification of complete formulas.
- Changes to classification policies or score formulas merely to unify their historical outputs. Honest partial/unknown presentation is in scope.
- Automatic deletion of catalogs, raw snapshots, dependencies, credentials or restore-point archives.
- Replacing the frontend framework or introducing a frontend build pipeline.
- Further folder reorganization and cosmetic command renames as release-blocking work.

### Future phases

Additional categories, MCP, routine analysis, advanced model-upgrade tooling, extra operational dashboards and public multi-user infrastructure are future scope, to be specified only when implementation is requested; see the separate [feature retirement study](FEATURE_RETIREMENT_STUDY.md) for reducing existing code outside this phase.

## Further Notes

- Current-state evidence comes from the project glossary, architecture and source-layout guides, directory and command review, and the subsequent scope interview. MVP+ scope was confirmed by the project owner.
- The ingredient relationship graph is included in main MVP+ scope. The separate [advanced-study experiments](../experiments/README.md) define the LangGraph specialist board, label-image transcription, Ingredient CSI and Standalone Formula Lab tracks, their current baselines and planned evaluation.
- The latest saved architecture validation records 125 passing regressions, 31 JavaScript semantic assertions, 20 parser cases and packaged HTTP checks. These are historical results, not a new test run for this specification. Browser layout was not established by that validation.
- The ingestion metadata/response issue was reproduced during the directory review using a temporary synthetic database. The working catalog was unchanged.
- The application's available catalog remains incomplete. A prepared study demonstrates a small convenience sample; neither its readiness nor stored review observations establish representative market coverage. Raw Nykaa data availability does not mean it has been imported, reconciled, prepared or evaluated in this application.
- Read-only inspection of NYKAA_DATA_DIR on November 4, 2026 confirmed detailed moisturizer product and review JSONL files. The product file contains 2,230 rows and 2,204 distinct source product IDs, including 26 repeated rows. The following product coverage uses the last file row per ID; absent acquisition timestamps mean this is not a verified latest-version policy.
- Of those source product IDs, 1,902 have nonempty ingredient text, 2,203 have descriptions, and 1,997 have ratings. Ingredient-list completeness and formulation identity are not thereby verified. All have numeric MRP and offer-price fields, but currency is not explicit.
- The main review file covers 1,250 product IDs and contains 520,217 product-review associations with 349,297 distinct source review IDs. Review IDs recur across product records. Reviews embedded in product rows raise the union to 349,301 distinct IDs. These counts do not establish independent reviewers or authentic purchases.
- Review arrays and claimed/collected metadata disagree for many records. Import must reconcile actual content and source identity before displaying coverage or preparing summaries. Fields such as the store's buyer flag remain attributed source claims.
- Source variant arrays exist for 333 product records, with 643 variant objects, but no explicit per-variant ingredient field was observed. Source collection timestamps and explicit currency were not found; filesystem modification times are not a substitute. Price freshness, currency and variant-formula applicability require validation.
- Existing reviewer-analysis outputs contain heuristic flags; they are not validated authenticity labels and must not be presented as such.
- No applicable architecture decision record was found during the repository scan. The existing glossary and documented module ownership govern this draft.
- The project owner confirmed domain operations as the primary testing boundary, with focused HTTP adapter checks and separate browser interaction checks.
- Publication is pending issue-tracker setup. The requested triage label is `ready-for-agent`; no tracker destination has been identified.
- Run `/setup-matt-pocock-skills` to provide the issue tracker and triage configuration required by the invoked skill. This draft has not been published or labeled.
