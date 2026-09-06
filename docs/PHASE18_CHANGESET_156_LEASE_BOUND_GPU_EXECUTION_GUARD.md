# Phase 18 Change Set 156 — Lease-Bound GPU Execution Guard

## Objective

Close the final time-of-check/time-of-use gap between cycle-level GPU live-memory qualification and the exact moment a leased Candidate job is allowed to transition to `RUNNING` and invoke the locked FLUX executor.

Change Set 155 re-qualified the physical GPU before queue recovery and `run_once()`. That protected durable queue mutation, but a small gap remained: a concrete job could be leased and another process could consume VRAM before the executor actually started. This change adds a second, lease-bound guard directly inside `GenerationWorkerService`.

## Added behavior

- `GenerationWorkerService` now accepts an optional `pre_execute_guard`.
- The guard runs only after a concrete compatible job has been leased and lease ownership has been validated.
- The guard runs before the job transitions to `RUNNING` and before the executor is called.
- `tools/phase18_gpu_worker.py` binds this guard to the existing fail-closed `_requalify_live_host()` policy, so CUDA, native BF16, GPU identity, `$0-local`, total VRAM, and live free VRAM are re-proven at the last safe boundary before FLUX execution.
- Cycle-level live requalification remains in place as defense in depth before recovery/leasing.

## Fail-closed semantics

If the lease-bound guard fails:

1. the executor is not called;
2. the job never enters `RUNNING`;
3. no generation attempt is consumed;
4. an explicit `RETRYABLE_FAILED` record with failure code `pre_execute_guard_blocked` is persisted;
5. the job is returned to `QUEUED` with lease owner/expiry cleared;
6. no semantic, Golden-quality, publication, or cost authority is granted.

This avoids punishing a locked Candidate for transient VRAM pressure that occurred after lease acquisition while preserving a durable audit trail.

## Files modified

- `engine/intelligence/generation_worker.py`
  - added `LeaseBoundPreExecutionGuard` protocol;
  - added optional `pre_execute_guard` dependency;
  - added lease-bound guard execution before `RUNNING`;
  - added explicit no-attempt-consumption requeue path for guard failures.
- `tools/phase18_gpu_worker.py`
  - bound `_requalify_live_host()` as the lease-bound guard;
  - retained cycle-level requalification;
  - exposed guard presence in worker/telemetry payloads.
- `tests/test_phase18_generation_worker.py`
  - proves guard ordering relative to lease, `RUNNING`, and executor;
  - proves guard failure requeues without executor invocation or attempt consumption.
- `tests/test_phase18_gpu_worker_live_requalification.py`
  - proves the concrete GPU worker wires the second live-host check into the leased execution boundary.

## Files added

- `docs/PHASE18_CHANGESET_156_LEASE_BOUND_GPU_EXECUTION_GUARD.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_156.md`

## Deleted

None.

## Production isolation and preserved gates

`main` and `main.py` were not modified. This change does not alter Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local`, FLUX.2 Klein 4B, native BF16, Candidate/request/seed/canvas/SHA locks, forbidden generated text/branding/exact facts/entity marks/sport geometry, Qwen BASE_SCENE/HYBRID_SURFACE, deterministic football geometry, provenance/evidence replay, Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand/Typography Integrity, or SemanticPublicationGate.

## Remaining blocker

A genuine Golden Hybrid v5 Candidate 1 still requires a physical NVIDIA CUDA host with native BF16 and sufficient live free VRAM to run FLUX.2 Klein 4B and subsequent Qwen inspection. No PNG or benchmark is fabricated by this change.
