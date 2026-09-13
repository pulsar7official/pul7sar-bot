# PUL7SAR Phase 18 — Implementation Log 156

## Scope

Branch: `phase18/story-intelligence` only.

`main` / `main.py`: not modified, merged, force-updated, or used as a write target.

## Change Set 156 — Lease-Bound GPU Execution Guard

### Why this change was needed

Change Set 155 moved live GPU requalification to the worker boundary before queue recovery and leasing. That eliminated stale early-preflight assumptions but still left a narrow TOCTOU window between lease acquisition and the actual executor call. Because VRAM is not reserved by qualification, another process could consume memory after the cycle check but before FLUX starts.

### Added

- `LeaseBoundPreExecutionGuard` protocol in `engine/intelligence/generation_worker.py`.
- Optional `pre_execute_guard` on `GenerationWorkerService`.
- A fail-closed guard-failure path that records `pre_execute_guard_blocked`, never calls the executor, never transitions to `RUNNING`, consumes no generation attempt, and returns the job to `QUEUED` with lease fields cleared.
- Lease-bound `_requalify_live_host()` wiring in `tools/phase18_gpu_worker.py` so the actual PUL7SAR GPU worker re-proves physical runtime state after lease and immediately before FLUX execution.
- Telemetry/ready payload indicators that the lease-bound guard is active.
- Regression coverage proving ordering and no-attempt-consumption semantics.
- Documentation: `docs/PHASE18_CHANGESET_156_LEASE_BOUND_GPU_EXECUTION_GUARD.md`.

### Modified

- `engine/intelligence/generation_worker.py`
- `tools/phase18_gpu_worker.py`
- `tests/test_phase18_generation_worker.py`
- `tests/test_phase18_gpu_worker_live_requalification.py`

### Deleted

None.

## Preserved contracts and gates

No change was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B model lock;
- native BF16 requirement;
- Candidate/request/seed/canvas/SHA locks;
- generated text / platform branding / exact facts / entity marks / sport geometry prohibitions;
- Qwen BASE_SCENE and HYBRID_SURFACE inspection;
- deterministic football geometry ownership;
- generation provenance and evidence replay;
- Golden visual-quality thresholds (8.5 minimum, 9.0+ elite);
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate / final publication readiness.

The new guard has no publication authority and cannot lower precision, change model/provider identity, or fabricate GPU evidence.

## Tests

New/expanded regression coverage checks:

- the pre-execution guard receives a leased job before the job enters `RUNNING`;
- the executor has not run when the guard executes;
- a guard failure persists a `RETRYABLE_FAILED` audit record and requeues the job;
- a guard failure consumes zero generation attempts;
- the concrete GPU worker binds `_requalify_live_host()` as the lease-bound guard while retaining the earlier cycle-level requalification.

GitHub Actions status for the final Change Set 156 head must be reported only after an actual workflow result is available; no CI success is inferred or fabricated.

## Remaining gap to first genuine Golden Visual PNG

The software path is prepared further, but actual Candidate 1 generation still requires a compatible physical NVIDIA CUDA host with native BF16 and enough live free VRAM for FLUX.2 Klein 4B, followed by Qwen semantic inspection. No fake PNG, benchmark, paid provider fallback, precision downgrade, or publication bypass was introduced.

Current intended path:

`immutable Phase 18 source → repository/runtime/cache/Qwen checks → Original Scene admission → Candidate 1 lease → lease-bound live GPU requalification → genuine FLUX PNG → provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed human review → Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate`

Seeds 2–4 remain unauthorized until Candidate 1 exists genuinely and passes the required visual review gates.
