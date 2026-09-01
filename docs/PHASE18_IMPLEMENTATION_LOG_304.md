# Phase 18 Implementation Log — Change Set 304

## Change Set

**CS304 — Byte-Admission-Bound Semantic Base QA**

Starting verified branch state: `d6dad376b289594b03651ab4e5f4130a4925949b` on `phase18/story-intelligence`.

## Review finding

The initial concern was that CS264 might bypass CS303. Source review showed that this was not the case: CS264 already imports and calls `verify_canonical_candidate_byte_admission`, and CS303 upgraded that verifier/schema to require the CS301/302 sealed handoff.

The real defect was a compatibility blocker immediately after that replay. CS264 still required legacy admission authority fields that the CS303 v2 receipt no longer emits. Its tests mocked the verifier using the obsolete source shape, so CI could remain green while a genuine CS303 -> semantic-QA transition would fail before semantic inspection.

CS304 fixes that executable contract and makes the sealed handoff lineage explicit in the semantic QA receipt.

## Added

- `docs/PHASE18_CHANGESET_304_BYTE_ADMISSION_BOUND_SEMANTIC_BASE_QA.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_304.md`

## Modified

- `engine/intelligence/qwen_image_canonical_candidate_semantic_base_qa.py`
  - bumped semantic base QA receipt schema from v1 to v2;
  - replaced obsolete legacy source-authority requirements with CS303 v2 authority;
  - requires `genuine_canonical_inference_executed`, `handoff_sealed`, and byte admission;
  - requires `$0-local`, `network_allowed=false`, and `local_files_only=true`;
  - requires a valid `source_candidate_handoff.handoff_sha256`;
  - renamed the source ingress/binding from legacy CS263 terminology to candidate admission terminology;
  - binds the sealed candidate handoff digest into the semantic QA receipt;
  - verifier replays CS303 and checks admission digest, handoff digest, story binding, and candidate path/hash/size/dimensions;
  - leaves identity, global semantic, Human Review, Golden, and publication authority closed.

- `tools/phase18_run_canonical_candidate_semantic_base_qa.py`
  - production argument changed from `--cs263-receipt` to `--candidate-admission`;
  - no prompt/model/network/cost/semantic/Golden/publication override was introduced.

- `tests/test_phase18_qwen_image_canonical_candidate_semantic_base_qa.py`
  - fixture updated to model the CS303 v2 admission authority shape;
  - regression verifies explicit sealed-handoff digest binding;
  - regression rejects obsolete legacy authority shape;
  - regression rejects missing handoff binding;
  - regression rejects paid-mode and network-enabled drift;
  - existing semantic/tamper/verifier/output-directory coverage retained.

## Deleted

None.

## Authority preservation

CS304 does not weaken or bypass any of the following:

- factual/freshness locks;
- entity/identity evidence and pixel-identity requirements;
- sentiment neutrality and loser-respect rules;
- story-bound semantic ownership;
- `$0-local` and local-only execution;
- generated-layer/composition QA;
- visual-quality adjudication;
- Human Review;
- Exact Brand/Typography;
- `SemanticPublicationGate`;
- Genuine Golden materialization;
- publication readiness.

The CS304 receipt must continue to carry:

- `identity_approved=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`

## Testing

Static syntax of the replacement semantic-QA module was checked locally with `python -m py_compile` before committing.

Repository regressions are delegated to the branch's existing GitHub Actions verification workflow. The exact final CS304 SHA and terminal workflow result must be checked after this log commit; no green claim is valid until the workflow reports `completed/success` for that exact SHA.

## Genuine Golden execution status

No genuine Qwen-Image model load, CUDA/BF16 inference, `canonical_candidate.png`, production composition, or Genuine Golden PNG was fabricated in this change set.

The remaining execution blocker is a compatible zero-cost host providing NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the CS260-authorized QwenImagePipeline/Diffusers runtime, sequential CPU offload, the exact approved already-local Qwen snapshot, and enough RAM/VRAM proven by real model loading and inference.

## Remaining path

`verified launch manifest -> preload/offline/runtime gates -> genuine local Qwen inference -> provenance/postflight replay -> sealed handoff -> CS303 byte admission -> CS304 semantic base QA -> identity requirement/review -> generated-layer/composition QA -> visual-quality adjudication -> Human Review -> Exact Brand/Typography -> SemanticPublicationGate -> Genuine Golden materialization -> publication readiness`
