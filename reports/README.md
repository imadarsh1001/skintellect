# Reports and validation artifacts

These files are saved outputs, not application source. A report describes its
recorded run; a file under `latest/` is not automatically fresh or human-validated.
Check its timestamp, source/model fingerprint and stated limitations.

| Location | Contents |
| --- | --- |
| `latest/` | Most recent saved evaluation, preparation and verification outputs |
| `history/` | Earlier experiments and release comparisons |
| `previews/` | Saved interface screenshots; not proof of the current rendered layout |
| `exports/` | Generated recommendation Markdown and standalone HTML reports |
| `cleanup-plan.json`, `cleanup-result.json` | Historical cleanup inventory and relocation records |

## Source-layout and cleanup verification

- [Source reorganization](latest/src-reorganization-validation.json): saved regression,
  packaging, HTTP and database-preservation results from the source move.
- [Installed wheel](latest/src-wheel-validation.json): standalone package imports,
  served assets, HTTP checks and original database hash comparison.
- [Generated-file cleanup](latest/generated-cleanup-validation.json): removed build/test
  artifacts and the limited post-cleanup application checks.
- [Workspace audit](latest/workspace-audit.json): source imports, JavaScript syntax,
  page resources, documentation links and read-only database integrity.
- [UI semantics](latest/ui-semantics.json): rendering-helper semantics and color contrast;
  this does not test browser layout.

## Research results

- [Prepared-cohort evaluation](latest/research_release_evaluation.json)
- [Prepared cohort run](latest/prepared_cohort_run.json)
- [Embedding migration](latest/embedding2-migration.json)
- [Review-aspect migration](latest/dynamic-absa-migration.json)
- [Decision endpoint smoke](latest/dynamic-decision-smoke.json)

Generated labels and model/rule agreement do not establish extraction accuracy,
clinical product performance or general retrieval-quality improvements.

Regenerate engineering checks with [the developer tools](../scripts/README.md).
Use `python -m skintellect.reporting --format markdown` or `--format html` for report
exports. Keep results needed for comparison; archive older material deliberately.
The optional browser smoke fixture reads `latest/prepared_assistant_demo.json`.
