# Phase 18 Change Set 237 — Fresh Story Gate Receipt Bundle Admission

## Purpose

Change Set 237 closes the gap between the Change Set 236 verification contract and any later semantic replay of the six fresh-story gates. It admits a complete receipt set only when every receipt belongs to the same story snapshot, binds to the exact evidence bytes locked by Change Set 235/236, and falls inside one explicit freshness window.

This is CPU-only preparatory work. It does not load Qwen, invoke CUDA, generate pixels, approve semantics, approve quality, or authorize publication.

## Required gate order

The admitted receipt bundle must contain exactly these gates, in this order:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `story_semantic_preflight`
5. `zero_cost_policy`
6. `semantic_layer_ownership`

Each receipt must carry all fields locked by Change Set 236, including the common story snapshot SHA-256, exact source-evidence SHA-256 and byte size, verifier identity/version, evaluation time, pass result, and verification-details SHA-256.

## Freshness boundary

The bundle builder requires an explicit UTC evaluation time and an explicit maximum gate age. The maximum accepted window is capped at 3600 seconds. Future-dated receipts and receipts older than the locked window fail closed.

This cap does not claim that one hour is universally appropriate for every production story. Callers may select a stricter value. Its purpose is to prevent an unbounded or effectively permanent story-gate receipt from becoming input to a later Golden-trial authorization.

## Byte and story binding

For every receipt, Change Set 237 verifies:

- gate order and identity;
- one shared `story_snapshot_sha256`;
- the exact evidence SHA-256 required by Change Set 236;
- the exact evidence byte size required by Change Set 236;
- a non-empty verifier id and version;
- `gate_passed=true`;
- a valid verification-details SHA-256;
- evaluation time inside the explicit freshness window.

The resulting bundle stores a SHA-256 of each full receipt. Replay rebuilds the expected bundle from the current parent contract, evidence manifest, and supplied receipts, so receipt mutation after admission fails closed. Parent replay also preserves Change Set 235 byte-level evidence verification.

## Authority boundary

Receipt admission is deliberately weaker than semantic verification. Even a structurally valid, fresh, same-story bundle keeps all of the following false:

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

A later layer must replay the gate-specific verification details using the actual verifier implementations before `fresh_story_gates_passed` can become true.

## Files

Added:

- `engine/intelligence/qwen_image_fresh_story_gate_receipt_bundle.py`
- `tests/test_phase18_qwen_image_fresh_story_gate_receipt_bundle.py`
- `tools/phase18_build_qwen_fresh_story_gate_receipt_bundle.py`
- `docs/PHASE18_CHANGESET_237_FRESH_STORY_GATE_RECEIPT_BUNDLE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_237.md`

Deleted: none.

No existing production/canonical-generation implementation is modified by this change set.

## Golden Visual impact

The first genuine Golden Visual PNG is still blocked on compatible zero-cost CUDA execution and the downstream evidence chain. Change Set 237 materially reduces the remaining authorization gap by making a six-gate receipt set immutable, same-story, evidence-bound, and freshness-bounded before semantic replay is attempted.
