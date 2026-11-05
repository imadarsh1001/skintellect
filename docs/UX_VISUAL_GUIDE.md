# Visual evidence guide

The study, question and progress screens use a shared navy, teal and blue palette.
Color helps identify the kind of information; every state also has a written label.

| Color | Meaning |
| --- | --- |
| Teal | Prepared evidence, completed tasks, or explicitly positive review sentiment |
| Blue | Source information, extracted themes and active processing |
| Amber | Unknowns, incomplete evidence, limits or paused work |
| Rose | Failed tasks or explicitly negative review sentiment |
| Purple | Mixed experiences and ingredient-comparison sections |
| Slate | Neutral metadata and inactive states |

These colors do not score product safety, effectiveness or individual suitability.
Positive and negative review sentiment are observations in collected text.

## A faster path into the data

The study starts with a live snapshot of prepared products, analyzed reviews and indexed
passages. Product cards show preparation counts and the formula-completeness limitation.
Exploration shortcuts follow the product cards so they do not delay reaching the products.
The curiosity shortcuts open the relevant product, reference or label tab and move focus
there. They do not send an image or trigger a paid research request.

Review panels highlight the most-mentioned extracted theme and identify themes containing
opposing or mixed experiences. Counts come from the existing API response. A one-sided
sample is explicitly not treated as consensus. The detailed theme table and source quotes
remain available underneath. Example research questions fill the editor; the main action
starts the query. Comparative ingredient lists have a separate visual treatment.

## Verification

Run `node tests/check_ui_semantics.js` to check summary meaning, literal-text rendering,
and eight text contrast pairs read directly from the shared stylesheet. All eight checked
pairs exceed 4.5:1. This is a targeted check, not a complete accessibility certification.
Results: `reports/latest/ui-semantics.json`.

Saved test counts belong to their recorded validation runs; see the
[validation artifacts](../reports/README.md). The workspace audit checks source
syntax, duplicate HTML IDs, static asset paths, documentation links and read-only
database integrity. Browser-based visual and interaction
checks remain unavailable in this execution environment; `tests/ui_smoke.py` is the
reusable desktop check. No new screenshot is claimed to show this revision.

Refresh `/study`, `/research` or `/progress` after restarting the server if needed. Use
Ctrl+F5 if the browser keeps an older stylesheet. Shared visual styles live in
`src/skintellect/web/static/css/workspace.css`; shared review highlights live in `src/skintellect/web/static/js/workspace.js`.
The original catalog screen retains its existing component styles.

## Product-first refinement

The shorter introduction and compact study totals lead directly to the product cards.
The example research prompt follows the products; the color key is expandable. Cards
now preview their actual most-mentioned review theme, its collected-review denominator,
and up to two other extracted themes. Preparation counts are available in a disclosure.
These previews reuse the saved-review endpoint and a page-local request cache; they do
not call Gemini. Failed preview requests can be retried by opening the product.

Study and research review panels offer theme and experience filters with a matching
observation count, a clear-filters action, pagination and a no-match state. Filters operate
on loaded observations, not products or recommendations. Loading more preserves already
opened source excerpts. Filter semantics are included in `tests/check_ui_semantics.js`.
