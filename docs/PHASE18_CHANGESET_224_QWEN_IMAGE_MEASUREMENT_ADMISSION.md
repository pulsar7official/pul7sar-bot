# Phase 18 Change Set 224 — Qwen Image 2512 Measurement Admission

## Goal

Close the gap between the pinned explicit local Qwen Image 2512 candidate and a future measured `$0-local` runtime-floor experiment without inventing a VRAM floor or authorizing canonical generation.

## Why this change exists

`Qwen/Qwen-Image-2512` is now an explicit curated local candidate with immutable upstream revision `2ce1c28560fbc62c9f5531e076b237d3575330a9`, but its `minimum_vram_gb` remains unknown and `runtime_floor_proven=false`. The generic `LocalModelRuntimeGate` therefore correctly blocks local generation. A separate measurement-only admission is required so that a future self-hosted GPU can be screened before spending time on a real model-load experiment.

## Added

- `engine/intelligence/qwen_image_measurement_admission.py`
  - verifies the SHA-bound explicit-local-candidate declaration;
  - requires the exact pinned Qwen Image model/revision and `$0-local` boundary;
  - requires observable CUDA, Torch, native BF16, total VRAM and live-free VRAM;
  - requires the existing live host-memory qualification;
  - requires an installed Diffusers runtime exposing `QwenImagePipeline`;
  - treats the exact pinned Hugging Face snapshot as cached only when the canonical `snapshots/<revision>` path is complete (`model_index.json` plus safetensors);
  - requires conservative cache disk capacity: repository size plus 8 GiB working headroom when uncached, or 8 GiB working headroom when the exact complete snapshot is already cached;
  - emits a SHA-sealed measurement receipt while explicitly keeping runtime-floor, generation, semantic, Golden and publication authority closed.

- `tools/phase18_preflight_qwen_image_measurement.py`
  - CPU/GPU-resource probe only;
  - never downloads or loads model weights;
  - never mutates the generation queue;
  - exits non-zero when the host is not measurement-ready.

- `tests/test_phase18_qwen_image_measurement_admission.py`
  - declaration SHA/authority checks;
  - BF16/live-resource checks;
  - unknown runtime-floor non-inference;
  - exact snapshot revision/completeness checks;
  - disk-capacity rules;
  - Diffusers `QwenImagePipeline` availability;
  - host-memory authority drift rejection.

## Modified

No existing canonical generation, semantic, Golden-quality or publication module was modified.

## Deleted

Nothing.

## Preserved gates

Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, canonical `$0-local`, generated-text/branding/exact-fact/entity-mark/exact-sport-geometry prohibitions, semantic/layer ownership, byte-bound Visual Critic, Human Review, Golden `8.5 minimum / 9.0+ elite`, Exact Brand/Typography Integrity and `SemanticPublicationGate` remain unchanged and fail-closed.

## Important boundary

A successful measurement admission means only: **this host is sufficiently observable and prepared to justify a future Qwen Image runtime-floor measurement attempt**. It does not mean the model fits, does not prove a VRAM floor, does not authorize generation, and does not make any remote research pixels canonical evidence.
