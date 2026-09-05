# PUL7SAR Phase 18 — Change Set 154: Live Free-VRAM Qualification

## Purpose

Strengthen the first genuine Golden Visual GPU preflight so a host is not accepted merely because its GPU has enough *total* VRAM. The live amount of free CUDA memory must also be proven sufficient before Qwen/FLUX model downloads or Candidate 1 execution are allowed.

## Why this reduces the gap to the first genuine PNG

A shared/self-hosted CUDA device can report a 24 GB or larger physical capacity while another process has already consumed most of it. The previous Golden host policy checked total VRAM, native BF16, CUDA identity, and compute capability, but it could still admit a busy device that had less than the model's proven 13 GB runtime floor available at that moment.

That failure would be discovered late, after runtime repair/model-cache work or during model loading. Change Set 154 moves this failure to the earliest hardware gate.

## Runtime changes

### `engine/intelligence/local_runtime.py`

`LocalRuntimeProbe` now attempts `torch.cuda.mem_get_info(device)` and records:

- `gpu_free_vram_gb`
- `gpu_used_vram_gb`

If CUDA memory telemetry is unavailable or throws, the probe records `None`; it does not invent free-memory evidence.

### `engine/intelligence/gpu_host_qualification.py`

`GpuHostQualification` now includes `gpu_free_vram_gb`.

The Golden host policy now requires:

- total VRAM >= the selected model's proven minimum
- **live free VRAM >= the same proven minimum**
- native BF16
- local CUDA runtime
- CUDA-enabled PyTorch
- GPU identity
- compute capability

Missing live free-VRAM evidence fails closed.

### `tools/phase18_qualify_gpu_host.py`

The receipt policy now explicitly declares:

`requires_live_free_vram=true`

The command still downloads nothing, installs nothing, mutates no queue, uses no paid API, and grants no generation/publication authority.

### `tools/phase18_colab_first_golden_bootstrap.py`

The strict first-Golden bootstrap now rejects a host if live free VRAM is missing or below `required_vram_gb` before shared cache budget, Qwen prefetch, FLUX prefetch, or Candidate 1 execution.

The bootstrap receipt is upgraded to:

`pul7sar-first-golden-colab-bootstrap-v4`

and records:

- `gpu_free_vram_gb`
- `required_vram_gb`
- `live_free_vram_proven=true`

### `.github/workflows/phase18-first-golden-review.yml`

The canonical self-hosted first-Golden workflow now replays the v4 bootstrap contract and independently rechecks the live free-VRAM evidence in both the bootstrap receipt and the SHA-bound GPU-host qualification receipt before accepting the sealed Candidate 1 review artifact.

## Regression coverage

Expanded tests now cover:

- CUDA probe records live free/used VRAM when `mem_get_info` succeeds.
- CUDA probe leaves free/used VRAM unproven when memory telemetry fails.
- A physically large but currently busy GPU is rejected.
- Missing live free-VRAM evidence is rejected.
- Bootstrap refuses to continue to model/cache work when free VRAM is insufficient.
- Bootstrap policy must explicitly require live free VRAM.
- Canonical workflow replays live free-VRAM evidence and the v4 bootstrap schema.

## Safety/gates unchanged

This change does not modify or weaken:

- Fact Lock
- Entity/Identity Verification
- Sentiment/Neutrality
- `$0-local`
- FLUX.2 Klein 4B identity
- native BF16 requirement
- Candidate/request/seed/canvas/SHA locks
- generated text/branding/exact facts/entity marks/sport-geometry prohibitions
- Original Scene runtime admission
- Qwen `BASE_SCENE` / `HYBRID_SURFACE`
- deterministic football geometry
- provenance/evidence replay
- Golden 8.5 minimum / 9.0+ elite thresholds
- Exact Brand Integrity
- Typography Integrity
- SemanticPublicationGate

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted visually.

## Files changed

Modified:

- `engine/intelligence/local_runtime.py`
- `engine/intelligence/gpu_host_qualification.py`
- `tools/phase18_qualify_gpu_host.py`
- `tools/phase18_colab_first_golden_bootstrap.py`
- `.github/workflows/phase18-first-golden-review.yml`
- `tests/test_phase18_local_runtime.py`
- `tests/test_phase18_gpu_host_qualification.py`
- `tests/test_phase18_colab_first_golden_bootstrap.py`
- `tests/test_phase18_first_golden_review_workflow.py`

Added:

- `docs/PHASE18_CHANGESET_154_LIVE_FREE_VRAM_QUALIFICATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_154.md`

Deleted: none.
