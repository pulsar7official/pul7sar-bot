# PUL7SAR Phase 18 — Change Set 102: Golden Review Schema Lock

## Purpose
Close a hard-blocker drift gap in the manual Golden Visual review path before the first new accepted Golden PNG is allowed to advance.

`GoldenVisualBlockers` already contained two hard blockers that the review CLI/template did not expose:

- `generated_platform_brand_or_wordmark`
- `broken_sport_surface_geometry`

Because the legacy review tooling used a hand-maintained blocker tuple, a stale review could omit these fields and the dataclass defaults would silently treat them as `False`. That is incompatible with Phase 18's fail-closed visual-quality policy.

## Changes

### Modified `tools/phase18_review_golden_batch.py`
- Review schema version is now `pul7sar-golden-visual-review-v2`.
- Score fields are derived directly from `GoldenVisualScores` dataclass fields.
- Hard-blocker fields are derived directly from `GoldenVisualBlockers` dataclass fields.
- Stale v1 review files are rejected.
- Generated PUL7SAR branding and broken sport-surface geometry can no longer be omitted by schema drift.

### Modified `tools/phase18_build_golden_review_template.py`
- Uses the same v2 review version as the evaluator.
- Derives score and blocker fields from the current Golden dataclasses instead of duplicating a manual list.
- Newly generated templates include every current hard blocker and keep all blocker defaults `False` only as an unedited template state; a human reviewer must inspect the real PNG before scoring.

### Modified regression tests
- `tests/test_phase18_golden_review_template.py`
  - proves the template schema exactly matches the Golden dataclasses;
  - proves the two previously omitted hard blockers are present;
  - proves scores remain unpopulated.
- `tests/test_phase18_review_golden_batch.py`
  - proves the review schema exactly matches `GoldenVisualBlockers`;
  - proves stale v1 reviews fail closed;
  - proves `generated_platform_brand_or_wordmark=true` rejects an otherwise 9.9-scored candidate;
  - proves `broken_sport_surface_geometry=true` rejects an otherwise 9.9-scored candidate.

## Safety and invariants
Unchanged:
- `main` / `main.py` and production publishing are untouched.
- Fact Lock remains mandatory.
- Identity verification remains fail-closed.
- Sentiment / neutrality rules are unchanged.
- `$0-local`, FLUX.2 Klein 4B, BF16, locked seeds and canvases are unchanged.
- SemanticPublicationGate remains mandatory.
- Golden thresholds remain 8.5 minimum / 9.0+ elite, with hard blockers overriding numeric scores.
- Generated PUL7SAR branding remains forbidden.
- Exact official brand/typography asset integrity remains required before final publication composition.

## Why this materially reduces the remaining gap
The next genuine Candidate 1 must ultimately cross Golden Visual review after semantic/alignment validation. This change prevents that final visual-quality review from silently missing exactly the two blocker classes most relevant to previous rejected proofs: generated PUL7SAR branding and broken football-surface geometry.

No GPU PNG is claimed by this change. It is CPU-safe preparatory hardening for the first genuine Golden Visual review.
