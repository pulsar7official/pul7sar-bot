# PUL7SAR Phase 18 — Change Set 057

## Self-hosted GPU Golden smoke workflow

### Goal
Reduce the remaining distance to the first genuine Golden Visual PNG without weakening the `$0-local` development policy or requiring a human to reconstruct the Phase 18 command sequence on a GPU host.

### Added

#### `.github/workflows/phase18-gpu-smoke.yml`
A manual GitHub Actions workflow for an explicitly labelled **self-hosted** PUL7SAR CUDA/BF16 runner.

The workflow deliberately does **not** select a GitHub-hosted GPU runner and does not contain any paid image-provider integration. It requires these runner labels:

`self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18`

It then:

1. requires the exact confirmation token `RUN_PHASE18_GOLDEN_GPU`,
2. checks out `phase18/story-intelligence` explicitly,
3. proves CUDA-enabled PyTorch already exists instead of replacing the host's CUDA build,
4. installs only `requirements-phase18-gpu.txt`, which intentionally excludes PyTorch,
5. runs the existing model-specific readiness gate and requires `golden_generation_ready=true`,
6. requires the BF16 Golden path,
7. invokes the already locked `tools/phase18_first_png.py` path,
8. verifies that the returned artifact is a real PNG by path, extension and PNG signature,
9. asserts that raw generation success did **not** self-authorize publication,
10. uploads generation, proof, queue, handoff and worker-telemetry evidence as a GitHub artifact.

The workflow uses a concurrency lock so two Golden smoke generations cannot accidentally compete on the same attached runner through this workflow.

#### `tests/test_phase18_gpu_smoke_workflow.py`
Regression coverage verifies that the workflow:

- remains manual (`workflow_dispatch`) rather than firing on production pushes,
- checks out only the Phase 18 development branch,
- requires self-hosted CUDA/BF16 labels,
- does not select common GitHub-hosted CPU runners,
- does not install PyTorch automatically,
- uses the existing locked first-PNG command,
- preserves `$0-local`,
- uploads real evidence,
- embeds no paid-provider/API-key path.

### Why this materially reduces the remaining gap
Before this change, a compatible GPU host still needed manual repository preparation and manual command execution. After Change Set 057, attaching a compatible self-hosted runner with the required labels makes the first genuine PNG a controlled GitHub workflow execution using the exact same Phase 18 generation contracts already tested in CPU CI.

This does **not** pretend that a GPU exists today. The workflow will remain queued if no matching self-hosted runner is attached. No PNG is claimed until that runner executes FLUX.2 Klein successfully.

### Safety invariants preserved

- `main` is not modified.
- `main.py` is not imported or invoked by the GPU smoke workflow.
- The workflow checks out `phase18/story-intelligence` explicitly.
- Fact Lock, identity verification, sentiment, neutrality and Generation Authorization remain upstream requirements.
- Handoff SHA-256, provider/model/seed/canvas locks remain unchanged.
- CUDA/BF16 requirements fail closed.
- No FP16 fallback is introduced.
- No paid provider or production secret is added.
- A real generated PNG remains `publication_ready=false` until semantic verification and the strict Golden quality gate approve it.
- No placeholder image, fake benchmark or synthetic success sample is created.

### Remaining external blocker
The repository still does not possess compute by itself. A compatible NVIDIA CUDA host with proven BF16 support and sufficient VRAM must be attached as a self-hosted GitHub Actions runner (or the same worker path must be executed on an equivalent host). Only then can the locked FLUX.2 Klein handoff produce the first genuine PNG.

### Next engineering step after first GPU execution
Use the uploaded artifact and telemetry to determine real latency/VRAM, inspect candidate 1, and either approve it or execute the remaining deterministic candidate seeds. Only observed GPU results may drive throughput and capacity decisions.
