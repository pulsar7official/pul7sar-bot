# PUL7SAR Phase 18 — Change Set 170

## GPU Requalification Regression Alignment

### Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

`main` and `main.py` are not modified by this change set.

### Problem found

Change Set 169 strengthened the GPU worker by replacing GPU-only queue-bound checks with a combined execution-host guard:

- live CUDA / native BF16 / GPU identity / live free VRAM; and
- live system RAM required by sequential CPU offload.

The production worker was already using `_requalify_execution_host(capabilities)` at all three protected boundaries, but an older regression-test module still searched source text for the retired GPU-only call `_requalify_live_host(capabilities)`.

As a result, `Phase 18 Story Intelligence Verification` run `32955328471` failed during CPU discover validation even though the new combined worker-host-memory tests passed and the production worker itself contained the intended stronger guard.

### Change

Modified `tests/test_phase18_gpu_worker_live_requalification.py` only.

The source-order regression assertions now track the current combined guard:

- initial guard: `initial_execution_host = _requalify_execution_host(capabilities)` before `FilesystemGenerationJobStore` construction;
- cycle guard: `_requalify_execution_host(capabilities)` before `store.recover_expired` and `service.run_once`;
- post-lease guard: `pre_execute_guard=lambda _job: _requalify_execution_host(capabilities)` before transition to `RUNNING` / FLUX execution.

The focused tests for `_requalify_live_host()` remain unchanged, so GPU-only policy behavior is still tested independently while execution-boundary ordering now reflects the stronger combined GPU + host-memory contract.

### Gates preserved

No runtime or policy gate was relaxed or changed.

Still fail-closed:

- factual/source integrity;
- entity/identity verification;
- sentiment/neutrality and loser-respect rules;
- `$0-local` execution;
- pinned FLUX.2 Klein and Qwen revisions;
- native BF16;
- total/live-free VRAM qualification;
- safe offload qualification;
- host-memory qualification;
- lease-bound resource requalification;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact facts/entity marks/sport geometry exclusion;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` inspection;
- deterministic football geometry and artifact integrity;
- provenance/evidence replay;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate and final publication readiness.

### Files

Modified:

- `tests/test_phase18_gpu_worker_live_requalification.py`

Added:

- `docs/PHASE18_CHANGESET_170_GPU_REQUALIFICATION_REGRESSION_ALIGNMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_170.md`

Deleted: none.

### Golden PNG status

No Golden PNG is created or claimed by this change set. This is a CPU-safe CI alignment fix that removes a known regression blocker before the next real Candidate 1 GPU execution.
