# Phase 18 Change Set 226 — Qwen Image 2512 Single-Inference Measurement

## Purpose

Change Set 225 proved only that the exact pinned `Qwen/Qwen-Image-2512` snapshot could be instantiated in an isolated process. That does not prove that a diffusion step can execute, does not establish a production runtime floor, and cannot authorize canonical generation.

Change Set 226 adds the next narrow measurement stage: one isolated, identity-neutral, `$0-local` inference probe using the exact pinned snapshot. The probe is deliberately small (`512x512`, four inference steps, fixed seed) and uses sequential CPU offload. It exists only to answer whether the measured host can complete one real Qwen Image inference without risking the parent orchestration process.

## Safety boundary

A successful probe remains engineering evidence only. It explicitly records:

- `engineering_measurement_only=true`
- `canonical_pixels_reusable=false`
- `runtime_floor_proven=false`
- `local_runtime_qualified=false`
- `canonical_generation_authorized=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`

The generated probe PNG is therefore not a Golden candidate and cannot be reused as canonical publication evidence.

## Prompt isolation

The probe prompt contains no PUL7SAR/PULSAR name, no real person, no real club, no real venue, no readable text, no crest, no sponsor mark, no exact sport geometry, and no field lines. It requests one continuous empty sports-adjacent architectural environment only.

The prompt is validated fail-closed and is SHA-256 bound into the measurement receipt.

## Runtime behavior

`tools/phase18_measure_qwen_image_single_inference.py`:

1. requires a successful Change Set 225 pipeline-load receipt;
2. replays the load receipt SHA and exact pinned model revision;
3. launches a child process;
4. loads the exact local snapshot with `torch.bfloat16` and `local_files_only=True`;
5. requires `enable_sequential_cpu_offload()`;
6. executes exactly one `512x512` image with four steps and a fixed seed;
7. writes the output PNG and records its SHA-256/size;
8. records GPU/RAM/runtime observations;
9. emits a fail-closed engineering measurement receipt.

If the child is OOM-killed, times out, or fails before writing a result, the parent records failure evidence and does not infer success.

## Files

Added:

- `engine/intelligence/qwen_image_inference_measurement.py`
- `tools/phase18_measure_qwen_image_single_inference.py`
- `tests/test_phase18_qwen_image_inference_measurement.py`
- `docs/PHASE18_CHANGESET_226_QWEN_IMAGE_SINGLE_INFERENCE_MEASUREMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_226.md`

Modified production/runtime files: none.

Deleted: none.

`main` and `main.py` are untouched.

## What this does not prove

A single successful 512x512 four-step probe does **not** prove the canonical Golden canvas, quality settings, sustained resource floor, semantic quality, visual quality, or publication readiness. Those remain separate fail-closed stages.

The next permissible stage after a real successful probe is a controlled runtime-floor experiment that measures a declared resolution/step envelope. Only measured evidence may change `runtime_floor_proven` from false.