# Phase 18 Change Set 385 — CS359 Candidate Admission Readiness Lineage

## Purpose

Preserve the exact CS351 CUDA/native-BF16 static-readiness receipt binding across the existing CS359 canonical-candidate byte-admission boundary. CS359 already replayed CS358 and preserved exact Qwen snapshot-byte inventory provenance; this changeset closes the remaining readiness-provenance drop before downstream semantic and identity QA.

## Production change

`engine/intelligence/qwen_image_canonical_candidate_byte_admission.py`

- Upgrades the admission schema from `v3` to `v4`.
- Requires `static_readiness_receipt_verified=true` from a freshly verified CS358 handoff before admission can be created.
- Validates and carries the exact readiness binding:
  - `repository_relative_path`
  - `sha256`
  - `byte_size`
- Replays CS358 during admission verification and compares the stored readiness binding with freshly verified upstream evidence.
- Rejects missing readiness authority, malformed readiness provenance, and readiness receipt drift even when the outer CS359 receipt digest is recomputed.

## Regression coverage

`tests/test_phase18_qwen_image_canonical_candidate_byte_admission.py`

Coverage now includes:

- successful readiness-lineage propagation;
- rejection when CS358 readiness authority is absent;
- rejection of readiness SHA tampering after admission even when the outer receipt SHA is recomputed;
- existing snapshot-inventory, exact-candidate-byte, sealed-handoff, local-only, and premature-authority protections.

## Authority boundaries

CS385 adds no new gate and grants no semantic, identity, sentiment, visual-quality, Human Review, Golden, materialization, publication-readiness, or external publication authority. It performs no model loading, inference, pixel mutation, upload, network model fallback, or paid execution.

The candidate remains only admitted for downstream post-generation QA, with `genuine_golden_png_created=false`, `semantic_approved=false`, `human_visual_review_approved=false`, `golden_quality_approved=false`, and `publication_ready=false`.

## Genuine Golden status

This changeset does not claim a Genuine Golden PNG. Real Qwen generation remains dependent on a compatible zero-cost NVIDIA CUDA host with CUDA-enabled PyTorch, native BF16, sufficient RAM/VRAM, and the approved already-local pinned Qwen snapshot.
