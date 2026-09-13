# Phase 18 Change Set 381 — CS351 CUDA BF16 Runtime Smoke Preflight

## Purpose

Harden the existing zero-cost Qwen-Image GPU readiness boundary before the first genuine canonical inference attempt.

CS351 previously relied on CUDA/native-BF16 capability reports (`torch.cuda.is_available()` and `torch.cuda.is_bf16_supported()`) plus local snapshot structure checks. Those reports can still be true on a host where the first CUDA allocation/kernel/synchronization fails because of a driver/runtime/kernel problem.

This changeset closes that execution gap without creating a new gate and without loading Qwen.

## Production change

`engine/intelligence/qwen_image_gpu_readiness.py`

- Raised the CS351 readiness schema from v2 to v3.
- Added `cuda_bf16_smoke_test_passed` to the fail-closed readiness receipt.
- Added a tiny local CUDA BF16 smoke probe: allocate two BF16 values on `cuda:0`, perform one addition, synchronize device 0, copy the two results back to CPU, and require `[2.0, 2.0]`.
- Adds blocker `cuda_bf16_smoke_test_failed` when CUDA/native BF16 are advertised but the real operation cannot complete correctly.
- Keeps `ready_for_model_load_attempt=false` when the smoke probe fails.
- Performs no model download, Qwen model load, Qwen inference, pixel creation/mutation, semantic approval, Human Visual Review, Golden-quality approval, Genuine-Golden materialization, upload, or publication.
- Keeps network access unnecessary and the existing `$0-local` contract unchanged.

The exact snapshot byte inventory remains owned by the existing CS352/CS354 path. CS381 deliberately does not duplicate or weaken that inventory binding.

## Tests

`tests/test_phase18_qwen_image_gpu_readiness.py`

- Existing compatible-host tests now explicitly require `cuda_bf16_smoke_test_passed=true`.
- CPU-only path explicitly records the smoke probe as not passed while remaining fail-closed for the existing CUDA/BF16 blockers.
- Added regression proving that a host which advertises CUDA + BF16 but fails the smoke operation is blocked before model load.
- Preserved wrong-revision, empty/partial snapshot, pipeline-class mismatch, zero-cost, no-inference, and no-authority behavior.

## Gate preservation

This is a pre-inference runtime-compatibility hardening only. It does not alter factual/freshness, Entity/Identity, sentiment neutrality / loser-respect, semantic QA, visual-quality, Human Visual Review, Final Presentation / Brand / Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine-Golden byte identity, publication-readiness, or external publication authority.

## Exact code-and-test commit

`746efeb7770248bec480e9526c05382bb0463c1d`

CI status is recorded separately in `PHASE18_IMPLEMENTATION_LOG_381.md`; no success is claimed until the exact code-and-test SHA completes the required Phase 18 verification.