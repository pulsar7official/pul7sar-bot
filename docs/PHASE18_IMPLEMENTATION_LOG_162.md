# PUL7SAR Phase 18 — Implementation Log 162

## Scope / branch safety

- Repository: `pulsar7official/pul7sar-bot`.
- Write target: `phase18/story-intelligence` only.
- `main` was reviewed separately and was not modified, merged, rebased, force-updated, or used as a write target.
- Starting Phase 18 HEAD reviewed for this work: `32995556ce5f355b05d22bdd421cb64f5e1e75e3`.

## Branch / CI state reviewed first

The branch HEAD above triggered `Phase 18 Story Intelligence Verification` run `32921552740` / run number `2812`, which completed with `failure` in the `Syntax and discover validation` step.

All visible companion Phase 18 visual-study workflows for the same HEAD completed successfully.

The Story Intelligence log showed exactly two failing tests out of 1,173 Phase 18 tests:

1. `GoldenVisualHandoffTests.test_golden_request_uses_real_phase18_layout_and_zero_cost_model`
   - missing exact marker: `story-specific non-identifying sports atmosphere`.
2. `GoldenVisualHandoffTests.test_golden_request_does_not_claim_specific_real_venue_or_person`
   - missing exact marker: `must not imply a specific real venue`.

The generated compact prompt still contained equivalent safety intent, but these phrases are part of the existing fail-closed Golden handoff contract. No verifier or test was weakened.

## Change Set 162 — Golden Prompt Compatibility Fix

### Modified

1. `engine/intelligence/golden_prompt_budget.py`
   - restored the exact marker `story-specific non-identifying sports atmosphere`;
   - restored the exact marker `must not imply a specific real venue`;
   - shortened adjacent descriptive prose so the compact scene prompt remains within the locked 1,200-character budget;
   - retained all current exact Golden v5 unified-scene, reserved-surface, deterministic-geometry, no-collage and unbranded-base markers.

2. `tests/test_phase18_golden_prompt_budget.py`
   - added both restored non-identifying phrases to the required v5 marker regression set.

### Added

1. `docs/PHASE18_CHANGESET_162_GOLDEN_PROMPT_COMPATIBILITY_FIX.md`.
2. `docs/PHASE18_IMPLEMENTATION_LOG_162.md`.

### Deleted

None.

## Gate preservation

No relaxation was made to Fact Lock / factual integrity, Entity and Identity Verification, Sentiment / neutrality, `$0-local`, pinned FLUX/Qwen revisions, native BF16, GPU/VRAM qualification, lease-bound requalification, Candidate/request/seed/canvas/SHA locks, generated text/branding/exact facts/entity marks/sport-geometry prohibitions, Original Scene runtime admission, Qwen BASE_SCENE/HYBRID_SURFACE, deterministic football geometry, provenance/evidence replay, Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand Integrity, Typography Integrity, or SemanticPublicationGate / Final Publication Readiness.

The optimization target remains only Golden benchmark scene prose. `negative_constraints` and `factual_constraints` are unchanged.

## Tests / CI

- Failure diagnosed from Story Intelligence run `32921552740` / `2812`.
- The two failing exact-marker conditions were corrected without changing their tests or relaxing the Golden contract.
- A fresh Story Intelligence workflow is expected from the corrected branch HEAD; no CI success is claimed until GitHub reports an actual successful run.

## Genuine Golden PNG status

No genuine new Golden Hybrid v5 PNG is claimed in this change set.

The exact remaining physical blocker is still an available host satisfying NVIDIA CUDA, native BF16, sufficient total and live-free VRAM, pinned FLUX.2 Klein 4B and Qwen revisions, and stable runtime fingerprinting across Candidate 1 execution.

No fake PNG, visual score, GPU benchmark, or publication result was substituted.

## Next executable path

`immutable Phase 18 source -> pinned runtime/models -> runtime fingerprint -> CUDA/BF16/live-VRAM -> Original Scene admission -> Candidate 1 -> provenance replay -> BASE_SCENE -> deterministic football Hybrid -> HYBRID_SURFACE -> sealed human review -> Golden 8.5/9.0`

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted through the required semantic and visual review stages.
