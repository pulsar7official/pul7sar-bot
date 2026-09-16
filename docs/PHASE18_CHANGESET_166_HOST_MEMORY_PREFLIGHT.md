# Phase 18 Change Set 166 — Host Memory Preflight Before First Golden Model Work

## Objective

Reduce the remaining risk before the first genuine Golden Hybrid v5 PNG by proving that the CUDA host also has enough *currently available system RAM* before Qwen/FLUX model work starts.

Sequential CPU offload protects constrained GPU VRAM, but it moves model state through host memory. Previous Phase 18 gates proved CUDA, BF16, total/live free VRAM, safe Diffusers offload capability, model revisions, cache budget, and runtime stability. They did not independently prove live CPU-memory headroom before model preparation.

## Changes

### Added `engine/intelligence/host_memory_qualification.py`

- stdlib-only `/proc/meminfo` measurement;
- measures total, available and used system RAM plus swap telemetry;
- default first-Golden available-RAM floor: **10 GiB**;
- never substitutes total RAM for `MemAvailable`;
- missing/unreadable live memory evidence fails closed;
- no network, model load, queue mutation, generation, semantic approval, Golden approval, or publication authority.

The 10 GiB value is an engineering admission floor, not a claim that every later allocation is guaranteed. It prevents obviously memory-starved hosts from entering expensive model work while retaining compatibility with the constrained zero-cost GPU class Phase 18 is targeting.

### Added `tools/phase18_preflight_host_memory.py`

CPU-only preflight that writes:

`output/phase18_gpu_smoke/host-memory-preflight.json`

The command is Phase-18-branch locked and `$0-local`.

### Added `tools/phase18_colab_first_golden_host_memory_locked.py`

New additive staging wrapper:

`host-memory preflight -> existing runtime-locked Candidate 1 pipeline`

It SHA-binds both the host-memory receipt and the existing runtime-lock receipt and keeps:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

No existing Golden runtime path was weakened or removed.

## Tests

Added:

- `tests/test_phase18_host_memory_qualification.py`
- `tests/test_phase18_first_golden_host_memory_lock.py`

Coverage includes:

- sufficient live available RAM;
- large total RAM with insufficient live available RAM;
- missing `MemAvailable` without guessing;
- measurement failure fail-closed behavior;
- host-memory preflight ordering before the runtime-locked pipeline;
- no Candidate 1 continuation when memory qualification fails;
- authority-drift rejection;
- repository path confinement.

## Safety / policy preservation

Unchanged:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local`;
- pinned FLUX.2 Klein 4B and Qwen revisions;
- native BF16 requirement;
- total/live-free VRAM gates;
- safe CPU-offload capability gate;
- lease-bound GPU requalification;
- runtime fingerprinting;
- request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/sport-geometry prohibitions;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` inspection;
- deterministic football geometry;
- provenance/evidence replay;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- Exact Brand/Typography Integrity;
- SemanticPublicationGate.

## Files

Added:

- `engine/intelligence/host_memory_qualification.py`
- `tools/phase18_preflight_host_memory.py`
- `tools/phase18_colab_first_golden_host_memory_locked.py`
- `tests/test_phase18_host_memory_qualification.py`
- `tests/test_phase18_first_golden_host_memory_lock.py`
- this document

Deleted: **none**.

`main` / `main.py`: **not modified**.

## Remaining blocker

No genuine Golden Hybrid v5 PNG is claimed by this change set. The remaining blocker is still a real compatible host providing NVIDIA CUDA, native BF16, sufficient total/live-free VRAM, safe Diffusers offload capability, sufficient live host RAM, the pinned FLUX/Qwen revisions, and the established zero-cost runtime path.
