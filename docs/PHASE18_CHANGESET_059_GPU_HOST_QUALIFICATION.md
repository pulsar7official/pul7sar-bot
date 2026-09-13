# PUL7SAR Phase 18 — Change Set 059: Fail-Closed GPU Host Qualification

## Goal
Reduce the remaining gap to the first genuine Golden Visual PNG by making host suitability explicit before any queue mutation, model download, or GPU generation attempt.

## Added
- `engine/intelligence/gpu_host_qualification.py`
  - Converts already-observed runtime facts into a deterministic Golden-host qualification receipt.
  - Requires `local_cuda` runtime kind.
  - Requires CUDA-enabled PyTorch and CUDA availability.
  - Requires a proven GPU identity.
  - Requires VRAM at or above the selected model's declared floor (13 GB for FLUX.2 Klein 4B).
  - Requires native BF16 support to be explicitly proven.
  - Requires CUDA compute capability to be observable.
  - Preserves `$0-local` as the only cost mode.
- `tools/phase18_qualify_gpu_host.py`
  - Read-only qualification command.
  - Installs nothing, downloads nothing, calls no paid API, and does not touch the generation queue.
  - Can persist a machine-readable JSON receipt.
  - Returns exit code `0` only for a fully qualified host and `2` otherwise.
- `tests/test_phase18_gpu_host_qualification.py`
  - Covers a valid 24 GB BF16 CUDA host.
  - Rejects insufficient VRAM.
  - Rejects unknown BF16 support.
  - Rejects missing compute capability evidence.
  - Rejects CPU-only hosts.

## Safety properties
This change does not weaken or bypass any Phase 18 gate. It does not alter prompt content, locked facts, identity references, sentiment, neutrality, semantic verification, Golden scoring, candidate seeds, model ID, provider ID, or output geometry.

A qualification receipt proves only that the host hardware observation satisfies the current Golden execution policy. It does **not** prove that model weights are cached, Diffusers is compatible, generation will succeed, or a generated image is publication-ready. Those remain separate fail-closed checks.

## First-PNG execution order after this change
1. Host qualification receipt.
2. Approved model cache preflight/prefetch.
3. FLUX-specific Diffusers readiness.
4. Golden BF16 readiness.
5. One-command candidate-1 smoke execution.
6. Real PNG registration and runtime/CUDA-memory telemetry.
7. Semantic publication verification.
8. Strict Golden Visual quality review.

## Production isolation
- Branch: `phase18/story-intelligence` only.
- `main`: not modified.
- `main.py`: not modified.
- Telegram production publishing: not modified.
- Legacy image path: not modified.
- No paid image API or production secret introduced.
- No fake PNG or fake throughput sample introduced.

## Remaining external blocker
The repository still cannot truthfully claim the first genuine PNG until a real NVIDIA CUDA host with enough VRAM and proven BF16 support executes the locked FLUX.2 Klein handoff. This change makes that host qualification observable and machine-verifiable before GPU time is spent.
