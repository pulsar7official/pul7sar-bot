# PUL7SAR Phase 18 — Change Set 056

## One-command first genuine Golden PNG path

### Goal
Reduce the remaining operational gap between the verified Phase 18 architecture and the first real FLUX.2 Klein PNG. The prior path required separate batch-build, integrity-verification, readiness, enqueue, and worker commands. Change Set 056 composes those already-trusted boundaries into one fail-closed command without adding a second generation implementation.

### Added

#### `engine/intelligence/golden_smoke.py`
Defines the first-PNG smoke coordinator contract.

It:
- accepts only `pul7sar-golden-batch-v1`;
- requires `$0-local` at both manifest and handoff levels;
- selects candidate 1 explicitly;
- cross-checks candidate request ID, seed, model ID, handoff path and payload SHA-256;
- creates exactly one durable smoke job by default: `golden-smoke-candidate-01`;
- safely reuses an existing job only when all locked identity fields still match;
- refuses to silently reset a `terminal_failed` job.

This module does not generate images and cannot bypass the existing GPU worker or FLUX executor.

#### `tools/phase18_first_png.py`
Adds a single operational entry point for a compatible GPU host.

Execution order:
1. Build the deterministic Golden batch only when its manifest is absent.
2. Verify the complete batch through the existing integrity verifier.
3. Run the existing local readiness command and require `golden_generation_ready=true`.
4. Only after readiness succeeds, create/reuse the durable candidate-1 smoke job.
5. Execute exactly one cycle through the existing `phase18_gpu_worker.py`.
6. Re-read durable job state and require `succeeded`.
7. Require the result path to be an existing `.png` file.
8. Report the PNG as a real generation proof while explicitly keeping `publication_ready=false` until semantic and Golden-quality gates run.

Critical ordering rule: an incompatible CPU/non-BF16 host fails before the durable queue is mutated.

Example on a compatible host:

```bash
PYTHONPATH=. python tools/phase18_first_png.py
```

No Colab-specific path is required by the command. It can run on any host satisfying the existing CUDA, VRAM, Diffusers/`Flux2KleinPipeline`, and BF16 readiness contracts.

#### `tests/test_phase18_golden_smoke.py`
Regression coverage for:
- locked candidate-1 identity;
- manifest SHA drift rejection;
- non-`$0-local` manifest rejection;
- exactly-one durable smoke job semantics;
- refusal to reuse a job with changed locked identity;
- refusal to silently requeue a terminal failure;
- explicit status payload identity.

### Existing gates preserved
- Fact Lock: unchanged.
- Identity verification: unchanged.
- Sentiment/neutrality: unchanged.
- Generation authorization: unchanged.
- `$0-local` policy: required explicitly.
- SHA-256 handoff integrity: required before job preparation.
- CUDA/BF16 readiness: required before queue mutation.
- FLUX.2 Klein provider/model lock: unchanged.
- Semantic publication gate: still mandatory after generation.
- Golden Visual 8.5/9.0 quality gate: still mandatory after generation.
- `main.py`: untouched.
- Telegram production path: untouched.

### Why this matters
Before Change Set 056, the first real PNG required an operator to execute a sequence of separate commands correctly. That is useful for debugging but is not the final operational shape of an automated image pipeline. This change reduces the smoke proof to one command while retaining the same internal durable queue and worker architecture intended for later unattended service operation.

The command is deliberately not described as publication automation. Its only success condition is a genuine locked PNG. Publication remains downstream of semantic verification and strict visual-quality approval.

### Current blocker
The repository still cannot truthfully claim a PNG until this command is executed on a compatible CUDA/BF16 GPU host with the required FLUX.2 Klein model runtime. CPU GitHub CI can verify orchestration and safety contracts but cannot produce the image.
