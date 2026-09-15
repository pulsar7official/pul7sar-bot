# PUL7SAR Phase 18 Implementation Log — Change Set 170

## Branch state reviewed first

Repository: `pulsar7official/pul7sar-bot`

Target branch: `phase18/story-intelligence`

Starting branch head observed for this run: `ea759573eb0d3dbe475fc8e7b8915519bf8f1fe2`

Observed `main` head: `b6d89bdd10f2c14d373fccb4a5e0fc87ca349b8e`

GitHub compare state before this change set: `diverged`; Phase 18 was 1477 commits ahead and 166 commits behind `main`.

No write, merge, force-update, or direct modification was made to `main` or `main.py`.

## CI state found during review

`Phase 18 Story Intelligence Verification` run `32955328471` completed with `failure` on the starting head.

All returned companion visual-study workflows on that same head completed successfully, including Data Monument, Verified Match Result, Premium Hybrid Result, Tactical Intelligence, Adaptive Brand Pixel, Result Statement, Event Hybrid Context, Composition Matrix, and Event Editorial.

The Story Intelligence failure occurred during `Syntax and discover validation` after 1208 Phase 18 tests had been discovered.

Exactly three failures were attributable to stale source-text assertions in `tests/test_phase18_gpu_worker_live_requalification.py`:

1. an initial-order assertion still searched for `initial_live_host = _requalify_live_host(capabilities)`;
2. a cycle-order assertion still searched for `_requalify_live_host(capabilities)`;
3. a lease-bound assertion still required `_requalify_live_host(capabilities)` inside `GenerationWorkerService` setup.

The production worker had already been intentionally strengthened by Change Set 169 to use `_requalify_execution_host(capabilities)`, which combines live GPU requalification with live host-memory requalification. The newer `test_phase18_worker_host_memory_guard.py` tests for that combined behavior were passing in the same CI run.

## Gap identified

The CI suite contained a regression mismatch: production code implemented the stronger combined GPU + system-RAM execution guard, while an older GPU-only source-order test still encoded the retired helper name.

Leaving this unresolved would keep Phase 18 Story Intelligence red and obscure real regressions before the first compatible GPU host becomes available.

## Code changes

### Modified

`tests/test_phase18_gpu_worker_live_requalification.py`

- Initial resource-order assertion now requires `initial_execution_host = _requalify_execution_host(capabilities)` before `FilesystemGenerationJobStore` construction.
- Cycle-order assertion now requires `_requalify_execution_host(capabilities)` before expired-lease recovery and `service.run_once()`.
- Lease-bound assertion now requires the combined execution-host guard in `pre_execute_guard`.
- Focused unit tests for `_requalify_live_host()` remain unchanged, preserving independent GPU-policy coverage.

### Added

`docs/PHASE18_CHANGESET_170_GPU_REQUALIFICATION_REGRESSION_ALIGNMENT.md`

`docs/PHASE18_IMPLEMENTATION_LOG_170.md`

### Deleted

Nothing.

## Gates preserved

No factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gate was relaxed.

Still fail-closed:

- factual/source integrity;
- entity and identity verification;
- sentiment/neutrality and loser-respect rules;
- `$0-local` execution;
- pinned FLUX.2 Klein and Qwen revisions;
- native BF16 requirement;
- total/live-free GPU VRAM qualification;
- safe local offload qualification;
- host-memory qualification;
- cycle-level and lease-bound GPU + host-RAM requalification;
- Candidate/request/seed/canvas/SHA locks;
- generated text/platform branding/exact facts/entity marks/sport geometry exclusion;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` verification;
- deterministic football geometry and artifact integrity;
- provenance/evidence replay;
- Golden minimum 8.5 and elite 9.0+ thresholds;
- exact brand and typography integrity;
- `SemanticPublicationGate` and final publication readiness.

## Testing status for this change set

The regression fix was committed first as `9f02b501970413efb83ba8363bce0033facf76a7`, followed by documentation commits on `phase18/story-intelligence`.

The branch is expected to trigger the Phase 18 CPU workflows again. This log intentionally does not mark Change Set 170 CI-green until a real `Phase 18 Story Intelligence Verification` run for the updated head completes successfully.

## First genuine Golden PNG status

No Golden PNG was generated or claimed.

Exact remaining execution blocker: the current tool environment does not expose a real host proving all required first-Golden conditions simultaneously:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free GPU VRAM;
- safe local Diffusers offload/runtime support;
- sufficient live system RAM at execution boundaries;
- pinned FLUX/Qwen revisions;
- stable runtime fingerprint;
- `$0-local` execution.

Without that host, Candidate 1 cannot be executed honestly. No fake PNG, visual score, or benchmark was produced.

## Immediate next work

1. Confirm Story Intelligence CI for Change Set 170.
2. If green, keep Candidate 1 as the only authorized Golden seed.
3. When a compatible GPU host is available, execute Candidate 1 through the existing resource guards and provenance path.
4. Do not authorize Seeds 2–4 until Candidate 1 passes provenance, `BASE_SCENE`, deterministic football Hybrid integrity, `HYBRID_SURFACE`, sealed human review, and Golden quality review.
