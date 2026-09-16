# Phase 18 Change Set 316 — Qwen Workflow Semantic Continuation

## Purpose

Change Set 316 removes the manual execution gap between the canonical Qwen-Image GPU workflow's CS303 exact-byte candidate admission and the CS315 admitted-candidate semantic checkpoint.

A successful genuine Qwen inference is now carried, in the same branch-bound and zero-cost workflow run, through:

1. launch-to-output attestation replay;
2. CS301 exact candidate handoff sealing and verification;
3. CS303 exact-byte admission;
4. CS304 pinned local Qwen2.5-VL BASE_SCENE semantic QA; and
5. CS305 pixel-identity-review requirement classification.

The workflow stops there. It does not approve identity, final semantics, Human Visual Review, Golden quality, Genuine Golden materialization, or publication.

## Fail-closed invariants

The canonical workflow remains restricted to `refs/heads/phase18/story-intelligence`, `$0-local`, self-hosted CUDA/BF16 execution, and an already-local Qwen-Image snapshot.

CS316 additionally makes the semantic continuation explicitly offline at workflow scope with:

- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- `HF_DATASETS_OFFLINE=1`
- `HF_HUB_DISABLE_TELEMETRY=1`

If the pinned Qwen2.5-VL semantic verifier is not already available locally, the checkpoint must fail rather than fetch it from the network.

The CS315 command is passed the `receipt_path` emitted by the same run's CS303 admission result. The workflow requires:

- `semantic_inspection_executed=true`
- `semantic_base_scene_approved=true`
- `identity_requirement_classified=true`
- `pixel_identity_review_required` to be an explicit boolean

It also requires all of the following to remain false:

- `identity_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

A CS304 rejection is preserved in the uploaded evidence but causes the workflow to fail; it is never converted into a pass.

## Files

Modified:

- `.github/workflows/phase18-qwen-image-canonical-inference.yml`
- `tests/test_phase18_qwen_image_canonical_inference_workflow.py`

Added:

- `docs/PHASE18_CHANGESET_316_QWEN_WORKFLOW_SEMANTIC_CONTINUATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_316.md`

Deleted: none.

## Authority boundary

CS316 is orchestration only. It does not alter the verdict logic or thresholds in CS304/CS305 and does not bypass any factual, identity, sentiment, visual-quality, semantic-publication, materialization, or publication-readiness gate.
