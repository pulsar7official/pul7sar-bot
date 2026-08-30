# Phase 18 Implementation Log — Change Set 265

## Baseline

- Working branch: `phase18/story-intelligence` only.
- Baseline HEAD reviewed before writes: `0a2300940ece329a0f0d0f78ec58f308d97669c4`.
- `main` reviewed read-only at `7cca9afed308492c15bda397d06ce3a393791d23`.
- No merge, rebase, force-update, or direct write to `main` was performed.
- CS264 HEAD verification was already green before CS265 work began.

## Purpose

CS264 deliberately leaves `identity_approved=false` because the pinned Qwen2.5-VL semantic inspector does not produce a pixel-level identity verdict. CS265 therefore introduces a fail-closed requirement classifier rather than pretending that semantic scene QA proves a generated person's identity.

## Added

1. `engine/intelligence/qwen_image_canonical_candidate_identity_requirement.py`
   - Replays CS264.
   - Requires CS264 semantic base-scene approval and all downstream authorities still closed.
   - Binds the exact `entity_identity_verification` evidence referenced by the CS257 manifest.
   - Re-evaluates the existing deterministic `evaluate_entity_identity` policy.
   - Records canonical human identity targets.
   - Sets only `identity_requirement_classified=true` and `pixel_identity_review_required=<bool>`.
   - Never grants identity, semantic, Human Review, Golden, or publication authority.
   - Verifier rejects later identity-evidence byte drift.

2. `tests/test_phase18_qwen_image_canonical_candidate_identity_requirement.py`
   - Human entity requires pixel-identity review.
   - Non-human entity does not manufacture identity approval.
   - Identity evidence byte drift is rejected.
   - Uses standard-library `unittest` only.

3. `tools/phase18_classify_canonical_candidate_identity_requirement.py`
   - CPU-only production CLI.

4. `docs/PHASE18_CHANGESET_265_CANONICAL_CANDIDATE_IDENTITY_REQUIREMENT.md`

5. `docs/PHASE18_IMPLEMENTATION_LOG_265.md`

## Modified

No pre-existing production or gate file was modified.

## Deleted

None.

## Existing gates preserved

No changes were made to Fact Lock, entity/identity semantic verification, sentiment neutrality, zero-cost policy, semantic-layer ownership, Qwen Image generation authorization, SemanticPublicationGate, Visual Critic, Human Review, Golden thresholds, exact brand integrity, or typography integrity.

## Authority state

CS265 may establish only:

- `identity_requirement_classified=true`
- `pixel_identity_review_required=true|false`

It keeps:

- `identity_approved=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `genuine_golden_png_created=false`
- `golden_quality_approved=false`
- `publication_ready=false`

## CUDA / Golden status

No genuine Qwen Image inference was executed in this change set and no Genuine Golden Visual PNG was created. The live generation blocker remains the absence of an available compatible host proving NVIDIA CUDA, native BF16, sufficient VRAM/RAM, the pinned Qwen/Qwen-Image-2512 revision, successful pipeline load/offload, and canonical `$0-local` execution.

## Remaining gap

For candidates whose CS265 receipt says `pixel_identity_review_required=true`, the next safe step is a byte-bound pixel-identity evidence contract that must compare the exact CS263 candidate against approved source-backed identity references. It must fail closed when no compatible identity-verification execution is available and must not substitute the general Qwen2.5-VL scene verdict for person identity.
