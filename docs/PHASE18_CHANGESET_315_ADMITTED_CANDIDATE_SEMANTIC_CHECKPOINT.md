# Phase 18 Change Set 315 — Admitted Candidate Semantic Checkpoint

## Purpose

CS314 preserves a scarce genuine Qwen-Image inference by sealing the exact output bytes and admitting them through CS303. The next two repository authorities already existed, but required separate operator orchestration:

1. CS304 runs pinned local Qwen2.5-VL BASE_SCENE semantic QA on the exact CS303-admitted PNG.
2. CS305 derives, from the same launch/evidence lineage, whether separate human pixel-identity review is mandatory.

CS315 adds one fail-closed orchestration command that executes exactly those existing authorities in order. It does not alter either authority and does not add a shortcut around later gates.

## New command

`tools/phase18_run_admitted_candidate_semantic_checkpoint.py`

Inputs:

- repository-contained CS303 candidate-admission receipt;
- a new repository-contained output root;
- repository root.

Execution:

`CS303 admission -> CS304 semantic Base QA -> (only if CS304 passes) CS305 identity-requirement classification`

If CS304 rejects, CS315 writes a rejection checkpoint receipt and stops before CS305. If CS304 passes, CS305 is built and independently replay-verified before the checkpoint is considered passed.

## Authority boundaries

The checkpoint requires the existing CS304 and CS305 verifiers to keep all of these false:

- `identity_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

CS315 performs no image generation, no pixel modification, no network publication, no identity approval, no Human Review, no Golden adjudication, no final semantic approval, and no publication side effect.

## Lineage guarantees

The existing CS304 implementation replays CS303 and binds the inspected PNG byte-for-byte to the admitted candidate. The existing CS305 implementation replays CS304 and derives identity evidence exclusively through the candidate launch lineage back to the exact CS257 evidence set.

CS315 additionally rejects any story SHA or candidate binding drift between its verified CS304 and CS305 receipts.

## Zero-cost and local semantics

The semantic inspection remains the repository's pinned local Qwen2.5-VL-3B-Instruct inspector at the immutable approved revision. Network-enabled or remote semantic verification is not introduced. Existing offline execution policy remains authoritative.

## Files

Added:

- `tools/phase18_run_admitted_candidate_semantic_checkpoint.py`
- `tests/test_phase18_admitted_candidate_semantic_checkpoint.py`
- `docs/PHASE18_CHANGESET_315_ADMITTED_CANDIDATE_SEMANTIC_CHECKPOINT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_315.md`

Modified: none.

Deleted: none.

## Remaining gap

A real first candidate still requires a compatible zero-cost CUDA/BF16 execution host with the exact already-local pinned Qwen-Image snapshot. CS304 additionally requires the pinned Qwen2.5-VL semantic model to be available locally/offline when the checkpoint is executed.

After CS315, any passing candidate still must traverse identity review when required, Generated-Layer QA, deterministic composition/post-composition QA, Golden quality adjudication, Human Visual Review, exact brand/typography verification, final composed approval, final semantic approval, `SemanticPublicationGate`, exact-byte Genuine Golden materialization, and final publication readiness.
