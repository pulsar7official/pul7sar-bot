# Phase 18 Change Set 155 — Worker-Bound Live GPU Requalification

## Objective

Close the remaining time-of-check/time-of-use gap between early GPU host qualification and the exact moment the durable GPU worker is allowed to recover, lease, or execute queued Golden generation work.

## Problem

Change Set 154 added live free-VRAM qualification before model preparation. That materially reduced late GPU failures, but the qualification receipt was still only an earlier observation. During Qwen/FLUX cache preparation, notebook activity, or another process could consume VRAM or change the visible GPU before the worker touched the queue.

A compatible host at preflight time is not equivalent to a reserved GPU at execution time.

## Implementation

`tools/phase18_gpu_worker.py` now re-runs `GpuHostQualificationPolicy`:

1. immediately after the normal worker capability build and before the generation store is created; and
2. at the start of every worker cycle, before expired-job recovery, leasing, or execution can mutate durable queue state.

The late requalification proves again:

- `local_cuda` runtime;
- CUDA-enabled PyTorch;
- exact FLUX.2 Klein 4B minimum VRAM policy;
- live free VRAM at or above the current model requirement;
- native BF16 support;
- CUDA compute capability;
- the same GPU identity observed during initial worker readiness; and
- `$0-local` cost mode.

The requalification step itself is explicitly non-authorizing:

- it does not mutate the queue;
- it does not authorize generation;
- it does not authorize publication.

Worker heartbeat/performance telemetry now records the live free VRAM observed immediately before the cycle and the required VRAM threshold.

## Tests

Added `tests/test_phase18_gpu_worker_live_requalification.py` covering:

- a valid live requalification receipt;
- rejection when live free VRAM is no longer sufficient;
- rejection when the visible GPU identity changes;
- source-order proof that live requalification precedes queue recovery and `service.run_once()`; and
- source-order proof that initial requalification occurs before generation-store construction.

## Files changed

### Modified

- `tools/phase18_gpu_worker.py`

### Added

- `tests/test_phase18_gpu_worker_live_requalification.py`
- `docs/PHASE18_CHANGESET_155_WORKER_LIVE_GPU_REQUALIFICATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_155.md`

### Deleted

- None.

## Gates preserved

No factual, identity, sentiment/neutrality, zero-cost, semantic-publication, or Golden visual-quality gate was relaxed. FLUX.2 Klein 4B, native BF16, Candidate 1, seed/canvas/SHA locks, Qwen BASE_SCENE/HYBRID_SURFACE, deterministic football geometry, Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand Integrity, Typography Integrity, and SemanticPublicationGate remain unchanged.

## Remaining blocker

This change does not fabricate a GPU result. The first genuine Golden Hybrid v5 Candidate 1 still requires a real NVIDIA CUDA host with native BF16 and enough live free VRAM to run FLUX.2 Klein 4B and the existing Qwen verification path.
