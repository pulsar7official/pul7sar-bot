# Phase 18 — Change Set 233: Controlled Golden-Trial Preflight Contract

## Purpose

Change Set 233 adds the final CPU-only contract layer immediately before a future live Golden-trial gate for the pinned `Qwen/Qwen-Image-2512` runtime.

It deliberately does **not** authorize generation. Its job is to replay the host-bound qualification evidence produced by Change Set 232 and lock, before any future canonical inference, the exact evidence families and post-generation gates that may not be bypassed.

## Why this layer exists

Change Set 232 can prove only that an exact observed runtime completed the locked engineering envelope. It explicitly requires a live host identity recheck before any Golden trial. A later generation step must also use fresh story evidence rather than assuming that facts, identity, sentiment, or semantics remain valid because an earlier engineering measurement succeeded.

Change Set 233 therefore separates two claims that must never be conflated:

1. the preflight **contract is locked**; and
2. the preflight has **actually passed live**.

Only the first claim is possible in this Change Set.

## Evidence replay

The contract builder requires:

- Change Set 232 host-bound qualification;
- Change Set 231 candidate;
- Change Set 230 execution receipt;
- SHA-256 anchors for all three receipt files.

It invokes the Change Set 232 verifier, which transitively rebuilds the qualification chain and replays the engineering PNG evidence. A self-asserted host qualification is therefore insufficient.

## Locked fresh pre-generation evidence

The future live gate must freshly prove all of:

- `fact_lock`
- `entity_identity_verification`
- `sentiment_neutrality`
- `story_semantic_preflight`
- `zero_cost_policy`
- `semantic_layer_ownership`

The contract does not invent or synthesize these receipts. It only locks them as mandatory requirements.

## Locked pixel boundaries

Model pixels remain forbidden from owning:

- generated text;
- generated branding;
- generated exact facts;
- generated entity marks;
- generated exact sport geometry.

Engineering measurement pixels remain non-reusable as canonical pixels.

## Locked post-generation gates

A genuine future canonical PNG must still pass:

- byte-bound Semantic/Layer QA;
- byte-bound Visual Critic;
- Human Review;
- Golden quality minimum `8.5`;
- elite quality threshold `9.0`;
- Exact Brand Integrity;
- Exact Typography Integrity;
- SemanticPublicationGate.

## Authority boundary

A valid Change Set 233 contract always keeps these claims false:

- `controlled_trial_preflight_valid`
- `live_host_recheck_passed`
- `fresh_story_gates_passed`
- `genuine_canonical_inference_executed`
- `genuine_golden_png_created`
- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `queue_mutated`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

The layer therefore cannot turn test fixtures, engineering PNGs, or an old host receipt into a Golden image.

## Files

Added:

- `engine/intelligence/qwen_image_controlled_golden_trial_preflight.py`
- `tools/phase18_build_qwen_controlled_golden_trial_preflight.py`
- `tests/test_phase18_qwen_image_controlled_golden_trial_preflight.py`
- `docs/PHASE18_CHANGESET_233_CONTROLLED_GOLDEN_TRIAL_PREFLIGHT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_233.md`

Deleted: none.

No production/canonical generation file is modified by this Change Set.

## Remaining execution blocker

No genuine Golden PNG is claimed. The execution environment available during this Change Set does not expose a compatible self-hosted host proving all of:

`NVIDIA CUDA + native BF16 + sufficient live VRAM + sufficient system RAM + exact pinned Qwen/Qwen-Image-2512 revision + compatible Diffusers/QwenImagePipeline + successful sequential CPU offload + canonical $0-local`.

The next live stage must recheck the exact runtime identity, obtain fresh canonical story-gate evidence, and only then consider a separate generation-authorization receipt. Change Set 233 itself can never grant that authority.
