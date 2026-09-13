# PUL7SAR Phase 18 — Change Set 164

## Low-VRAM Sequential Offload Lock

### Purpose

Reduce the remaining risk between a qualified CUDA host and the first genuine Golden Hybrid v5 PNG without changing the locked model, BF16 precision, seed, canvas, prompt, factual gates, semantic gates, or visual-quality gates.

A previously proven T4-class host (~14.6 GiB VRAM) can still OOM inside FLUX.2 attention when the runtime falls back to model-level CPU offload. The current FLUX wrapper already prefers sequential CPU offload, but if that method is missing it previously allowed a model-offload fallback. On a T4-class host this is an unsafe fallback because it can consume the scarce Candidate 1 opportunity without producing a PNG.

### Change

`engine/intelligence/flux2_klein_diffusers.py` now treats model-level CPU offload as a high-memory-only path:

- Sequential CPU offload remains the preferred default.
- A model-level offload path requires measurable physical CUDA VRAM.
- Model-level offload is rejected when total physical CUDA VRAM is `<= 16 GiB` by default.
- Unknown CUDA VRAM fails closed instead of being treated as a high-memory host.
- Disabling the sequential preference cannot bypass the VRAM safety gate.
- The threshold is part of `Flux2KleinInferenceConfig` and must remain positive.

No image-quality parameter is reduced. The following remain unchanged:

- `black-forest-labs/FLUX.2-klein-4B`;
- immutable approved FLUX revision;
- native BF16;
- 4 inference steps;
- guidance scale 1.0;
- locked Candidate 1 seed/canvas/prompt/provenance;
- `$0-local`;
- Qwen semantic gates;
- deterministic football geometry;
- Golden 8.5 minimum / 9.0+ elite thresholds.

### Regression coverage

`tests/test_phase18_flux2_klein_diffusers.py` now proves:

1. sequential CPU offload is still preferred when available;
2. model offload is allowed only on a measured high-memory host;
3. a T4-class 14.6-GiB host cannot fall back to model offload;
4. unknown VRAM cannot fall back to model offload;
5. `prefer_sequential_cpu_offload=False` cannot be used as a low-VRAM bypass;
6. invalid offload safety thresholds fail closed.

### Files

Added:

- `docs/PHASE18_CHANGESET_164_LOW_VRAM_SEQUENTIAL_OFFLOAD_LOCK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_164.md`

Modified:

- `engine/intelligence/flux2_klein_diffusers.py`
- `tests/test_phase18_flux2_klein_diffusers.py`

Deleted: none.

`main` / `main.py`: not modified.

### Golden PNG status

This change does not fabricate a GPU result. A genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA host with native BF16 and sufficient live free VRAM. This change materially reduces the chance that a low-VRAM host passes all earlier checks only to enter a known-unsafe model-offload fallback immediately before FLUX inference.
