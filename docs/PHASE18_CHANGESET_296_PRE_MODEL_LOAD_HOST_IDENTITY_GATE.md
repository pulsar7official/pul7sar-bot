# Phase 18 Change Set 296 — Pre-Model-Load Host Identity Gate

## Objective

Move exact CS260 runtime-identity replay ahead of the expensive Qwen `from_pretrained(...)` boundary.

Before CS296, CS287 static preflight ran before model load, but the exact CS260/CS261 runtime identity comparison was completed only after the local Qwen pipeline had already loaded. A host with the wrong GPU identity, VRAM amount, PyTorch/CUDA version, Diffusers version, or runtime contract could therefore consume model-load resources before failing closed.

CS296 closes that gap without inventing a VRAM threshold and without granting any new approval authority.

## Runtime behavior

`engine/intelligence/qwen_image_local_inference_runtime.py` now performs this order:

1. require `PUL7SAR_PHASE18_COST_MODE=$0-local`;
2. run CS287 local static GPU/snapshot preflight;
3. import the already-installed local PyTorch and Diffusers runtime;
4. validate the exact expected CS260 identity field set;
5. require the expected post-load contract to retain `weights_loaded=true` and `sequential_cpu_offload_enabled=true`;
6. measure host-observable identity before model load;
7. compare GPU name, observed total VRAM, PyTorch version, CUDA version, Diffusers version, pipeline class contract, dtype, offload mode, BF16 requirement, model ID, and pinned revision against CS260;
8. only after all those checks pass, call `QwenImagePipeline.from_pretrained(...)` with `local_files_only=True` and BF16;
9. enable sequential CPU offload;
10. replay the complete post-load identity as before.

## Resource-boundary rule

CS296 deliberately does not introduce a minimum VRAM number. Matching the previously attested host identity is not a claim that resources are sufficient. Real resource sufficiency remains proven only by genuine model load and genuine inference.

## Gate preservation

This change does not alter or bypass factual/freshness, entity/identity, sentiment neutrality, loser-respect, story-bound prompt ownership, zero-cost, semantic approval, composition QA, visual-quality adjudication, Human Review, Exact Brand/Typography, SemanticPublicationGate, Genuine Golden materialization, or publication readiness.

No inference pixels are created by the new pre-load comparison and no authority field is set by it.

## Regression coverage

The Phase 18 test surface now verifies that:

- zero-cost mode failure occurs before readiness probing;
- static preflight failure occurs before software/model loading;
- successful execution still uses the exact local snapshot with `local_files_only=True`, BF16, and sequential CPU offload;
- GPU identity drift fails before `from_pretrained`;
- Diffusers-version drift fails before `from_pretrained`;
- the expected sequential-offload post-load contract cannot be weakened.

Synthetic test doubles are control-plane evidence only and are never represented as genuine Qwen output or a Golden Visual.

## Remaining blocker

The first genuine Golden Visual PNG still requires an actually compatible zero-cost NVIDIA CUDA host with CUDA-enabled PyTorch, native BF16, compatible QwenImagePipeline, sequential CPU offload, the exact already-local approved Qwen snapshot, and sufficient real VRAM/RAM demonstrated by genuine load/inference.
