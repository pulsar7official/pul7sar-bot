# Phase 18 Change Set 259 — Live Host Identity Recheck

## Purpose

Change Set 259 narrows the gap between the story-bound controlled-trial request from Change Set 258 and the first genuine Qwen Image 2512 generation attempt.

It performs a fresh, same-host, no-weight observation of the CUDA/software environment and compares the observable identity fields against the exact runtime identity locked by the Change Set 233 preflight contract.

## What it proves

A passing CS259 receipt proves only that the currently observed host matches the previously qualified runtime for these fields:

- GPU name
- total GPU VRAM
- PyTorch version
- CUDA runtime version exposed by PyTorch
- Diffusers version
- native BF16 support

The receipt is byte-bound to the exact CS258 request and the exact CS233 preflight contract.

## What it deliberately does not prove

CS259 does not instantiate the Qwen Image 2512 model, load model weights, activate sequential CPU offload, execute inference, create canonical pixels, approve semantics, approve visual quality, approve branding/typography, or authorize publication.

Therefore a successful CS259 receipt keeps all of the following false:

- `live_host_recheck_passed`
- `controlled_trial_preflight_valid`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_canonical_inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

The next runtime boundary must still prove the pipeline-load/offload portion on the same host before any generation authority can be considered.

## Fail-closed behavior

CS259 rejects request digest drift, request authority drift, preflight byte drift, preflight digest drift, cross-contract binding drift, symlinked inputs, incompatible model/revision/cost mode, missing native BF16, GPU identity mismatch, software-version mismatch, and malformed observation fields.

The production CLI collects the observation locally from `torch` and `diffusers`, verifies CUDA and native BF16, and imports the `QwenImagePipeline` class without instantiating it. It does not load weights.

## Zero-cost and quality boundaries

The path remains `$0-local`. All factual, identity, sentiment, semantic-preflight, zero-cost, semantic-layer-ownership, post-generation semantic/layer QA, Visual Critic, Human Review, Golden 8.5/9.0, Exact Brand/Typography, and SemanticPublicationGate requirements remain unchanged and closed until their respective evidence exists.
