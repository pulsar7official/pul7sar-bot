# Phase 18 Changeset 377 — CS347 Semantic Publication Request Snapshot Lineage

## Scope

Harden the existing CS347 continuation from CS346 Final Semantic Approval to the existing CS283 Semantic Publication Execution Request without executing SemanticPublicationGate, materializing a Genuine Golden PNG, or granting publication authority.

## Proven downstream contract

The branch-local tree contains `engine/intelligence/qwen_image_final_semantic_approval_to_semantic_publication_execution_request.py`, which replays CS346 and its exact CS282 receipt before building CS283. This is the first existing continuation after CS346/CS282 toward SemanticPublicationGate.

## Gap closed

CS346 schema v2 already carries the exact Qwen generator snapshot byte lineage, but CS347 schema v1 did not preserve it. CS347 is now schema v2 and carries:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

CS347 validates that lineage on fresh CS346 replay before CS283 creation, stores it in its receipt, and compares every field again during verification against a freshly verified CS346 receipt.

## Fail-closed properties

- Unverified snapshot inventory is rejected before the CS283 builder is invoked.
- Rehashing an altered CS347 receipt cannot hide snapshot-lineage drift because verification replays CS346 and compares the five fields.
- Final Semantic Approval remains distinct from SemanticPublicationGate authorization.
- `semantic_publication_gate_executed=false` and `semantic_publication_allowed=false` remain mandatory in CS347.
- `genuine_golden_png_created=false`, `publication_ready=false`, and `authoritative=false` remain mandatory.
- No model loading, network fallback, pixel mutation, upload, or publication execution was added.

## Files

Modified:
- `engine/intelligence/qwen_image_final_semantic_approval_to_semantic_publication_execution_request.py`
- `tests/test_phase18_qwen_final_semantic_approval_to_semantic_publication_execution_request.py`

Added:
- `docs/PHASE18_CHANGESET_377_CS347_SEMANTIC_PUBLICATION_REQUEST_SNAPSHOT_LINEAGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_377.md`

Deleted: none.
Dependencies: none.

## Code/test SHA

Exact code-and-test-bearing commit: `0bce98bcd0f3d0d34d2dd13ac5e2906bfaf78c22`.

CI status is recorded in `PHASE18_IMPLEMENTATION_LOG_377.md` after verification is observed.
