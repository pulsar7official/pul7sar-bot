# Phase 18 Change Set 153 — Early GPU Host Qualification

## Goal

Reduce the remaining risk before the first genuine Golden Hybrid v5 PNG by proving that the physical GPU host can actually execute the locked native-BF16 FLUX.2 Klein path **before any Qwen or FLUX model-weight download is permitted**.

## Problem found

The canonical strict first-Golden bootstrap already proved repository integrity, repaired the runtime, checked combined cache headroom, prepared Qwen, and only later reached the existing first-PNG path where GPU host qualification happened.

That ordering could waste a rare compatible-GPU session by downloading Qwen weights on a CUDA host that later proves unsuitable because of insufficient VRAM or missing native BF16 support.

## Changes

### `tools/phase18_colab_first_golden_bootstrap.py`

- Added an explicit early call to `tools/phase18_qualify_gpu_host.py` immediately after runtime repair.
- The host must prove:
  - `eligible=true`
  - exact model `black-forest-labs/FLUX.2-klein-4B`
  - `runtime_kind=local_cuda`
  - CUDA-enabled PyTorch
  - native BF16 support
  - `$0-local`
  - no dependency install, model download, queue mutation, or paid API authority in the qualification policy.
- Host qualification now occurs before the combined Qwen+FLUX cache budget and before Qwen prefetch.
- Added SHA/byte evidence binding for `output/phase18_gpu_host/qualification.json`.
- Raised the strict bootstrap receipt contract from `pul7sar-first-golden-colab-bootstrap-v2` to `pul7sar-first-golden-colab-bootstrap-v3`.
- Added `gpu_host_eligible=true` and `native_bf16_proven=true` to the final strict bootstrap receipt.

### `.github/workflows/phase18-first-golden-review.yml`

- Updated canonical replay verification to require bootstrap v3.
- Added `gpu_host_qualification` to the exact bootstrap evidence set.
- Replays the qualification file hash and size, then rechecks eligibility, native BF16, exact FLUX model, local CUDA runtime, and `$0-local` before the Candidate 1 review artifact can be accepted.

### Regression tests

Updated:

- `tests/test_phase18_colab_first_golden_bootstrap.py`
- `tests/test_phase18_first_golden_review_workflow.py`

New/expanded assertions prove:

- GPU host qualification happens after runtime repair but before cache/model downloads.
- An ineligible or non-BF16 host blocks before semantic prefetch and sealed staging.
- Host qualification cannot gain download/install/queue/paid-API authority.
- Bootstrap v3 contains the host receipt in its SHA-bound evidence set.
- The canonical workflow replays and validates the host receipt before artifact acceptance.

## Unchanged safety/quality contracts

No changes were made to:

- Fact Lock
- Entity/Identity Verification
- Sentiment/Neutrality
- `$0-local`
- FLUX.2 Klein 4B model identity
- native BF16 requirement
- Candidate/request/seed/canvas/SHA locks
- generated text/branding/exact facts/entity marks/sport-geometry prohibitions
- Qwen `BASE_SCENE` / `HYBRID_SURFACE` gates
- deterministic football geometry
- provenance/evidence replay
- Golden 8.5 minimum / 9.0+ elite thresholds
- Exact Brand Integrity
- Typography Integrity
- SemanticPublicationGate

`main` and `main.py` were not modified.

## Deleted files

None.

## Remaining blocker

A genuine Golden Hybrid v5 PNG still requires a real NVIDIA CUDA host that proves the current native-BF16 and VRAM policy. No PNG or benchmark is fabricated when such hardware is unavailable.
