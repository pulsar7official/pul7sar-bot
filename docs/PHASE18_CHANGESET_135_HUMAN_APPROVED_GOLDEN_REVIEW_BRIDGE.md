# PUL7SAR Phase 18 — Change Set 135

## Human-Approved Golden Review Bridge

### Purpose

Change Set 134 made the Hybrid human-review decision tamper-evident, but the existing Golden scorecard path could still be invoked from an older locked-semantic receipt without proving that the new explicit human Hybrid decision had been accepted.

Change Set 135 adds a new fail-closed Golden-quality bridge that requires the full current evidence chain before any 8.5/9.0 scorecard can be created or applied.

### Evidence chain required

The new gate requires all three artifacts together:

1. the Candidate 1 first-PNG Hybrid handoff for request/seed/base provenance;
2. the successful Hybrid semantic continuation proving BASE_SCENE and HYBRID_SURFACE approval plus deterministic-artifact integrity;
3. the accepted SHA-bound human Hybrid review decision from Change Set 134.

The gate recomputes SHA-256 for the base PNG, the semantic-approved Hybrid PNG, the human-review copy, and all three JSON evidence files. The human-review copy must contain the same bytes as the semantic-approved Hybrid artifact.

### Added

- `engine/intelligence/human_approved_golden_visual_review.py`
  - Candidate 1 only;
  - branch/manifest/cost/dtype checks from the Hybrid handoff;
  - BASE_SCENE + HYBRID_SURFACE semantic approval required;
  - deterministic Hybrid artifact-integrity receipt required;
  - explicit `HYBRID_HUMAN_REVIEW_ACCEPTED` decision required;
  - SHA replay across base, Hybrid and review-copy pixels;
  - request ID and seed inherited from provenance evidence, never guessed;
  - Golden scores and hard blockers derived from the existing `GoldenVisualScores` and `GoldenVisualBlockers` contracts;
  - hard blockers override high scores;
  - publication remains closed even when Golden quality passes.

- `tools/phase18_build_human_approved_golden_review.py`
  - creates a human scorecard template only after the full evidence chain passes;
  - defaults to the current GPU-smoke/Colab receipt paths;
  - never invents scores.

- `tools/phase18_apply_human_approved_golden_review.py`
  - applies a completed scorecard to the same SHA-bound evidence chain;
  - returns non-zero when Golden quality is not approved;
  - never grants publication readiness.

- `tests/test_phase18_human_approved_golden_visual_review.py`
  - accepted-chain template path;
  - rejected human decision blocks Golden scoring;
  - clean 8.5+ path can approve Golden but not publication;
  - hard blocker defeats a 9.9 score;
  - Hybrid tampering is rejected;
  - scorecard identity/binding drift is rejected.

### Modified

The two new CLI tools were aligned with the canonical current receipts:

- `output/phase18_colab/latest.json`
- `output/phase18_gpu_smoke/hybrid-semantic-continuation.json`
- `output/phase18_gpu_smoke/hybrid-human-review-decision.json`

No existing production runtime or publication path was modified.

### Deleted

Nothing.

### Gates preserved

Change Set 135 does not weaken or bypass Fact Lock, entity/identity verification, sentiment neutrality, `$0-local`, FLUX.2 Klein 4B, native BF16, seed/canvas locks, generated text/branding/score/crest/geometry exclusions, Qwen BASE_SCENE or HYBRID_SURFACE inspection, deterministic football geometry ownership, SemanticPublicationGate, Golden 8.5 minimum / 9.0+ elite policy, or exact brand/typography integrity.

Human acceptance remains a prerequisite, not a Golden score. Golden approval remains a quality prerequisite, not publication authority.

### Remaining external blocker

The first genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA + BF16 host. No GPU image, score or benchmark is fabricated by this change set.
