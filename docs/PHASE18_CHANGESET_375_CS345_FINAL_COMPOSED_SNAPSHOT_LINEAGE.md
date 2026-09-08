# Phase 18 Changeset 375 — CS345 Final-Composed Snapshot Lineage

## Purpose

Close the proven generator-byte provenance gap in the existing CS345 continuation:

`engine/intelligence/qwen_image_final_presentation_evidence_to_final_composed_visual_approval.py`

CS345 is the first existing branch-local consumer after CS344/CS280. It freshly replays CS344 and its exact admitted CS280 Final Presentation Review evidence, reconstructs the exact CS273 semantic-QA lineage, and invokes the repository's existing CS281 deterministic Final Composed Visual Approval contract.

Before this changeset, CS345 schema v1 could grant `composed_visual_approved=true` without carrying the exact five-field Qwen generator snapshot provenance already present in CS344.

## Production hardening

Schema upgraded:

`pul7sar-phase18-final-presentation-evidence-to-final-composed-visual-approval-v1`

->

`pul7sar-phase18-final-presentation-evidence-to-final-composed-visual-approval-v2`

CS345 now requires, preserves, and freshly verifies:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

The continuation validates the fresh CS344 generator snapshot lineage before CS281 output creation. Its own receipt carries the same five fields, and receipt verification freshly replays CS344 and compares the lineage field-by-field. Recomputing the outer CS345 `receipt_sha256` therefore cannot hide snapshot-inventory or model-revision drift.

Generator identity remains explicitly independent from Final Composed Visual Approval identity/authority.

## Existing gates preserved

This changeset does not alter pixels, execute Qwen inference, create a new visual review, fabricate scores/verdicts, or bypass any upstream gate. Existing exact CS280, CS273, and CS281 bindings remain in force.

CS345 may grant only the existing deterministic Final Composed Visual Approval authority after the required upstream approvals. It still keeps:

- `semantic_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

Final semantic approval, SemanticPublicationGate, Genuine Golden PNG materialization, publication readiness, and publication execution remain independent and fail-closed.

Factual/freshness correctness, Entity/Identity verification, sentiment neutrality/loser respect, zero-cost policy, hybrid semantic QA, visual-quality review/evidence, Human Visual Review, Final Presentation Review, exact-brand integrity, and typography integrity remain upstream prerequisites and are not weakened.

## Tests added/updated

`tests/test_phase18_qwen_final_presentation_evidence_to_final_composed_visual_approval.py` now covers:

- successful propagation of all five generator snapshot fields;
- fail-before-CS281 when `snapshot_byte_inventory_verified=false`;
- `snapshot_inventory_sha256` tampering rejected after recomputing the outer receipt digest;
- `model_revision` tampering rejected after recomputing the outer receipt digest;
- presentation rejection remains fail-closed;
- premature semantic authority remains rejected;
- exact CS280 receipt binding remains required;
- no Qwen generation, model download, final semantic shortcut, Genuine-Golden shortcut, network fallback, upload, or publication shortcut is introduced.

## Commits

- Production hardening: `abe66172ddea3731e9b4f57b5ece0daa491b77d5`
- Exact code-and-test-bearing SHA: `bd0d9f05e796ac4ea4ab31c55d7a1f0aad6f8aa4`

## CI state at documentation time

`Phase 18 Story Intelligence Verification` runs for exact code-and-test-bearing SHA `bd0d9f05e796ac4ea4ab31c55d7a1f0aad6f8aa4` were still in progress when this changeset document was created. No terminal-green claim is made here until the exact workflow completes successfully.

## Genuine Golden runtime status

No Genuine Qwen-Image inference or production Golden PNG was produced by this changeset. The current execution environment is CPU-only (`torch=2.10.0+cpu`, CUDA unavailable, no CUDA runtime, no native CUDA BF16, and no `nvidia-smi`). Genuine generation remains blocked until a compatible zero-cost NVIDIA CUDA host and the approved already-local pinned generator/verifier assets are available.