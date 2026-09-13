# Phase 18 Changeset 379 — CS349 Genuine-Golden Materialization Snapshot Lineage

## Scope

Harden the existing `qwen_image_semantic_publication_gate_to_genuine_golden_materialization.py` continuation only. No parallel materialization gate is introduced.

## Proven gap

CS348 v2 carries exact Qwen generator snapshot provenance through the actual CS284 SemanticPublicationGate decision. CS349 v1 required an allowed CS348 result and reused the existing CS285 materialization contract, but it dropped the five generator snapshot-lineage fields at the boundary where `genuine_golden_png_created` can become true.

The affected fields are:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

## Change

CS349 is raised to schema v2. It now:

1. Freshly verifies the exact CS348 receipt.
2. Requires valid five-field generator snapshot lineage before CS285 can be invoked.
3. Preserves the exact lineage into the CS349 materialization receipt.
4. Freshly replays CS348 during CS349 verification and compares all five fields field-by-field.
5. Keeps generator identity independent from CS285 materialization identity.
6. Reuses the existing CS285 contract exactly once and preserves exact source-composed-PNG byte identity.
7. Does not grant publication readiness or downstream authority.

## Security / authority effect

A caller cannot alter generator snapshot digest or model revision inside a CS349 receipt and hide the change by recomputing only the outer receipt digest. Fresh CS348 replay exposes such lineage drift.

The following remain mandatory upstream/downstream boundaries rather than shortcuts:

- factual/freshness verification
- Entity/Identity verification
- sentiment neutrality and loser-respect
- zero-cost/offline model rules
- semantic QA
- visual-quality evidence/adjudication
- Human Visual Review
- Final Presentation / Brand / Typography
- Final Composed approval
- Final Semantic approval
- actual CS284 SemanticPublicationGate allow decision
- existing CS285 byte-preserving materialization
- separate publication-readiness / publication authority downstream

## Resulting authority state

CS349 may set `genuine_golden_png_created=true` only after a verified allowed CS348/CS284 chain and successful CS285 byte-preserving materialization. It still requires:

- `publication_ready=false`
- `authoritative=false`

No new pixels are generated or mutated by CS349.
