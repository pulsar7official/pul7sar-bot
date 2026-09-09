# Phase 18 Changeset 378 — CS348 Semantic Publication Gate Snapshot Lineage

## Purpose

Harden the existing CS348 continuation so the exact pinned Qwen generator snapshot provenance carried by CS347 survives the transition through the real CS284 SemanticPublicationGate execution contract.

## Existing boundary

CS348 already replays the exact CS347 publication-execution request, reopens the exact selected CS283 receipt, executes the existing CS284 semantic-publication gate using repository-bound evidence, and preserves CS284's allow/deny result exactly. Before this changeset, CS348 schema v1 did not carry the generator snapshot provenance that CS347 v2 already provided.

## Change

CS348 schema is raised from v1 to v2. The receipt now preserves and verifies:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

CS348 rejects an unverified or malformed snapshot lineage before CS284 execution. Verification replays CS347 fresh and compares all five fields exactly, so changing the snapshot digest or model revision and recomputing only the outer CS348 receipt digest remains fail-closed.

## Authority separation

This changeset does not create or alter SemanticPublicationGate authority. `semantic_publication_allowed` is still sourced only from the existing CS284 execution result. Generator identity remains distinct from semantic-publication verifier identity.

The following states remain false at CS348:

- `genuine_golden_png_created`
- `publication_ready`
- `authoritative`

No image generation, pixel mutation, network-model fallback, upload, publish, or Genuine-Golden materialization is performed here.

## Tests

The CS348 test fixture now represents the upstream CS347 v2 snapshot lineage. Regressions cover:

- successful five-field propagation;
- rejection of `snapshot_byte_inventory_verified=false` before CS284 execution;
- snapshot inventory digest tampering even after recomputing the outer CS348 digest;
- model revision tampering even after recomputing the outer CS348 digest;
- preservation of allow and deny decisions from CS284;
- existing request-only and CS283 binding protections;
- forbidden generation/network/publication shortcuts.

## Genuine Golden status

This changeset materially reduces the remaining provenance gap immediately before Genuine-Golden materialization, but it does not fabricate a PNG. Real Qwen-Image inference remains separately blocked unless a compatible zero-cost CUDA/BF16 execution host and approved pinned local assets are available.
