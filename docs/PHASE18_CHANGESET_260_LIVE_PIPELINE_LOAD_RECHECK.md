# Phase 18 — Change Set 260: Live Pipeline Load Recheck

## Purpose

Change Set 259 deliberately proved only the live observable CUDA/software identity. It did not load the pinned Qwen Image 2512 weights and therefore could not prove that the same host could instantiate `QwenImagePipeline` in the previously qualified `bfloat16` / `sequential_cpu` runtime contract.

Change Set 260 closes exactly that gap without generating pixels.

## Production path

`CS258 story-bound request -> CS259 live host identity -> CS260 pinned pipeline load + sequential CPU offload -> separate canonical generation authorization`

The live CLI:

1. requires CUDA and native BF16;
2. imports the installed Diffusers `QwenImagePipeline`;
3. loads `Qwen/Qwen-Image-2512` at the repository-pinned exact revision with `torch.bfloat16`;
4. requires the loaded class to be `QwenImagePipeline`;
5. calls `enable_sequential_cpu_offload()` successfully;
6. records the same GPU/software identity again after load;
7. passes the observation to the fail-closed CS260 receipt builder;
8. deletes the pipeline reference and clears caches;
9. never calls the pipeline and therefore never performs inference.

## Fail-closed bindings

CS260 reopens the exact CS259 receipt and the CS233 preflight bytes that CS259 bound. It rejects schema/status/model/cost drift, stale or modified preflight bytes, semantic-authority drift, GPU/software drift between CS259 and the load observation, pipeline/dtype/offload mismatch, absent BF16, absent weights-load proof, and absent sequential-offload proof.

The runtime contract is reused from `qwen_image_runtime_envelope_plan.py` (`DTYPE=bfloat16`, `OFFLOAD_MODE=sequential_cpu`) rather than copied as an independent constant.

## Authority boundary

A passing CS260 receipt may truthfully set only the runtime facts that have now been executed on the same host:

- `model_weights_loaded=true`
- `sequential_cpu_offload_enabled=true`
- `live_host_recheck_passed=true`
- `controlled_trial_preflight_valid=true`

It must still keep all generation and publication authorities closed:

- `canonical_generation_authorized=false`
- `inference_executed=false`
- `genuine_canonical_inference_executed=false`
- `genuine_golden_png_created=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`

Therefore a successful CS260 is not a Golden Visual and is not permission to generate one. A separate story-bound canonical generation authorization remains required.

## Zero-cost boundary

The path remains `$0-local`. No paid inference API is introduced. A compatible CUDA host is still required to execute the live CLI successfully.
