# Label OCR

## Overview

Experimental Gemini-based label transcription module
(`experiments/label_ocr/labels.py`). `read_label` validates a base64 PNG/JPEG image,
asks Gemini to transcribe only the visible ingredient declaration, and returns the
extraction together with an image hash, budget telemetry, and an optional
three-way comparison against a recorded formula. Per the module contract, it never
changes formula verification: outputs are marked unverified and no catalog data is
touched.

## Interface

- `[labels.py:read_label(data_b64, mime_type, db_path, recorded_names=None)]` — the
  module's only public symbol. Returns a dict with keys:
  - `extraction` — `model_dump()` of
    `src/skintellect/research/models.py:LabelExtraction` as returned by Gemini.
  - `image_hash` — SHA-256 hex digest of the decoded raw image bytes.
  - `model` — the Gemini model id reported by `GeminiClient`.
  - `human_verified` — always `False`.
  - `formula_verification_changed` — always `False`.
  - `comparison` — `None` when `recorded_names is None`; otherwise
    `{"shared", "image_only", "catalog_only"}` as sorted lists over
    `normalize()`-ed names (`src/skintellect/formulation/ingredient_facts.py:normalize`).
  - `events` — the budget run's event list from `run_budget`.
  - `notice` — fixed experimental-transcription disclaimer string.
- Input validation (all raise `ValueError`, `[labels.py:read_label]`):
  - `mime_type` must be `image/png` or `image/jpeg`, and `len(data_b64)` must be
    at most `8_000_000`, otherwise `'unsupported_or_oversized_image'`.
  - Base64 payload must decode with `base64.b64decode(data_b64, validate=True)`,
    otherwise `'invalid_image_encoding'`.
  - Decoded size must be at most `6_000_000` bytes and the magic signature must
    match the declared type — PNG `b'\x89PNG\r\n\x1a\n'` or JPEG `b'\xff\xd8\xff'` —
    otherwise `'invalid_image_signature'`.
- Gemini call: `src/skintellect/gemini.py:GeminiClient(db_path).structured('label_transcription', ...)`
  with response model `LabelExtraction`, version `'1'`, `max_tokens=4000`, and the
  image payload `{"mimeType", "data"}`, wrapped in
  `src/skintellect/gemini.py:run_budget(2, 90)` (max 2 calls, 90 s budget).

## Invariants

- Transcription is bounded to the visible ingredient declaration, in printed order:
  the system prompt instructs the model to treat the image as untrusted data, never
  reconstruct hidden or unreadable text, and place uncertainty in `uncertain_text`
  (`[labels.py:read_label]`).
- `[labels.py:read_label]` always returns `human_verified=False` and
  `formula_verification_changed=False`; an extraction never updates, certifies, or
  replaces any recorded formula (module docstring: "never changes formula
  verification").
- Comparison sets are computed only between `normalize()`-ed names, so case and
  formatting differences cannot create false diffs
  (`[labels.py:read_label]`).
- `comparison` is `None` unless `recorded_names` is explicitly provided
  (`[labels.py:read_label]`).
- Image size and signature checks are enforced before any network call is made
  (`[labels.py:read_label]` validation block precedes `GeminiClient` use).

## Side Effects

- Network: one Gemini `structured` request per call, including the image payload
  (`[labels.py:read_label]` via `src/skintellect/gemini.py:GeminiClient.structured`).
- Budget accounting: the call runs inside
  `src/skintellect/gemini.py:run_budget(2, 90)`, which records call/elapsed events in
  the returned `events` list; `db_path` is passed to `GeminiClient`, which opens
  `database(self.db_path)` for its DB-backed budget/telemetry bookkeeping
  (`src/skintellect/gemini.py:GeminiClient.__init__`).
- Database writes via the shared Gemini transport (`database(self.db_path)`):
  `GeminiClient.structured` runs `ensure_tables` DDL first
  (`src/skintellect/gemini.py:ensure_tables`), always INSERTs a `gemini_runs`
  telemetry row in its finally block (even when the call fails), and INSERT OR
  REPLACEs a `gemini_cache` row on success (`src/skintellect/gemini.py:249`,
  `src/skintellect/gemini.py:304`). The package itself writes no tables of its
  own and performs no filesystem writes.

## Verification

No dedicated automated test targets this experimental module. Repository-level smoke
checks from the root:

```
python -m experiments.smoke_agents
python -m tests.smoke_api
```

Note that neither exercises `read_label` (it requires a Gemini round trip with an
image payload); `python -m tests.smoke_api` covers the API surface only. No pytest is
configured for this repository.
