# Phase 18 Change Set 287 — Qwen-Image GPU Static Preflight

## Purpose

CS287 reduces the remaining execution gap after CS286 without adding another approval authority. It introduces a local, zero-cost, fail-closed static preflight for the pinned `Qwen/Qwen-Image-2512` runtime.

The preflight does **not** download models, instantiate `QwenImagePipeline`, allocate model weights, run inference, create image bytes, approve a visual, or grant semantic/publication authority.

## Checks

The preflight records and verifies, where locally observable:

- PyTorch version and CUDA runtime visibility.
- CUDA availability and device count.
- native BF16 support.
- GPU identity and observed VRAM as diagnostics only.
- `nvidia-smi` availability.
- `diffusers.QwenImagePipeline` importability.
- `enable_sequential_cpu_offload` support.
- the exact approved local `Qwen/Qwen-Image-2512` snapshot revision via `approved_model_revisions.assert_snapshot_revision`.
- zero-cost/local-only semantics: no network access is initiated.

## Fail-closed authority boundary

`static_preflight_passed=true` means only that the host is eligible for a **real model-load attempt**. It never means genuine inference succeeded.

The contract therefore always emits:

- `genuine_inference_executed=false`
- `ready_for_genuine_inference_claim=false`

A genuine-inference claim remains downstream of actual model loading and image generation evidence.

## VRAM handling

CS287 intentionally does not invent a Qwen-specific minimum-VRAM threshold. Observed VRAM is recorded as `gpu_memory_gib_observed`, but resource sufficiency must be proven by a genuine compatible model-load/inference run or by a separately approved execution contract. This avoids treating the older FLUX-specific GPU threshold as if it applied to Qwen-Image.

## Preserved gates

No changes are made to factual, identity/entity, sentiment/loser-respect, zero-cost semantic verification, visual-quality/Golden adjudication, human review, brand/typography, final semantic approval, `SemanticPublicationGate`, Genuine Golden materialization, or publication readiness.
