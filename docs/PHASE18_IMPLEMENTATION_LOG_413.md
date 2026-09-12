# Phase 18 Implementation Log — CS413

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

Starting branch HEAD: `417f9d316ce46e96f81649d23411cc8b351063c5`.

## Why CS413 was needed

The Story Intelligence verification run for CS412 (`34641299770`) failed during `Syntax and discover validation` before any GPU execution. The full Phase 18 unittest discovery ran 2324 tests and reported 4 failures plus 15 errors.

The failures were caused by legacy test fixtures constructing approved-model snapshot paths such as `.../snapshots/<revision>` under arbitrary cache prefixes. CS412 intentionally hardened `assert_snapshot_revision()` so an approved snapshot must live under the canonical Hugging Face cache layout `models--<owner>--<repo>/snapshots/<revision>`.

The production validator is correct and was not weakened. CS413 aligns the affected fixtures with the canonical layout so each test reaches the specific condition it is intended to exercise.

## Changes

Modified test fixtures only:

- `tests/test_phase18_colab_first_golden_bootstrap.py`
  - Qwen2.5-VL cache fixture now uses `models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots/<revision>`.
- `tests/test_phase18_qwen_image_gpu_host_launch_manifest.py`
  - Qwen-Image snapshot fixture now uses `models--Qwen--Qwen-Image-2512/snapshots/<revision>`.
- `tests/test_phase18_qwen_image_inventory_bound_launch_manifest.py`
  - snapshot inventory fixture now uses the canonical Qwen-Image cache path.
- `tests/test_phase18_qwen_image_local_inference_provenance.py`
  - accepted and wrong-revision fixtures both use canonical Qwen-Image cache structure so revision-drift tests remain revision tests rather than malformed-cache tests.
- `tests/test_phase18_qwen_image_measurement_admission.py`
  - complete, incomplete, and wrong-revision snapshot fixtures now share canonical Qwen-Image cache structure.
- `tests/test_phase18_semantic_gpu_preflight.py`
  - semantic Qwen2.5-VL snapshot fixtures now use canonical Hugging Face cache structure.

Added:

- `docs/PHASE18_IMPLEMENTATION_LOG_413.md`

Deleted: none.

Production code changed: none.

## Gate preservation

CS413 does not change model IDs, approved revisions, prompts, generation settings, dependencies, or runtime authority. It does not relax factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gates.

The CS412 canonical-cache validator remains intact. Local model execution remains `$0-local`, revision-pinned, and fail-closed. Human visual review, Golden Quality, publication readiness, and Seeds 2–4 remain unauthorized.

## Validation status

The pre-fix verification run `34641299770` is the diagnostic baseline: 2324 Phase 18 tests were discovered, with 4 failures and 15 errors, all occurring before GPU execution because legacy test fixtures were intercepted by the new canonical-cache guard.

A new Story Intelligence verification is expected from the CS413 branch HEAD after these fixture-only updates. Its terminal status must be checked before CS413 is described as terminal-green.

## First Genuine Golden Visual status

No genuine Golden PNG was created or claimed in CS413.

The remaining non-substitutable execution blocker is a compatible self-hosted NVIDIA runner satisfying the Phase 18 Golden execution contract: CUDA-enabled PyTorch, native BF16, sufficient live VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in canonical local Hugging Face cache. Network model downloads remain unauthorized.
