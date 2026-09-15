# PUL7SAR Phase 18 — Change Set 165
## Pre-model FLUX.2 Offload Capability Qualification

### Goal
Reduce the remaining risk before the first genuine Golden Candidate 1 by proving the installed Diffusers runtime exposes a safe CPU-offload path **before** any FLUX.2 weights are loaded or downloaded.

### Gap
Change Set 164 correctly blocked unsafe model-level CPU offload on T4-class / low-VRAM hosts. That protection was enforced inside the pipeline factory, after `Flux2KleinPipeline.from_pretrained(...)` had already been called.

On a constrained but otherwise compatible CUDA host, this still left a wasteful failure mode: repository checks, runtime repair, GPU qualification, cache planning and potentially model preparation could proceed before discovering that the installed Diffusers build did not expose the sequential offload API required for safe low-VRAM execution.

### Added
- `engine/intelligence/flux2_offload_capability.py`
  - inspects the installed `Flux2KleinPipeline` class without instantiating it;
  - proves availability of `enable_sequential_cpu_offload` and `enable_model_cpu_offload`;
  - binds the safe choice to measured physical VRAM;
  - requires sequential CPU offload at or below the existing 16-GiB model-offload safety floor;
  - permits model-level offload only above that floor when sequential offload is unavailable;
  - performs no model load, network request, download, generation, queue mutation or publication action.
- `tools/phase18_preflight_flux2_offload.py`
  - consumes the existing GPU host qualification receipt;
  - enforces Phase 18 branch, approved FLUX model identity, CUDA, BF16 and `$0-local`;
  - writes `output/phase18_gpu_smoke/flux2-offload-preflight.json` only when a safe mode is proven.
- `tests/test_phase18_flux2_offload_capability.py`
  - low-VRAM sequential success;
  - low-VRAM model-only rejection;
  - high-VRAM model-offload fallback;
  - unknown VRAM rejection;
  - missing offload API rejection;
  - zero-cost / no-authority CLI contract;
  - host identity drift rejection.

### Modified
- `tools/phase18_colab_first_golden_bootstrap.py`
  - runs FLUX offload capability preflight immediately after GPU host qualification and **before cache budget / Qwen model preparation**;
  - upgrades the bootstrap receipt to `pul7sar-first-golden-colab-bootstrap-v5`;
  - records the safe offload mode and seals the offload preflight receipt into `bootstrap_evidence`.
- `tests/test_phase18_colab_first_golden_bootstrap.py`
  - locks the new ordering and fail-closed behavior;
  - proves low-VRAM offload failure stops before model downloads;
  - proves offload preflight cannot grant generation or publication authority.
- `.github/workflows/phase18-first-golden-review.yml`
  - replays the offload preflight receipt and SHA as part of the canonical first-Golden evidence chain;
  - binds total VRAM between GPU host qualification and offload preflight;
  - enforces sequential mode for low-VRAM hosts.
- `tests/test_phase18_first_golden_review_workflow.py`
  - adds regression locks for the v5 bootstrap contract and offload evidence replay.

### Deleted
None.

### Gates preserved
No change to:
- Fact Lock;
- Entity / Identity Verification;
- Sentiment / result neutrality;
- `$0-local` policy;
- pinned FLUX and Qwen revisions;
- native BF16;
- total/live-free VRAM qualification;
- lease-bound GPU requalification;
- runtime fingerprint stability;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact facts/entity marks/sport geometry prohibitions;
- Qwen BASE_SCENE / HYBRID_SURFACE gates;
- deterministic football geometry ownership;
- provenance/evidence replay;
- Golden 8.5 minimum / 9.0+ elite threshold;
- Exact Brand / Typography integrity;
- SemanticPublicationGate / final publication readiness.

### Golden PNG status
No genuine Golden Hybrid v5 Candidate 1 PNG is claimed by this change. The exact external blocker remains a compatible NVIDIA CUDA host with native BF16 and sufficient live free VRAM. This change reduces the gap by ensuring an incompatible Diffusers offload API is detected before FLUX model-weight loading or download work begins.
