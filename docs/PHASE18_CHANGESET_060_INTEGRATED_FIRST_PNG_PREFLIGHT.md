# PUL7SAR Phase 18 — Change Set 060

## Integrated fail-closed first-PNG preflight

### Objective
Make the existing one-command Golden Visual smoke path truthful end-to-end after Change Sets 058–059. The command must no longer assume that host qualification and model-cache preparation happened separately.

### Modified
- `tools/phase18_first_png.py`
  - Adds explicit GPU-host qualification before any model download or durable queue mutation.
  - Adds exact FLUX.2 Klein cache preflight/prefetch before model-specific readiness.
  - Persists host-qualification and model-cache receipt paths in the returned evidence payload.
  - Requires host `eligible=true`.
  - Requires cache `ready=true` and `$0-local` cost mode.
  - Adds configurable `--minimum-free-gib` with a positive-value guard; default remains 30 GiB.
  - Keeps CUDA/FLUX/BF16 readiness after host/cache preflights and before queue creation.
  - Keeps `publication_ready=false` even when a genuine PNG succeeds.

### Added
- `tests/test_phase18_first_png_preflight.py`
  - Proves ordering: host qualification -> model cache -> Golden readiness -> queue mutation.
  - Proves a non-eligible host fails closed.
  - Proves nonzero host qualification is treated as terminal preflight failure.
  - Proves model cache must be ready and remain `$0-local`.
  - Proves configured disk headroom is forwarded to the cache preflight.
  - Proves relative evidence paths remain scoped under the repository root.

### Deleted
None.

### Security and editorial invariants
No factual, identity, sentiment, neutrality, semantic-publication, or Golden Visual quality rule is changed. No prompt, seed, canvas, provider ID, model ID, or candidate payload is changed. No paid image provider/API is introduced. No placeholder or synthetic proof file is created.

### Why this materially reduces the remaining gap
Before Change Set 060, `phase18_first_png.py` could be called directly while the newer Change Set 058 model-cache and Change Set 059 host-qualification steps were only guaranteed by the dedicated GitHub GPU workflow/runbook. That meant the supposed one-command path was no longer fully self-contained.

After Change Set 060 the direct command itself owns the complete prerequisite chain:

`Golden batch integrity -> GPU host qualification -> approved model cache/prefetch -> FLUX/BF16 readiness -> durable queue -> GPU worker -> genuine PNG`

An incompatible host fails before downloading model weights. A compatible but uncached host can prepare the exact approved open-weight model automatically. The durable queue is not mutated until all hardware/cache/runtime prerequisites are proven.

### Remaining external blocker
A genuine PNG still requires a real NVIDIA CUDA host that passes the BF16/VRAM qualification and executes the locked FLUX.2 Klein handoff. CPU CI must not claim image generation.
