# Phase 18 Change Set 231 — Qwen Image 2512 Runtime Qualification Candidate

## Purpose

Change Set 230 made the locked 512/768/1024 Qwen Image 2512 runtime envelope executable on a future compatible `$0-local` CUDA host. Its aggregate execution receipt validates each probe independently and byte-binds successful engineering PNGs.

Before any later runtime-qualification decision, one additional evidence property must be enforced: the successful probes must describe one coherent runtime environment rather than a stitched set of individually valid observations from different GPUs or software stacks.

Change Set 231 adds that normalization boundary.

## What was added

### `engine/intelligence/qwen_image_runtime_qualification_candidate.py`

Consumes a Change Set 230 execution receipt and:

1. replays the Change Set 230 receipt, including byte verification when `repo_root` is provided;
2. requires the envelope to be fully measured, not stopped or partially successful;
3. requires all three locked probes to have succeeded;
4. requires one coherent runtime identity across all probes for:
   - GPU name;
   - total GPU VRAM;
   - Torch version;
   - CUDA version;
   - Diffusers version;
   - `QwenImagePipeline` class;
   - BF16 evidence;
   - dtype;
   - sequential CPU offload mode;
5. summarizes conservative observed bounds across the complete envelope;
6. emits a SHA-bound runtime qualification *candidate*.

The candidate is deliberately non-authoritative.

### `tools/phase18_build_qwen_runtime_qualification_candidate.py`

CPU-only CLI that converts an on-disk Change Set 230 execution receipt into a qualification candidate. It never loads Qwen Image, invokes CUDA, changes the generation queue, or authorizes canonical generation.

### `tests/test_phase18_qwen_image_runtime_qualification_candidate.py`

Canonical `unittest` regressions cover:

- complete same-runtime envelope acceptance as a candidate only;
- mixed GPU identity rejection;
- mixed CUDA-version rejection;
- mixed total-VRAM rejection;
- stopped/incomplete envelope rejection;
- authority forgery rejection after digest recomputation;
- candidate digest tamper detection.

## Evidence semantics

A successful Change Set 231 receipt means only:

- all locked engineering probes succeeded;
- the evidence is internally coherent as one measured runtime environment;
- the measured envelope has been normalized for an explicit later qualification review.

It does **not** mean:

- a production runtime floor is proven;
- the local runtime is qualified;
- canonical generation is authorized;
- engineering PNGs may be reused as canonical pixels;
- semantic approval has occurred;
- Human Review has occurred;
- Golden quality has been achieved;
- publication is allowed.

The receipt therefore hard-codes these boundaries as false:

- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `queue_mutated`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Why this materially reduces the Golden gap

Without this boundary, a later qualification stage could accidentally treat three individually valid probe observations as one coherent hardware/runtime measurement even if they were captured on different GPU or software environments. Change Set 231 prevents that evidence-stitching ambiguity before any authority can be raised.

The remaining path is now:

`locked envelope execution -> coherent qualification candidate -> explicit local-runtime qualification -> genuine canonical trial PNG -> semantic/layer QA -> byte-bound Visual Critic -> Human Review -> Golden threshold -> brand/typography -> SemanticPublicationGate`

## Preserved gates

No Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local`, pinned-model provenance, generated-text/branding/exact-fact/entity-mark/exact-sport-geometry restriction, Semantic/Layer Ownership, byte-bound Visual Critic, Human Review, Golden threshold, Exact Brand Integrity, Typography Integrity, or SemanticPublicationGate rule is weakened by this change set.

## Golden status

No genuine Golden Visual PNG is claimed or fabricated by Change Set 231. The current execution environment still lacks the compatible self-hosted CUDA execution required to produce the measured envelope that this new layer consumes.
