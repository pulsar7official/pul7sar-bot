# PUL7SAR Phase 18 — Change Set 134

## SHA-bound Hybrid Human Review Decision Lock

### Goal

Close the gap between the exact semantically approved Hybrid review bundle and the later Golden 8.5/9.0 quality review without inventing a score, auto-selecting a pitch preset, or granting publication authority.

### Added

- `engine/intelligence/hybrid_human_review_decision.py`
  - consumes only `pul7sar-hybrid-human-review-bundle-v1` Candidate 1 receipts;
  - replays SHA-256 for the review bundle and both review PNGs;
  - requires the upstream BASE_SCENE and HYBRID_SURFACE approvals to remain true;
  - requires `human_visual_review_required=true` and `automatic_selection_performed=false`;
  - produces an explicit checklist covering pitch perspective, photographic integration, surface tint, line readability and premium editorial composition;
  - refuses acceptance unless every required visual-integration check is explicitly `true`;
  - records rejection without escalating to Golden or publication authority;
  - keeps `golden_quality_approved=false` and `publication_ready=false` in every outcome.

- `tools/phase18_build_hybrid_human_review_template.py`
  - Phase 18 branch lock;
  - builds a review template bound to the exact review bundle and PNG hashes;
  - performs no inference, scoring, generation, preset selection or publication action.

- `tools/phase18_record_hybrid_human_review.py`
  - records the explicit human accept/reject decision;
  - fails closed on incomplete checklist data, hash drift, path drift or authority drift;
  - returns non-zero on rejection so an automation pipeline cannot silently treat rejection as approval.

- `tests/test_phase18_hybrid_human_review_decision.py`
  - exact-byte acceptance path;
  - rejection path;
  - acceptance requires every check;
  - incomplete checklist fails closed;
  - Hybrid tampering after bundle creation is rejected;
  - repository path escape is rejected.

### Modified

No existing production or generation runtime file was modified. This change set is additive and consumes the Change Set 133 human-review bundle.

### Deleted

Nothing.

### Gates preserved

No change was made to Fact Lock, identity verification, sentiment/neutrality, `$0-local`, FLUX.2 Klein 4B, BF16, seed/canvas locks, generated-text/brand/score/crest/geometry exclusions, Qwen BASE_SCENE/HYBRID_SURFACE inspection, deterministic football geometry, SemanticPublicationGate, Golden 8.5 minimum / 9.0+ elite thresholds, or exact brand/typography integrity.

### Remaining sequence

`genuine Candidate 1 → provenance → BASE_SCENE ownership QA → deterministic Hybrid → HYBRID_SURFACE QA → SHA-bound review bundle → explicit SHA-bound human decision → Golden 8.5/9.0 review → exact brand/typography → SemanticPublicationGate`

The external blocker remains a compatible NVIDIA CUDA + BF16 host for the first genuine FLUX.2 Klein Candidate 1. No PNG is fabricated by this change set.
