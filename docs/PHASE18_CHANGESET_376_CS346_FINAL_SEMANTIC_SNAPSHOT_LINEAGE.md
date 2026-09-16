# Phase 18 Changeset 376 — CS346 Final-Semantic Snapshot Lineage

## Purpose

Close the proven generator-byte provenance gap in the existing CS346 continuation:

`engine/intelligence/qwen_image_final_composed_visual_approval_to_final_semantic_approval.py`

CS346 is the existing branch-local continuation from CS345 Final Composed Visual Approval to the repository's existing CS282 Final Semantic Approval contract. Before this changeset, schema v1 could grant `semantic_approved=true` while dropping the exact five-field Qwen generator snapshot provenance already carried by CS345.

## Production hardening

Schema upgraded:

`pul7sar-phase18-final-composed-visual-approval-to-final-semantic-approval-v1`

->

`pul7sar-phase18-final-composed-visual-approval-to-final-semantic-approval-v2`

CS346 now requires, preserves, and freshly verifies:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

The fresh CS345 receipt must expose valid generator snapshot lineage before CS282 output creation. The CS346 receipt carries the same fields. During CS346 verification, CS345 is freshly replayed and all five fields are compared field-by-field, so recomputing the outer CS346 `receipt_sha256` cannot conceal inventory or model-revision drift.

Generator identity remains explicitly independent from Final Semantic Approval identity/authority.

## Existing gates preserved

This changeset does not alter pixels, execute Qwen inference, create semantic evidence, fabricate review outcomes, invoke SemanticPublicationGate, materialize a Genuine Golden PNG, upload, or publish.

Existing exact CS345 -> CS281 -> CS282 binding and replay remain in force.

CS346 retains the repository's existing final-semantic authority only after all required upstream approvals and exact lineage checks. It still keeps:

- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

SemanticPublicationGate, Genuine Golden materialization, publication readiness, and publication execution remain independent and fail-closed.

Factual/freshness correctness, Entity/Identity verification, sentiment neutrality/loser respect, zero-cost policy, hybrid semantic QA, visual-quality review/evidence, Human Visual Review, Final Presentation Review, brand integrity, typography integrity, and Final Composed Visual Approval remain upstream prerequisites and are not weakened.

## Tests added/updated

`tests/test_phase18_qwen_final_composed_visual_approval_to_final_semantic_approval.py` now covers:

- successful propagation of all five generator snapshot fields;
- fail-before-CS282 when `snapshot_byte_inventory_verified=false`;
- `snapshot_inventory_sha256` tampering rejected after recomputing the outer receipt digest;
- `model_revision` tampering rejected after recomputing the outer receipt digest;
- missing final-composed approval remains fail-closed;
- premature semantic authority upstream remains rejected;
- exact CS281 receipt binding remains required;
- CS282 cannot grant Genuine-Golden or publication authority;
- no Qwen generation, model download, SemanticPublicationGate shortcut, Genuine-Golden shortcut, network fallback, upload, or publication shortcut is introduced.

## Commits

- Production hardening: `2c82b672830bf583561838540f4995a1a9436e98`
- Exact code-and-test-bearing SHA: `2ff1ab653fdcd92989087ba42136f681b3d271c3`

## CI state at documentation time

GitHub Actions is evaluated against exact code-and-test-bearing SHA `2ff1ab653fdcd92989087ba42136f681b3d271c3`. No terminal-green claim is made until the exact Story Intelligence workflow completes successfully.

## Genuine Golden runtime status

No Genuine Qwen-Image inference or production Golden PNG was produced by this changeset. The execution environment remains CPU-only (`torch=2.10.0+cpu`, CUDA unavailable, no CUDA runtime, no native CUDA BF16, and no `nvidia-smi`). Genuine generation remains blocked until a compatible zero-cost NVIDIA CUDA host and the approved already-local pinned generator/verifier assets are available.