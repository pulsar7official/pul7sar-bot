# Phase 18 Changeset 384 — CS358 Canonical Handoff Readiness Lineage

## Scope

Harden the existing CS358 canonical-candidate handoff so the exact CS351 CUDA/native-BF16 static-readiness receipt binding already carried by CS357 becomes first-class downstream provenance.

## Why this change

CS383 made CS357 carry `static_readiness_receipt` and `static_readiness_receipt_verified=true`, and CS358 already byte-bound the full CS357 attestation file. However, CS358 exposed the exact Qwen snapshot-byte inventory as first-class provenance while omitting the readiness binding itself. That made the historical preflight evidence less directly auditable by downstream consumers.

CS384 closes only that provenance gap. It creates no new readiness authority and no new approval or publication path.

## Production changes

`engine/intelligence/qwen_image_canonical_candidate_handoff.py`

- schema upgraded from `pul7sar-phase18-qwen-image-2512-canonical-candidate-handoff-v1` to `...-v2`;
- added `_readiness_evidence()` validation for repository-relative path, SHA-256, byte size, and upstream verified flag;
- build now requires CS357 `static_readiness_receipt_verified=true` before sealing CS358;
- payload now carries `static_readiness_receipt` and `static_readiness_receipt_verified=true`;
- verification freshly replays CS357 and compares the stored readiness binding field-by-field;
- malformed, missing, or recomputed-but-drifted readiness evidence fails closed.

## Tests

`tests/test_phase18_qwen_image_canonical_candidate_handoff.py`

- positive propagation of exact readiness binding;
- rejection when CS357 readiness authority is missing;
- rejection of modified readiness SHA even when the outer CS358 `handoff_sha256` is recomputed;
- existing snapshot inventory, source byte-drift, premature-authority, and publication-readiness protections retained.

## Gate preservation

No model loading, inference, image generation, pixel mutation, semantic approval, identity approval, sentiment approval, visual-quality approval, Human Review approval, Golden approval, materialization, upload, publication, or external authority is added.

CS358 continues to require all downstream authority flags to remain false and preserves `$0-local`, offline/local-only execution lineage.

## Genuine Golden status

This changeset does not claim a production `canonical_candidate.png` or `genuine_golden_visual.png`. Genuine inference still requires a compatible zero-cost NVIDIA CUDA host with CUDA-enabled PyTorch, native BF16, sufficient memory, and the approved already-local pinned Qwen assets.
