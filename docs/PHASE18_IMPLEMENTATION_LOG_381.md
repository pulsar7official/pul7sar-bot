# Phase 18 Implementation Log 381 — CS351 CUDA BF16 Runtime Smoke Preflight

## Branch safety

Target branch: `phase18/story-intelligence` only.
Starting branch HEAD: `ccf08e4594f99af8f74e7c38b3c10d7fba3785e5`.
Starting `main` HEAD observed read-only: `a906f90bc79da616a1640da1a1f5959f81096376`.
`main` was not modified, merged, rebased, reset, force-updated, or otherwise written.

## Why this boundary was selected

No verified direct publication-authority consumer was found after CS350/CS286, so no parallel publication contract was invented.

The existing genuine-inference path was reviewed instead. CS354 already owns exact local snapshot-byte inventory and replay, so duplicating snapshot lineage in CS351 would be wrong. A real remaining execution gap existed in CS351: CUDA/native-BF16 capability flags could pass without proving that a tiny BF16 CUDA allocation/kernel/synchronization actually works on the host.

## What changed

### Modified

1. `engine/intelligence/qwen_image_gpu_readiness.py`
   - Raised schema from `pul7sar.phase18.qwen_image_gpu_readiness.v2` to `v3`.
   - Added `cuda_bf16_smoke_test_passed` to the readiness receipt.
   - Added a two-element local BF16 CUDA smoke operation and explicit device synchronization.
   - Added fail-closed blocker `cuda_bf16_smoke_test_failed`.
   - A failed real CUDA/BF16 operation now keeps `static_preflight_passed=false` and `ready_for_model_load_attempt=false` before Qwen model load.
   - No model load, download, inference, pixel work, authority grant, upload, or publication was added.

2. `tests/test_phase18_qwen_image_gpu_readiness.py`
   - Updated compatible-host expectations for the new smoke field.
   - Added dedicated regression for advertised CUDA/BF16 with a failing real-operation smoke probe.
   - Preserved CPU-only, revision, snapshot-structure, component, pipeline-class, zero-cost, and no-inference assertions.
   - CI compatibility correction: removed the newly introduced module-level `pytest` dependency/autouse fixture because the authoritative Phase 18 workflow installs only `requirements.txt` and imports all `test_phase18_*.py` modules through `unittest discover`.
   - Each synthetic compatible-GPU test now stubs `_cuda_bf16_smoke_test` explicitly, keeping the regression behavior deterministic without adding or changing dependencies.

### Added

- `docs/PHASE18_CHANGESET_381_CS351_CUDA_BF16_RUNTIME_SMOKE_PREFLIGHT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_381.md`

### Deleted

None.

### Dependencies

None added or changed. In particular, `pytest` was not added to `requirements.txt`; the accidental test-only import was removed instead.

## Commits

Production hardening commit: `c07fb984fab7c79b4e553365f81d986fbf3aebf0`.
Initial code-and-test-bearing commit: `746efeb7770248bec480e9526c05382bb0463c1d`.
Changeset documentation commit: `c73d7a84667f3b0bed8cef293f2e36e3f72b1913`.
Initial implementation-log commit: `84ba61d340b5df7bce9d0ede63e1402fe8702648`.
CI compatibility fix commit and final exact code-and-test-bearing SHA: `cf5523d21992d060505ec66eb98f973f7c67a926`.
Failure-analysis log update commit: `013395c5a0e02b0415dd79f9535654efdee36c49`.
This terminal-green log update is committed separately on the same branch.

## Gate preservation

CS381 changes only pre-model-load runtime compatibility. It deliberately leaves exact snapshot byte inventory to existing CS352/CS354 and does not create a competing asset-verification gate.

All factual/freshness, Entity/Identity, sentiment neutrality / loser-respect, `$0-local`, semantic QA, visual-quality, Human Visual Review, Final Presentation / Brand / Typography, Final Composed, Final Semantic, actual SemanticPublicationGate, Genuine-Golden byte identity, publication readiness, and external publication authority boundaries remain independent and fail-closed.

The readiness receipt still requires:

- `genuine_inference_executed=false`
- `ready_for_genuine_inference_claim=false`
- `network_required=false`
- `zero_cost_local_only=true`

## Tests / CI

The first authoritative workflow for initial exact code-and-test SHA `746efeb7770248bec480e9526c05382bb0463c1d` was `Phase 18 Story Intelligence Verification` run `34427480974`, run number `5305`.

Result: `completed / failure`.

Failure boundary: `Syntax and discover validation`; later Phase 18 workflow steps were skipped. The authoritative workflow executes `python tools/phase18_cpu_validate.py`, which imports `test_phase18_*.py` through `python -m unittest discover` after installing only `requirements.txt`. The CS381 test commit had newly introduced a module-level `import pytest` solely for an autouse fixture. That new dependency was unnecessary and incompatible with the authoritative discovery environment.

Corrective commit `cf5523d21992d060505ec66eb98f973f7c67a926` removes the `pytest` import/autouse fixture and explicitly stubs the CUDA BF16 smoke result in the relevant synthetic GPU tests. No production behavior and no dependency manifest were changed by this correction.

The replacement authoritative workflow is `Phase 18 Story Intelligence Verification` run `34431012562`, run number `5311`, on exact corrective SHA `cf5523d21992d060505ec66eb98f973f7c67a926`.

Result: `completed / success`.

Every authoritative job step completed successfully, including `Syntax and discover validation`, `Completion and production isolation`, all visual-study/golden-handoff build-and-verify steps, and artifact uploads. Therefore CS381 is terminal-green on exact code-and-test SHA `cf5523d21992d060505ec66eb98f973f7c67a926`.

## Genuine Golden execution blocker

No Genuine Golden PNG is claimed by this changeset. A real canonical candidate still requires a compatible zero-cost self-hosted NVIDIA CUDA runner, CUDA-enabled PyTorch, native BF16, a passing real BF16 CUDA smoke operation, sufficient RAM/VRAM under actual model load/inference, and the approved already-local pinned Qwen snapshot and verifier/runtime assets.

The current execution environment remains CPU-only (`torch=2.10.0+cpu`, CUDA unavailable, no CUDA runtime reported by PyTorch, zero CUDA devices, native CUDA BF16 unavailable, and `nvidia-smi` unavailable). No fixture/test bytes are treated as a production Golden Visual.

## Remaining gap

CS381 is terminal-green. Once a compatible host exists, the existing workflow can proceed through CS351 readiness, CS354 exact snapshot-byte-bound launch, manifest-bound genuine inference, launch-to-output attestation, candidate handoff, and downstream QA. The first actual model-load/inference attempt remains the only valid proof of resource sufficiency; CS381 does not invent a VRAM threshold.