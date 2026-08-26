# PUL7SAR Phase 18 — Change Set 169

## Lease-Bound Host Memory Guard

### Goal

Reduce the remaining failure window before the first genuine Golden Candidate 1 PNG without weakening any editorial, factual, identity, zero-cost, semantic, or visual-quality gate.

Change Sets 166–168 proved host RAM before model work and established a canonical host-memory-locked workflow. Change Sets 155–156 also requalified live GPU VRAM at worker cycle and post-lease execution boundaries. One resource gap remained: live system RAM could drop after the early host-memory preflight but before a leased Candidate 1 entered FLUX execution, which is relevant because sequential CPU offload depends on currently available host memory.

### Changes

Added `engine/intelligence/worker_host_memory_guard.py`.

- Reuses the existing fail-closed `HostMemoryQualificationProbe`.
- Re-measures Linux `MemAvailable` at worker boundaries.
- Preserves the existing 10 GiB first-Golden available-RAM floor.
- Refuses execution when host RAM is unproven or below the floor.
- Is explicitly non-authorizing: it cannot mutate the queue, authorize generation, or mark publication ready.

Modified `tools/phase18_gpu_worker.py`.

- Initial worker readiness now requalifies both live GPU state and live host RAM before the generation store is created.
- Every worker cycle requalifies both resources before expired-lease recovery or new leasing can mutate durable queue state.
- The lease-bound `pre_execute_guard` now repeats both GPU and host-memory checks after a concrete job is leased and immediately before `RUNNING` / FLUX execution.
- Host-memory values are recorded in worker readiness output, heartbeat metadata, generation samples, and cycle output for diagnosis.
- A guard failure still uses the existing lease-bound requeue path: the job never enters `RUNNING`, the FLUX executor is not called, and no generation attempt is consumed.

Added `tests/test_phase18_worker_host_memory_guard.py`.

- Proves non-authorizing receipts.
- Rejects a live RAM drop below the floor.
- Rejects unproven `MemAvailable`.
- Verifies combined GPU + RAM requalification occurs before store creation.
- Verifies the lease-bound guard rechecks both resources.
- Verifies cycle-level requalification occurs before recovery/lease execution.

### Safety properties preserved

No changes were made to:

- Fact Lock or source integrity;
- entity / identity verification;
- sentiment, neutrality, or loser-respect rules;
- `$0-local` execution policy;
- pinned FLUX.2 Klein and Qwen revisions;
- native BF16 requirement;
- Candidate/request/seed/canvas/SHA locks;
- generated text, platform branding, exact facts, entity marks, or sport-geometry exclusion;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` semantic gates;
- deterministic football geometry and artifact integrity;
- provenance/evidence replay;
- Golden minimum 8.5 / elite 9.0+ thresholds;
- exact brand / typography integrity;
- `SemanticPublicationGate` or final publication readiness.

No file was deleted. `main` and `main.py` were not modified.

### First genuine Golden PNG status

No PNG was fabricated or claimed. The remaining execution blocker is still external: a real host must prove NVIDIA CUDA, native BF16, sufficient total/live-free GPU VRAM, sufficient live system RAM, safe local offload/runtime support, pinned FLUX/Qwen revisions, and `$0-local` execution before Candidate 1 can run.
