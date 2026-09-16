# Phase 18 Change Set 234 — Qwen Image 2512 Live Same-Host Recheck

## Purpose

Change Set 233 locked the requirement that any controlled Golden trial must recheck the exact qualified Qwen runtime on the live host immediately before canonical generation. Change Set 234 makes that requirement executable without loading model weights or running inference.

## Added

- `engine/intelligence/qwen_image_live_host_recheck.py`
- `tools/phase18_recheck_qwen_live_host.py`
- `tests/test_phase18_qwen_image_live_host_recheck.py`

## Evidence boundary

The recheck observes the current CUDA/Torch/Diffusers environment and requires exact equality with the runtime identity locked by Change Sets 232–233 across:

- GPU name
- total VRAM
- Torch version
- CUDA version
- Diffusers version
- `QwenImagePipeline`
- `bfloat16`
- `sequential_cpu` offload contract
- native BF16 support

The observed runtime fingerprint must also equal the fingerprint already locked in the controlled Golden-trial preflight contract.

## What a passing receipt proves

A passing receipt proves only that the currently executing host/runtime identity matches the exact previously qualified runtime identity. It does not load Qwen weights and does not execute inference.

The receipt explicitly keeps all of the following false:

- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `queue_mutated`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`
- `fresh_story_gates_passed`
- `controlled_trial_preflight_valid`
- `genuine_golden_png_created`

## Preserved gates

No factual, identity, sentiment, zero-cost, semantic/layer, Visual Critic, Human Review, brand, typography, Golden-score, or SemanticPublicationGate requirement is weakened. The canonical model remains pinned and the recheck remains `$0-local`.

## Why this reduces the Golden gap

Before Change Set 234, `live_same_host_recheck_required=true` was a locked requirement but had no dedicated executable evidence receipt. The first compatible CUDA host would therefore still need an ad-hoc runtime identity check before canonical generation. Change Set 234 removes that ambiguity and makes the recheck deterministic, SHA-bound, replayable, and fail-closed.

## Remaining blocker

The current execution environment still does not provide a compatible self-hosted NVIDIA CUDA runtime with the exact pinned Qwen Image 2512 snapshot and the previously measured/qualified runtime chain. Therefore no genuine Golden PNG is claimed by this change set.
