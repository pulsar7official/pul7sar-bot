# Phase 18 Change Set 238 — Fresh Story Gate Semantic Replay

## Purpose

Change Set 238 closes the gap between the structurally admitted fresh-story gate receipt bundle from Change Set 237 and any future canonical-generation authorization.

Change Set 237 intentionally states that it does not know how to replay Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, Story Semantic Preflight, canonical `$0-local` policy, or Semantic/Layer Ownership. A SHA or a `gate_passed=true` field is not semantic verification.

This change therefore introduces a fail-closed gate-specific replay layer. It is the first Phase 18 layer allowed to set `fresh_story_gates_passed=true`, and it can do so only after all six registered replay verifiers execute against the exact byte-bound evidence and reproduce the semantic verification details already bound by the corresponding fresh receipts.

## Required gate order

The replay set is fixed to the same order locked by Change Sets 233–237:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `story_semantic_preflight`
5. `zero_cost_policy`
6. `semantic_layer_ownership`

Missing, extra, reordered, or non-callable verifiers fail closed.

## Replay contract

For every gate, the registered verifier receives:

- the exact repository-bound evidence file path;
- the common `story_snapshot_sha256`;
- the original gate receipt.

The verifier must recompute and return exactly:

- gate ID;
- story snapshot SHA-256;
- source evidence SHA-256 and byte size;
- verifier ID and version;
- gate pass result;
- non-empty semantic verification details.

Change Set 238 then recomputes `verification_details_sha256` from the actual replay output and requires it to equal the digest stored in the admitted gate receipt. A verifier identity/version mismatch, changed semantic result, failed gate, cross-story output, or evidence drift fails closed.

## Freshness is checked again at replay time

Change Set 237 checks receipt freshness when the bundle is assembled. That is insufficient if an authorization attempt happens later.

Change Set 238 therefore accepts an explicit `replayed_at_utc` and checks every receipt again against the original bounded `max_gate_age_seconds` window. A receipt that was fresh during bundle admission but is stale by semantic replay time is rejected.

This closes a time-of-check/time-of-use gap before any future generation authorization.

## Production verifier boundary

This change does **not** invent substitute implementations for the six editorial/safety gates. The engine requires an explicit ordered verifier registry. The CLI loads that registry from a repository Python module exposing `GATE_REPLAY_VERIFIERS`.

If genuine production gate adapters are not registered, semantic replay cannot complete and the process fails closed. Unit tests use deterministic fixture verifiers only to exercise the replay contract; fixture success is not production story approval.

## Authority boundary

A successful Change Set 238 receipt may set only:

- `fresh_story_gates_passed=true`

It still forces all of the following to remain false:

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

Therefore Change Set 238 cannot trigger Qwen, mutate the generation queue, reuse engineering pixels, certify a Golden visual, or publish anything.

## Preserved Phase 18 gates

No existing factual, identity, sentiment, zero-cost, model-provenance, semantic-publication, layer-ownership, brand, typography, visual-critic, human-review, or Golden-quality gate is relaxed.

In particular, the later visual path still requires byte-bound Semantic/Layer QA, byte-bound Visual Critic, Human Review, Golden score >= 8.5 (elite >= 9.0), Exact Brand Integrity, Exact Typography Integrity, and SemanticPublicationGate before publication can be considered.

## Files

Added:

- `engine/intelligence/qwen_image_fresh_story_gate_semantic_replay.py`
- `tests/test_phase18_qwen_image_fresh_story_gate_semantic_replay.py`
- `tools/phase18_replay_qwen_fresh_story_gates.py`
- `docs/PHASE18_CHANGESET_238_FRESH_STORY_GATE_SEMANTIC_REPLAY.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_238.md`

Deleted: none.

Existing production/canonical-generation implementations modified: none.

## GPU status

This change is CPU-only. It does not load Qwen Image 2512 and does not execute CUDA inference.

The first genuine Golden Visual PNG remains blocked until an available `$0-local` host proves the already-locked runtime requirements, including NVIDIA CUDA, native BF16, sufficient live VRAM/system RAM, the exact pinned Qwen Image 2512 snapshot/revision, compatible Diffusers/QwenImagePipeline behavior, and successful sequential CPU offload.
