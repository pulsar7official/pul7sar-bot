# Phase 18 Changeset 373 — CS343 Final-Presentation Request Snapshot Lineage

## Scope

Harden the existing CS343 continuation at `engine/intelligence/qwen_image_human_visual_review_evidence_to_final_presentation_review_request.py`. CS343 is the proven branch-local consumer that takes approved CS342/CS278 Human Visual Review evidence into the repository's existing CS279 Final Presentation Review Request contract.

## Proven gap

CS342 schema v2 carries the exact five-field Qwen generator snapshot byte lineage, but CS343 schema v1 replayed CS342 without preserving that lineage in its own receipt. This created a provenance discontinuity immediately before final presentation/brand/typography review.

## Contract changes

- Upgrade CS343 schema from v1 to v2.
- Require valid `snapshot_byte_inventory_verified=true` on freshly verified CS342 before any CS279 output is created.
- Validate and preserve:
  - `snapshot_byte_inventory_verified`
  - `snapshot_inventory_sha256`
  - `snapshot_file_count`
  - `snapshot_total_bytes`
  - `model_revision`
- During CS343 verification, freshly replay CS342 and compare all five fields field-by-field.
- Keep Qwen generator identity separate from Human Visual Review and Final Presentation Review identity.
- Continue using the existing CS279 contract and exact composed PNG binding.

## Authority boundaries preserved

CS373 does not perform image generation, download a model, fabricate a Human or presentation verdict, self-approve brand/typography, grant composed visual approval, grant semantic approval, create a Genuine Golden PNG, or publish/upload anything.

Final Presentation Review, exact brand integrity, typography integrity, final composed approval, final semantic approval, SemanticPublicationGate, Genuine Golden materialization, publication readiness, and publication execution remain independent and fail-closed.

## Regression coverage

The CS343 test fixture now carries exact generator snapshot lineage. Tests cover successful five-field propagation, rejection of an unverified snapshot before CS279 output creation, rejection of snapshot inventory digest drift after outer-receipt digest recomputation, rejection of model-revision drift after outer-receipt digest recomputation, human rejection, CS278 story/PNG drift, premature presentation/final authority, and absence of generation/network/publication shortcuts.
