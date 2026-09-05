# Phase 18 Change Set 176 — Composition Map Provenance Lock

## Purpose

Golden Editorial v6 is story-first and context-only for the generic season-opening PREVIEW. Its generation contract now carries an explicit composition map:

- visual priority: `story_focal_hierarchy_before_sport_surface`
- focal anchor: `illuminated_tunnel_lower_left`
- copy negative space: `right_center`
- brand quiet zone: `upper_left`

The Colab generation summary and semantic-review path already carry these values, but the semantic continuation previously accepted a handoff without explicitly failing on composition-map drift. That left a stale/tampered-summary gap between generation and the first human Golden review.

## Changes

### `tools/phase18_continue_hybrid_from_first_png.py`

- Added canonical v6 composition-map constants.
- Added `_require_composition_map()` fail-closed validation.
- The canonical handoff must now match all four composition-map fields before Qwen review can start.
- The semantic-review result must independently preserve the same four fields.
- The semantic continuation receipt is upgraded to `pul7sar-first-png-editorial-semantic-continuation-v3`.
- Successful receipts now include the four composition values and `composition_map_locked=true`.
- Publication authority remains closed and the PREVIEW still forbids deterministic pitch reintroduction.

### `tests/test_phase18_first_png_hybrid_semantic_continuation.py`

- Updated fixtures to the current v6 composition map.
- Added regression coverage for each handoff field drifting before semantic review.
- Added regression coverage for each semantic-result field drifting after Qwen review.
- Added assertions that the final receipt preserves the map and remains non-publication-ready.

## Preserved gates

No factual, identity, sentiment/neutrality, zero-cost, semantic-publication, or Golden-quality gate was weakened. In particular:

- `$0-local` remains required.
- Candidate 1 and BF16 remain locked.
- generated branding remains forbidden.
- generated exact sport geometry remains forbidden.
- the generic PREVIEW remains `context_only` and does not receive deterministic pitch replacement.
- semantic layer QA remains required.
- Golden visual quality remains unapproved at this stage.
- publication remains closed.

## Why this reduces the first-PNG gap

The first genuine Candidate 1 must now carry the same story-first visual hierarchy all the way from the generated handoff into the semantic proof that will be shown to the human Golden reviewer. A stale summary cannot silently replace the intended lower-left tunnel anchor with a centered pitch composition while still passing generic semantic checks.

## Deleted files

None.
