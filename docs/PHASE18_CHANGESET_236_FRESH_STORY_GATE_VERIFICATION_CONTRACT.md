# Phase 18 Change Set 236 — Fresh Story Gate Verification Contract

## Purpose

Change Set 235 byte-bound the exact evidence files supplied for the six fresh-story gates required by the controlled Golden-trial preflight. That proved which bytes were present, but intentionally did not interpret those bytes as gate approvals.

Change Set 236 closes the next cross-story/cross-run substitution gap. It locks the exact invariants that future gate-specific verification receipts must satisfy before any canonical-generation authorization can be considered.

## Required gates

The contract preserves the exact Change Set 233 order:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `story_semantic_preflight`
5. `zero_cost_policy`
6. `semantic_layer_ownership`

For every gate, a future verification receipt must bind to the exact `source_evidence_sha256` and `source_evidence_byte_size` recorded by Change Set 235.

## Same-story invariant

Every future gate receipt must carry one common `story_snapshot_sha256`. The contract therefore prevents a later authorization layer from silently combining, for example, Fact Lock from story A with identity or sentiment evidence from story B.

## Required receipt shape

Each future gate-specific receipt must expose the locked fields:

- `schema`
- `gate_id`
- `story_snapshot_sha256`
- `source_evidence_sha256`
- `source_evidence_byte_size`
- `verifier_id`
- `verifier_version`
- `evaluated_at_utc`
- `gate_passed`
- `verification_details_sha256`

A bare `gate_passed=true` is therefore insufficient.

## Authority boundary

This Change Set is a verification contract only. It does not claim that any gate passed and does not execute model or CUDA work. The following remain false and fail-closed:

- `fresh_story_gates_passed`
- `controlled_trial_preflight_valid`
- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `queue_mutated`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

The pre-existing generated-text, generated-branding, exact-fact, entity-mark, exact-sport-geometry, Semantic/Layer QA, Visual Critic, Human Review, 8.5 Golden minimum, 9.0 elite threshold, Exact Brand, Exact Typography, and SemanticPublicationGate requirements remain unchanged.

## Files

Added:

- `engine/intelligence/qwen_image_fresh_story_gate_verification_contract.py`
- `tests/test_phase18_qwen_image_fresh_story_gate_verification_contract.py`
- `tools/phase18_build_qwen_fresh_story_gate_verification_contract.py`
- `docs/PHASE18_CHANGESET_236_FRESH_STORY_GATE_VERIFICATION_CONTRACT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_236.md`

Deleted: none.

Existing production/canonical generation code modified: none.

## CUDA / Golden status

No CUDA inference is claimed by this Change Set. No engineering PNG or Golden PNG is created. The genuine GPU path remains blocked until a compatible zero-cost local NVIDIA environment is available with the exact pinned Qwen Image 2512 runtime requirements.
