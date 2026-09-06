# Phase 18 Change Set 302 — Sealed Candidate Execution

## Purpose

CS302 closes the operational gap between the CS300 successful canonical inference replay and the CS301 canonical candidate handoff seal. The new production wrapper does not return success after inference alone. It requires the canonical launcher to succeed, then builds `canonical_candidate_handoff.json`, independently verifies that handoff, and only then returns zero.

## Execution contract

The path is now:

1. verified launch manifest;
2. mandatory preload diagnostic;
3. zero-cost/offline child execution envelope;
4. exact pre-model-load host identity enforcement;
5. genuine local Qwen model load and one-shot inference;
6. CS290 provenance;
7. CS293/300 launch-to-output replay;
8. CS301 handoff build;
9. independent CS301 handoff verification;
10. downstream factual/identity/sentiment, semantic, composition, visual-quality, human-review, brand/typography, semantic-publication, Golden materialization, and publication-readiness gates.

A non-zero inference exit is propagated unchanged and no handoff is attempted. An existing handoff path is rejected fail-closed rather than overwritten.

## Authority boundary

CS302 grants no downstream approval. Both the built and replay-verified handoff must keep the following false:

- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

The wrapper additionally requires `genuine_canonical_inference_executed=true` and `handoff_sealed=true` before it may return success.

## Zero-cost and network boundary

CS302 does not alter the existing `$0-local`, local snapshot, `local_files_only=True`, Hugging Face offline, Transformers offline, or no-network evidence contracts. It composes the already-verified CS295-CS300 execution path and CS301 handoff verifier rather than introducing a second inference path.

## New files

- `engine/intelligence/qwen_image_sealed_candidate_execution.py`
- `tools/phase18_run_sealed_canonical_candidate.py`
- `tests/test_phase18_qwen_image_sealed_candidate_execution.py`
- `docs/PHASE18_CHANGESET_302_SEALED_CANDIDATE_EXECUTION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_302.md`

## Test intent

Regression coverage verifies that:

- non-zero inference exits are propagated without handoff creation;
- zero exit requires both handoff build and independent replay verification;
- premature semantic/Golden/publication authority is rejected;
- an existing handoff is not overwritten.

These tests are CPU/control-plane regressions only. They do not claim a Qwen model load, CUDA/BF16 inference, candidate PNG, Golden PNG, or publication readiness.
