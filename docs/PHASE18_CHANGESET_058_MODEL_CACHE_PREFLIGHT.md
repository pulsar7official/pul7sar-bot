# PUL7SAR Phase 18 — Change Set 058

## Model-cache preflight before Golden GPU execution

### Objective
Remove a non-GPU failure mode from the first genuine Golden Visual run. A host may have valid CUDA/BF16 hardware yet still waste the smoke window by discovering only during model loading that the approved FLUX.2 Klein snapshot is absent or the cache filesystem cannot hold it.

### Added
- `engine/intelligence/model_cache.py`
  - Immutable model-cache qualification result.
  - Fail-closed disk-headroom policy for uncached model acquisition.
  - Cached complete snapshots remain eligible without demanding fresh-download headroom.
  - Unknown free-space state blocks a required download instead of guessing.
- `tools/phase18_prefetch_flux2.py`
  - Uses only the locked model ID `black-forest-labs/FLUX.2-klein-4B`.
  - Checks local Hugging Face cache first.
  - Requires a conservative 30 GiB free-cache floor before a missing snapshot is downloaded.
  - Downloads/caches weights only; it never generates an image.
  - Validates that the returned snapshot directory exists and contains `model_index.json`.
  - Writes a machine-readable cache receipt with model/provider/license/cost mode, cache path, file count and apparent snapshot size.
- `tests/test_phase18_model_cache.py`
  - Cached-model eligibility.
  - Insufficient-disk rejection.
  - Sufficient-disk acceptance.
  - Unknown-free-space fail-closed behavior.
  - Invalid-input validation.

### Modified
- `requirements-phase18-gpu.txt`
  - Makes `huggingface_hub` an explicit GPU-side dependency rather than relying on a transitive install.
- `.github/workflows/phase18-gpu-smoke.yml`
  - Extends the manual self-hosted smoke timeout to allow first-time open-weight acquisition.
  - Adds a pre-generation model-cache step after GPU dependencies are installed and before Golden readiness/generation.
  - Verifies the receipt remains `$0-local` and points to the exact approved model ID.
  - Preserves the same self-hosted CUDA/BF16 labels, explicit confirmation token and publication gating.

### Deleted
None.

### Safety properties preserved
- `main` is not modified.
- `main.py` and production publishing remain isolated.
- No paid image API or hosted inference provider is introduced.
- No API key or provider secret is embedded.
- The prefetch step cannot alter prompt, seed, canvas, factual claims, identity plan, sentiment, generation package or handoff SHA-256.
- A cached/downloaded model does not imply generation readiness or publication readiness.
- CUDA/BF16 model-specific readiness still runs independently after cache preparation.
- A successful GPU generation still remains `publication_ready=false` until semantic verification and strict Golden review pass.

### Why this materially reduces the first-PNG gap
The first compatible GPU window now spends generation time on model execution instead of discovering storage/download problems after scheduling the runner. Persistent self-hosted hosts can reuse the Hugging Face cache in later runs, so model acquisition is a one-time preparation cost rather than a recurring generation dependency.

### Remaining blocker
A genuine Golden PNG still requires an actual NVIDIA CUDA/BF16 host with sufficient VRAM to execute `Flux2KleinPipeline`. No PNG is claimed by this change set.
