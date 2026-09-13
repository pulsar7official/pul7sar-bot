# Phase 18 Change Set 363 — Composition Execution Preflight Snapshot Lineage

## Purpose

CS363 closes the first proven generator-lineage gap downstream of CS362. The existing `qwen_image_canonical_candidate_composition_execution_preflight.py` contract already fresh-replayed the deterministic composition request, reopened the exact candidate bytes, and validated repository-bound deterministic payload bytes, but its own receipt did not preserve the Qwen-Image generator snapshot-byte lineage.

CS363 changes that existing boundary rather than creating a parallel gate.

## Contract change

The composition execution preflight schema advances from `v1` to `v2` and now seals the exact upstream fields:

- `snapshot_byte_inventory_verified=true`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

The values are accepted only from a successful fresh `verify_deterministic_composition_request(...)` replay. They are independently shape-validated before sealing.

During receipt verification, CS363:

1. validates the preflight receipt digest and all existing closed-authority constraints;
2. validates the sealed snapshot lineage;
3. reopens the exact source CS362/CS269 receipt and payload manifest bytes;
4. fresh-replays `verify_deterministic_composition_request(...)`;
5. extracts the fresh upstream snapshot lineage;
6. requires every sealed lineage field to match the fresh replay;
7. then continues the existing candidate-byte, payload-byte, renderer-contract, blocker, and readiness replay.

Therefore changing lineage metadata and recomputing the outer `receipt_sha256` is insufficient to forge a valid preflight receipt.

## Authority preservation

CS363 does not render pixels and does not grant any new semantic, identity, sentiment, visual-quality, Human Visual Review, Golden, semantic-publication, publication-readiness, or external-publication authority. Existing downstream false authorities remain explicitly false.

No network model fallback, paid execution fallback, model download, synthetic inference, or publication shortcut is introduced.

## Tests

Regression coverage verifies:

- successful snapshot-lineage preservation;
- rejection of an unverified upstream snapshot inventory;
- rejection of snapshot-inventory tampering even after recomputing the outer receipt digest;
- rejection of generator-revision tampering even after recomputing the outer receipt digest;
- preservation of existing payload, candidate-byte, renderer-contract, output-isolation, and authority behavior.

The test suite remains standard-library `unittest` based and adds no dependency.
