# PUL7SAR Phase 18 — Implementation Log 155

## Branch / isolation state reviewed first

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Branch HEAD at review start: `bbbf2afd3a8611cac93ff25d40c2cb52935c36d7`
- `main` HEAD observed during this run: `10e4ead8e1fcf82e76924f28c45472aa07b228c8`
- Comparison: `diverged`
- Phase 18 ahead of `main`: 1380 commits
- Phase 18 behind `main`: 143 commits
- Merge base: `386529f2352c9c6d9a099ac817b9b73077545240`
- `main` / `main.py` were not modified, merged, force-updated, or used as a write target.

## Starting verification state

The pre-existing Phase 18 HEAD was fully green before Change Set 155:

- Phase 18 Story Intelligence Verification: run `32886327221`, run number `2699`, `success`
- Composition Matrix: `success`
- Data Monument: `success`
- Result Statement: `success`
- Adaptive Brand Pixel Verification: `success`
- Tactical Intelligence: `success`
- Event Hybrid Context: `success`
- Premium Hybrid Result: `success`
- Verified Match Result: `success`
- Event Editorial: `success`

This confirms Change Set 154 and its live free-VRAM host qualification were already accepted by CPU CI before the current work began.

## Change Set 155 — Worker-Bound Live GPU Requalification

### Why this was needed

Change Set 154 moved live free-VRAM qualification earlier, before expensive model work. A remaining TOCTOU gap still existed: the GPU could become busy, free VRAM could fall, or the visible device could change after early preflight but before the durable worker recovered or leased Candidate 1.

### Added

- `tests/test_phase18_gpu_worker_live_requalification.py`
- `docs/PHASE18_CHANGESET_155_WORKER_LIVE_GPU_REQUALIFICATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_155.md`

### Modified

- `tools/phase18_gpu_worker.py`

### Deleted

- Nothing.

### Runtime behavior added

The GPU worker now re-runs the same `GpuHostQualificationPolicy` at the worker boundary:

1. after normal readiness/capability construction and before the generation store is constructed; and
2. before every worker cycle, prior to expired-job recovery and `GenerationWorkerService.run_once()`.

The worker refuses to touch queue state if the current host can no longer prove:

- CUDA/local-CUDA runtime;
- sufficient total VRAM;
- sufficient **live free VRAM** for FLUX.2 Klein 4B;
- native BF16;
- CUDA compute capability;
- the same GPU identity observed during initial readiness; and
- `$0-local` cost mode.

The requalification receipt is deliberately non-authorizing: it cannot mutate the queue, authorize generation, approve semantic/Golden quality, or mark publication ready.

### Telemetry added

Worker ready/cycle telemetry now carries:

- `live_free_vram_gb` / `live_free_vram_gb_before_cycle`
- `required_vram_gb`
- proof that live host requalification occurred before queue mutation

This makes a future first genuine PNG failure more diagnosable without treating telemetry as publication authority.

## Gates preserved

No relaxation was made to:

- Fact Lock
- Entity / Identity Verification
- Sentiment / Neutrality
- `$0-local`
- FLUX.2 Klein 4B model lock
- native BF16
- Candidate / request / seed / canvas / SHA locks
- generated text / branding / exact facts / entity marks / sport-geometry prohibitions
- Qwen BASE_SCENE and HYBRID_SURFACE verification
- deterministic football geometry
- provenance / evidence replay
- Golden 8.5 minimum / 9.0+ elite thresholds
- Exact Brand Integrity
- Typography Integrity
- SemanticPublicationGate

Seeds 2–4 remain unauthorized before Candidate 1 is generated and accepted visually.

## Test status for Change Set 155

New regression tests were added, but the new commit had not yet existed when this log entry was prepared. GitHub Actions must be observed on the committed head before Change Set 155 is described as CI-green.

## Exact remaining blocker

No genuine new Golden Hybrid v5 PNG was fabricated in this run. The remaining external blocker is a real host that simultaneously proves:

- NVIDIA CUDA
- native BF16
- total VRAM at/above the current FLUX.2 Klein 4B requirement
- **live free VRAM** at/above that requirement immediately before the worker touches Candidate 1
- working exact Qwen runtime/model path

When such a host exists, the current canonical path remains:

`immutable Phase 18 source -> repository integrity -> runtime repair -> early host qualification -> shared cache budget -> Qwen readiness -> Original Scene admission -> Candidate 1 -> worker-bound live host requalification -> genuine PNG -> provenance replay -> BASE_SCENE ownership QA -> deterministic football Hybrid -> HYBRID_SURFACE QA -> sealed human review -> Golden 8.5/9.0 -> exact brand/typography -> SemanticPublicationGate`
