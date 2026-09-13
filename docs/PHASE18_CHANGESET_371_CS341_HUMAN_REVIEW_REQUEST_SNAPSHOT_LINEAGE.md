# Phase 18 Changeset 371 — CS341 Human-Review Request Snapshot Lineage

## Purpose

Preserve the exact five-field Qwen generator snapshot byte provenance when an independently verified successful CS340/CS276 Golden-quality adjudication is continued into the existing CS277 Human Visual Review request contract.

## Proven gap

CS340 schema v2 already carries:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

The existing CS341 schema v1 replayed CS340 and its exact selected CS276, then opened CS277, but dropped those generator provenance fields from the CS341 receipt. That created a downstream lineage discontinuity immediately before the Human Visual Review path.

## Implementation

`engine/intelligence/qwen_image_golden_quality_adjudication_to_human_visual_review_request.py`

- schema upgraded from v1 to v2;
- validates exact generator snapshot lineage on freshly verified CS340 before any CS277 output directory is created;
- copies the five fields into CS341 receipt;
- revalidates CS341 receipt lineage shape;
- freshly replays CS340 during verification and compares the five fields field-by-field;
- keeps generator identity independent from Human Visual Review identity;
- continues to reuse existing CS276 and CS277 contracts rather than creating parallel authority.

## Regression coverage

`tests/test_phase18_qwen_golden_quality_adjudication_to_human_visual_review_request.py`

- positive propagation of all five lineage fields;
- unverified snapshot inventory fails before CS277 creation;
- snapshot inventory SHA tampering is rejected even after recomputing outer receipt digest;
- model revision tampering is rejected even after recomputing outer receipt digest;
- existing rejected-Golden, premature-Human-authority, and no-generation/network/publication-shortcut coverage retained.

## Authority boundaries

CS371 does not perform a human verdict and does not create a Genuine Golden PNG. It may only request Human Visual Review after the existing CS276 Golden/Elite result has been independently verified. It leaves:

- `human_visual_review_executed=false`
- `human_visual_review_approved=false`
- `composed_visual_approved=false`
- `semantic_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

Factual/freshness, Entity/Identity, sentiment neutrality/loser respect, zero-cost policy, semantic QA, visual quality, Human Review, brand/typography, final composed approval, final semantic approval, SemanticPublicationGate, Genuine Golden materialization, and publication remain independent and fail-closed.

## Zero-cost and runtime policy

No model download, paid fallback, network-model fallback, synthetic inference, Human verdict fabrication, Golden PNG fabrication, upload, or publication shortcut is introduced.
