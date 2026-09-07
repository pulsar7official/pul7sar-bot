# Phase 18 Change Set 362 — Deterministic Composition Request Snapshot Lineage

## Purpose

CS362 closes the first verified downstream generator-lineage gap after CS361 without creating a parallel gate. The existing `qwen_image_canonical_candidate_deterministic_composition_request.py` contract is the first branch-specific consumer of `verify_canonical_candidate_generated_layer_qa(...)`. It already fresh-replayed CS361, reopened the exact candidate bytes, enforced the generated-layer plan, bound verified assets, and required deterministic renderer contracts, but its composition-request receipt dropped the exact Qwen-Image generator snapshot-byte lineage proven upstream.

## Contract change

The existing deterministic composition-request schema advances from `v1` to `v2`. A successful build now requires the fresh CS361 receipt to carry valid generator snapshot evidence and seals these exact fields into the composition request:

- `snapshot_byte_inventory_verified = true`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

Verification does not trust these sealed values merely because the outer request digest is valid. It fresh-replays `verify_canonical_candidate_generated_layer_qa(...)`, reconstructs the verified upstream lineage, compares every sealed lineage field, and fails closed on any mismatch.

The top-level `model_revision` remains the Qwen-Image generator revision. It is not repurposed as the identity of any downstream semantic, composition, or visual verifier.

## Security / authority properties

CS362 grants no composition-executed, composed-visual, semantic, identity, Human Visual Review, Golden-quality, Genuine Golden materialization, publication-readiness, or external-publication authority. It only strengthens evidence carried into the pre-existing deterministic composition request.

All existing factual/freshness, Entity/Identity, sentiment-neutrality/loser-respect, zero-cost, semantic-publication, generated-layer, deterministic-layer, visual-quality, Human Review, Golden-quality, Brand/Typography/Presentation, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden materialization, and publication-readiness boundaries remain fail-closed.

No model download, network-model fallback, paid execution fallback, synthetic inference, retry shortcut, upload shortcut, or publication shortcut is introduced.

## Regression coverage

The deterministic composition-request tests now cover:

- exact generator snapshot-lineage propagation from fresh CS361 replay;
- fail-closed behavior when snapshot inventory proof is absent;
- snapshot inventory tampering rejected even after recomputing the outer request digest;
- generator model-revision tampering rejected even after recomputing the outer request digest;
- preservation of existing candidate-byte, verified-asset-byte, CS361-receipt-byte, layer-source, required-brand, and output-isolation behavior.

Tests use Python `unittest` only and add no dependency.
