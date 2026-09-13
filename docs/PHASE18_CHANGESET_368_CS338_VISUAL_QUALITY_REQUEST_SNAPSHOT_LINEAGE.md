# Phase 18 Change Set 368 — CS338 Visual-Quality Request Snapshot Lineage

## Purpose

Preserve the exact approved Qwen-Image generator snapshot byte lineage when the existing CS338 continuation advances an independently reverified CS337/CS273 semantic pass into the existing CS274 visual-quality review-request contract.

This change closes a proven provenance gap in the existing downstream consumer. It does not introduce a parallel gate and it does not grant visual-quality, Human Review, Golden, semantic-publication, publication, or authoritative status.

## Proven gap

Before CS368, `qwen_image_hybrid_surface_semantic_qa_to_visual_quality_review_request.py` freshly reverified CS337, replayed the exact CS273 selected by CS337, built and reverified CS274, and bound the exact composed PNG and receipt bytes. However, its own CS338 receipt did not preserve these generator-snapshot fields already sealed by CS337:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

That caused exact generator-byte provenance to terminate at the boundary immediately before visual-quality review.

## Implementation

CS338 schema advances from `v1` to `v2`.

The existing CS338 receipt now copies the five generator snapshot fields from the freshly verified CS337 receipt. Construction and verification both require `snapshot_byte_inventory_verified is True`, validate the field shapes, and compare all five fields against fresh CS337 verification field-by-field.

The receipt policy explicitly records that generator snapshot lineage must survive the visual-quality request boundary and that generator identity is independent from semantic/visual verifier identity.

CS273 remains the semantic-verifier receipt. CS368 deliberately does not manufacture generator provenance inside CS273 or treat semantic-verifier identity as generator identity.

## Fail-closed properties

A modified CS338 snapshot inventory digest or model revision is rejected even when an attacker recomputes the outer `receipt_sha256`, because verification freshly replays CS337 and compares the lineage fields directly.

An unverified upstream snapshot is rejected before CS274 construction.

Existing exact-story, exact-composed-PNG, exact-CS273, exact-CS274, no-network, no-generation, no-scoring, no-publication, and downstream-authority constraints remain in force.

## Authority boundary

CS368 may only establish that a visual-quality review request is ready. It keeps the following false:

- `visual_quality_review_executed`
- `visual_quality_review_approved`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`
- `authoritative`

It does not execute CS275, Human Review, Golden adjudication/materialization, SemanticPublicationGate, or publication.

## Zero-cost rule

No dependency, model download, paid service, network-model fallback, generation retry, external publication, or GPU requirement is introduced by this change set.
