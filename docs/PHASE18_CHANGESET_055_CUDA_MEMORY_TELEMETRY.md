# PUL7SAR Phase 18 — Change Set 055

## CUDA high-water memory and executor timing telemetry

### Goal
Make the first genuine Golden Visual GPU run produce operational evidence in the same machine-readable result as the PNG, so production sizing is based on observed CUDA behavior rather than guesses.

### Added
- `engine/intelligence/cuda_memory.py`
  - Optional PyTorch CUDA peak-memory tracker.
  - Resets peak counters before the FLUX model execution boundary when CUDA exposes the API.
  - Captures peak/current allocated and reserved GPU memory in GiB.
  - Returns an explicit unavailable state instead of fabricating measurements when CUDA/torch counters cannot be read.
- `tests/test_phase18_cuda_memory.py`
  - Covers reset/capture, CUDA unavailable behavior, and counter failure behavior without requiring a GPU in CI.

### Modified
- `tools/phase18_flux2_execute.py`
  - Starts timing immediately before the concrete Diffusers backend/pipeline execution boundary.
  - Records UTC start/finish timestamps and monotonic elapsed seconds.
  - Resets CUDA peak counters before model construction/generation.
  - Captures CUDA high-water and current memory counters after real proof registration.
  - Persists all telemetry in the existing dedicated `--result` JSON channel.

### New real-result fields
- `execution_started_at`
- `execution_finished_at`
- `execution_seconds`
- `cuda_memory_available`
- `cuda_peak_counters_reset`
- `cuda_device_index`
- `cuda_peak_allocated_gb`
- `cuda_peak_reserved_gb`
- `cuda_current_allocated_gb`
- `cuda_current_reserved_gb`
- `cuda_memory_blocker`

### Safety invariants
- No change to prompt, seed, model, provider, canvas, identity or factual locks.
- No FP16 or other precision fallback; Golden execution remains BF16-only.
- Missing CUDA telemetry does not become a fake zero value.
- Telemetry does not make an image publication-ready; semantic and Golden gates remain independent.
- No paid provider/API is introduced.
- `main` and all production publication paths remain untouched.

### Why this materially reduces the production gap
The first real candidate will now yield, in one execution, the PNG plus observed latency, GPU identity/VRAM, BF16 evidence and actual CUDA high-water memory. This lets PUL7SAR size worker concurrency and images/hour from measured evidence and identify whether VRAM rather than inference latency is the limiting production resource.

### Remaining blocker
A genuine PNG still requires a compatible CUDA GPU with native BF16 support and a Diffusers build exposing `Flux2KleinPipeline`. CPU CI deliberately does not claim this proof.
