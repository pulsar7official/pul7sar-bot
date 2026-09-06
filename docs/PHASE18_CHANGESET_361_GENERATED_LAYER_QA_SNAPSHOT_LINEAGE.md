# Phase 18 Change Set 361 — Generated-Layer QA Snapshot Lineage

## Purpose

CS361 closes the first verified downstream lineage gap after CS360 without creating a parallel gate. The existing `qwen_image_canonical_candidate_generated_layer_qa.py` contract already fresh-replayed CS360 semantic-base QA and the identity-requirement/review lineage, but its generated-layer QA receipt did not preserve the exact Qwen-Image generator snapshot byte lineage that CS360 had already proven.

## Contract change

The existing generated-layer QA schema advances from `v1` to `v2`. A successful build now requires the fresh CS360 receipt to carry valid generator snapshot evidence and seals these exact fields into the generated-layer receipt:

- `snapshot_byte_inventory_verified = true`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

Verification does not trust the sealed fields merely because the outer receipt digest is valid. It fresh-replays `verify_canonical_candidate_semantic_base_qa(...)`, reconstructs the verified lineage, and compares every sealed lineage field. Any mismatch fails closed.

## Security / authority properties

This change grants no new editorial, identity, semantic-publication, Human Review, Golden-quality, materialization, publication-readiness, or external-publication authority. The existing HybridLayerQualityGate remains the generated-layer authority. Existing identity-review requirements remain mandatory when required, and upstream unverified-identity evidence is never suppressed.

No model download, network model fallback, paid execution fallback, synthetic inference, retry shortcut, upload shortcut, or publication shortcut is introduced.

## Regression coverage

The existing generated-layer QA tests are updated for CS360 lineage and add coverage for:

- exact lineage propagation from fresh CS360 replay;
- fail-closed behavior when snapshot inventory proof is absent;
- snapshot inventory tampering rejected even after recomputing the outer receipt digest;
- preservation of existing identity, generated-text leakage, candidate-byte-drift, and output-isolation behavior.

Tests use Python `unittest` only and add no dependency.
