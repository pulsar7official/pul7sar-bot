# Phase 18 Implementation Log 314 — Qwen Candidate Seal and Admission

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Starting branch HEAD: `2aea932803f36bd4f8217c9b2ba55180ebf102e5`.

`main` was treated as read-only throughout this change set. No merge, rebase, reset, force-update, or content write to `main` was performed.

## Pre-change review

The branch was reviewed before any write and remained on CS313 at `2aea932803f36bd4f8217c9b2ba55180ebf102e5`.

The CS313 workflow was traced from GPU-host qualification through manifest-bound canonical inference and launch-to-output attestation. Its downstream boundary was then compared with the existing canonical-candidate handoff and CS303 byte-admission implementations.

The audit found a concrete orchestration gap rather than a missing quality gate: CS313 uploaded the attested candidate/evidence bundle immediately after attestation, while the repository already had deterministic, non-generative tools to seal those exact bytes into the CS301 handoff and replay them through CS303 admission. Leaving this as a manual follow-up increased the operational gap between a scarce successful GPU run and the first downstream QA receipt.

The existing `engine/intelligence/qwen_image_canonical_candidate_handoff.py` contract was reviewed before modification. It replays `launch_to_output_attestation.json`, requires `genuine_canonical_inference_executed=true`, keeps downstream authorities false, and byte-binds `canonical_candidate.png`, `canonical_inference_receipt.json`, `local_inference_provenance.json`, and the launch attestation itself.

The existing `engine/intelligence/qwen_image_canonical_candidate_byte_admission.py` contract was also reviewed. It replays the sealed handoff and the one-shot canonical inference receipt, verifies exact candidate bytes and PNG dimensions, enforces `$0-local`/offline authority, and grants only `candidate_bytes_admitted_for_post_generation_qa=true` while semantic, human, Golden, Genuine-Golden and publication authorities remain false.

## Modified

### `.github/workflows/phase18-qwen-image-canonical-inference.yml`

The canonical Qwen GPU workflow now continues after its existing independent launch-to-output attestation replay by:

- requiring the canonical-candidate handoff and byte-admission tools to be present on the exact checked-out Phase 18 commit;
- building a CS301 canonical-candidate handoff directly from the already-generated canonical inference output directory;
- replay-verifying that handoff immediately;
- running CS303 exact-byte candidate admission against that exact sealed handoff;
- asserting from the CS303 result that `handoff_sealed=true` and `candidate_bytes_admitted_for_post_generation_qa=true`;
- asserting that `genuine_golden_png_created=false` and `publication_ready=false` remain closed at this edge;
- retaining all generated handoff/admission receipts in the existing workflow artifact bundle.

No second Qwen inference is performed. The workflow reuses the exact bytes already attested by the original CS313 inference step.

### `tests/test_phase18_qwen_image_canonical_inference_workflow.py`

Regression coverage now additionally requires the workflow to contain:

- CS301 handoff build;
- CS301 handoff replay verification;
- CS303 byte admission;
- run-ID-bound handoff/admission destinations;
- positive assertions for sealed-handoff and byte-admission authority;
- negative assertions preventing Genuine-Golden and publication authority from being created by admission.

The existing branch-bound, `$0-local`, offline, CUDA/BF16, manifest-bound Qwen and no-legacy-FLUX checks remain intact.

## Added

### `docs/PHASE18_CHANGESET_314_QWEN_CANDIDATE_SEAL_AND_ADMISSION.md`

Formal CS314 contract and authority boundary.

### `docs/PHASE18_IMPLEMENTATION_LOG_314.md`

This implementation log.

## Deleted

None.

## Preserved gates and authorities

CS314 does not change or weaken:

- fact/freshness requirements;
- entity/identity verification;
- sentiment neutrality and loser-respect constraints;
- zero-cost policy;
- semantic Base QA;
- generated-layer QA;
- composition QA;
- Golden visual-quality adjudication;
- human visual review;
- exact brand/typography review;
- final composed approval;
- final semantic approval;
- `SemanticPublicationGate`;
- exact-byte Genuine Golden materialization;
- final publication readiness.

The added workflow steps are provenance sealing and byte admission only. They cannot turn a canonical candidate into a Golden Visual or make it publication-ready.

## Testing

Static workflow regression coverage was updated with the code change. Repository CI status for the final CS314 HEAD is recorded below once observed during this run; no GPU success is inferred from CPU CI.

## GPU execution blocker

No genuine Qwen image is claimed by CS314 itself. A real candidate still requires a compatible zero-cost self-hosted runner with CUDA-enabled PyTorch, at least one NVIDIA CUDA device, native BF16 support, the compatible Qwen-Image runtime, the exact already-local pinned `Qwen/Qwen-Image-2512` snapshot, and sufficient RAM/VRAM for actual model load and inference.

If such a runner is unavailable, CS314 materially reduces the remaining procedural gap but cannot fabricate `canonical_candidate.png`.

## Remaining path after CS314

Once a compatible GPU produces a real candidate, the workflow now exits with both the exact sealed handoff and CS303 admission receipt in the same artifact bundle. The remaining intentional gates are:

1. semantic Base QA and factual/entity/sentiment revalidation;
2. identity and generated-layer lineage checks;
3. composition/post-composition QA;
4. Golden visual-quality adjudication;
5. human visual review;
6. exact brand/typography and final composed approval;
7. final semantic approval;
8. lineage-bound `SemanticPublicationGate` execution;
9. exact-byte Genuine Golden PNG materialization;
10. separate publication readiness.

No placeholder or fabricated PNG may satisfy any stage.
