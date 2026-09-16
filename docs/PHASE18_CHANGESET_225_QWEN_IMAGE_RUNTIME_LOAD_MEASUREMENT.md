# Phase 18 Change Set 225 — Qwen Image 2512 Runtime Load Measurement

## Goal

Advance the pinned `Qwen/Qwen-Image-2512` local-candidate path from **measurement admission** to a real, isolated **pipeline-load measurement** without fabricating a runtime floor or authorizing image generation.

Change Set 224 proved only that a host is observable and prepared enough to justify a future measurement attempt. It intentionally kept `runtime_floor_proven=false`. Change Set 225 adds the next bounded experiment: instantiate the exact pinned Qwen Image snapshot in a child process, record durable resource/runtime evidence, and preserve a failure receipt even when the child exits or is OOM-killed.

## Safety boundary

A successful load measurement proves only that the exact pinned snapshot can be instantiated by the measured local software stack. It does **not** execute image inference and therefore does **not** prove a usable inference/runtime floor.

Every receipt keeps the following closed:

- `inference_executed=false`
- `runtime_floor_proven=false`
- `local_runtime_qualified=false`
- `generation_authorized=false`
- `queue_mutated=false`
- `png_created=false`
- `semantic_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`

Canonical cost mode remains `$0-local`.

## Added

### `engine/intelligence/qwen_image_runtime_measurement.py`

Adds a fail-closed evidence contract for the pinned Qwen Image 2512 load experiment.

It:

- replays the Change Set 224 measurement-admission SHA;
- requires the exact pinned model ID and revision;
- requires the exact cached snapshot and a complete snapshot structure;
- rejects any upstream authority drift;
- records pipeline-load success/failure and observed resource telemetry;
- emits a SHA-bound measurement receipt;
- never upgrades a successful load to runtime-floor or generation authority.

### `tools/phase18_measure_qwen_image_runtime_load.py`

Adds an isolated measurement runner.

The parent process validates the measurement admission and launches a child process against the exact local snapshot. The child:

- requires CUDA and native BF16;
- imports the installed `QwenImagePipeline`;
- instantiates the exact snapshot using `torch.bfloat16`, `local_files_only=True`, and `low_cpu_mem_usage=True`;
- records software versions, GPU identity, live VRAM before/after, CUDA peak allocation/reservation, process peak RSS, and elapsed time;
- performs **no image inference**.

If the child is terminated without writing a result (including an external OOM kill), the parent still emits a fail-closed measurement receipt rather than treating the attempt as success.

### `tests/test_phase18_qwen_image_runtime_measurement.py`

Adds regression coverage for:

- SHA-bound admission replay;
- exact snapshot requirement;
- authority-drift rejection;
- successful pipeline-load evidence remaining non-authoritative;
- failed/OOM-killed child evidence remaining non-authoritative;
- measurement-receipt tamper detection;
- the measurement tool containing no image-inference call.

## Modified

No existing production/generation/publication runtime file was modified. Change Set 225 is additive above the green Change Set 224 baseline.

## Deleted

Nothing.

## Preserved gates

No factual, entity/identity, sentiment/neutrality, cost, semantic-publication, or visual-quality gate was weakened. In particular:

- canonical generation remains `$0-local`;
- Qwen Image 2512 remains pinned to its approved upstream revision;
- no runtime floor is inferred from observed VRAM or from a successful pipeline load;
- no remote research pixel becomes canonical evidence;
- no generated branding/text/exact facts/entity marks/exact sport geometry authority is introduced;
- Semantic/Layer Ownership, byte-bound Visual Critic, Human Review, Golden `8.5` minimum / `9.0+` elite, Exact Brand/Typography, and SemanticPublicationGate remain downstream and fail-closed.

## Remaining blocker

This environment still does not expose an approved self-hosted `$0-local` CUDA host on which the pinned Qwen Image snapshot can be loaded and measured. Therefore Change Set 225 adds the measurement protocol and evidence path but does **not** claim a successful local load, inference runtime floor, or a new Golden PNG.

The next valid progression is:

`pinned explicit local candidate → measurement admission → isolated pipeline-load measurement → controlled inference/runtime-floor experiment → measured local runtime admission → genuine canonical PNG → Semantic/Layer QA → byte-bound Visual Critic → Human Review → Golden 8.5/9.0+`.
