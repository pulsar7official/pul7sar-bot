# Phase 18 Change Set 228 — Qwen Runtime Envelope Byte-Bound Admission

## Objective

Reduce the remaining gap between the successful engineering single-inference contract and a future measured runtime-envelope experiment without fabricating CUDA execution or weakening any Golden/publication gate.

## Problem closed

Change Sets 226–227 made the Qwen Image 2512 single-inference receipt tamper-evident and internally consistent, but the receipt replay only required a PNG-shaped path, SHA-256-shaped digest, and positive size. The next stage therefore needed an independent byte replay before it could trust those pixels as engineering evidence.

Change Set 228 adds that missing transition. A runtime-envelope experiment may only be admitted after the source inference receipt is replayed and the exact PNG bytes are reopened, verified as PNG, checked for repository path containment, and matched to the recorded SHA-256 and byte size.

## Added

- `engine/intelligence/qwen_image_runtime_envelope_admission.py`
  - replays the existing single-inference receipt;
  - requires a measured successful single inference;
  - resolves the engineering PNG inside the repository boundary;
  - verifies the PNG signature, exact size, and SHA-256 against live bytes;
  - validates positive GPU/RAM/time telemetry and basic CUDA-memory consistency;
  - emits a SHA-bound runtime-envelope admission receipt.
- `tools/phase18_build_qwen_runtime_envelope_admission.py`
  - CPU-only evidence builder;
  - does not load the model, call CUDA, perform inference, or mutate queues.
- `tests/test_phase18_qwen_image_runtime_envelope_admission.py`
  - canonical `unittest` regression coverage for byte tampering, signature changes, path escape, telemetry inconsistency, and authority drift.

## Authority boundary

The admission receipt is engineering evidence only. Even a valid admission forces all of the following to remain false:

- `source_pixels_canonical_reusable`
- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `queue_mutated`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

Therefore this change cannot turn the 512x512 engineering probe into a Golden Visual candidate.

## Preserved gates

Fact Lock, identity/entity verification, sentiment/neutrality, canonical `$0-local`, pinned model provenance, generated-text/branding/exact-fact/entity-mark/exact-sport-geometry exclusions, Semantic/Layer Ownership, byte-bound Visual Critic, Human Review, Golden 8.5 minimum / 9.0+ elite target, Exact Brand/Typography integrity, and SemanticPublicationGate remain fail-closed.

## Remaining blocker

No compatible self-hosted CUDA host is available in the current execution environment. The first real runtime-envelope measurement still requires the pinned Qwen Image 2512 snapshot on a `$0-local` NVIDIA host with native BF16, sufficient live VRAM and system RAM, compatible Diffusers/QwenImagePipeline runtime, and safe offload behavior.

No GPU result, runtime floor, canonical PNG, Golden score, or publication approval is claimed by this change set.
