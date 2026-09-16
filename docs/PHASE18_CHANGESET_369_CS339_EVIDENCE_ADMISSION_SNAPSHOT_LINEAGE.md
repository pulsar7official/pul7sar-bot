# Phase 18 Changeset 369 — CS339 Evidence-Admission Snapshot Lineage

## Proven gap

The existing CS339 continuation in `engine/intelligence/qwen_image_visual_quality_review_request_to_evidence_admission.py` is the first branch-local consumer after CS338. It independently reverifies CS338 and CS274, admits one repository-bound external manual visual-quality review through the existing CS275 evidence gate, independently reverifies CS275, and stops before CS276 Golden-quality adjudication.

CS368 sealed exact Qwen-Image generator snapshot provenance into CS338, but CS339 previously dropped that provenance from its own receipt.

## Change

CS339 advances from schema `v1` to `v2` and now preserves:

- `snapshot_byte_inventory_verified`;
- `snapshot_inventory_sha256`;
- `snapshot_file_count`;
- `snapshot_total_bytes`;
- `model_revision`.

Construction requires a freshly verified CS338 whose snapshot inventory is explicitly verified and whose lineage fields have valid fail-closed shapes. Verification replays the exact bound CS338 and compares the five fields individually. Recomputing CS339's outer `receipt_sha256` after tampering therefore cannot conceal generator-lineage drift.

Generator identity remains independent from the admitted external visual-review evidence and from CS274/CS275 review semantics. This changes provenance continuity only; it grants no visual-quality approval, Human Review, Golden, semantic-publication, publication, or authoritative status.

## Regression coverage

The CS339 tests now cover:

- exact five-field propagation into evidence admission;
- rejection of `snapshot_byte_inventory_verified = false` before CS275 construction;
- inventory-digest tampering after recomputing the outer receipt digest;
- model-revision tampering after recomputing the outer receipt digest;
- continued premature-authority rejection;
- continued absence of generation, scoring, network-model, CS276, and publication shortcuts.

No dependency was added or changed.
