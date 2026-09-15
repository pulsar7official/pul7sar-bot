# Phase 18 Change Set 367 — CS337 Snapshot Lineage

## Purpose

Harden the existing CS337 continuation (`qwen_image_composed_byte_admission_to_hybrid_surface_semantic_qa.py`) so the exact Qwen-Image generator snapshot-byte provenance sealed by terminal-green CS366/CS336 survives the first post-composition semantic-QA continuation.

## Contract

CS337 must fail closed unless fresh CS336 and fresh CS272 verification agree on all five generator-lineage fields:

- `snapshot_byte_inventory_verified = true`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

The CS337 receipt seals those fields and verification compares them against fresh CS336/CS272 replay after validating the outer receipt digest. Recomputing the outer digest after lineage tampering therefore cannot create authority.

Generator identity remains separate from the existing pinned CS273 semantic-verifier identity. CS367 does not turn the hybrid-surface semantic decision into global semantic-publication authority.

## Preserved gates

CS337 still stops before CS274 visual-quality review and preserves:

- factual/freshness and Entity/Identity requirements upstream;
- sentiment neutrality and loser-respect requirements;
- zero-cost/local-only semantic-verifier isolation;
- composed visual approval closed;
- global semantic approval closed;
- Human Visual Review closed;
- Golden quality/materialization closed;
- publication readiness and authoritative status closed.

No paid fallback, network-model fallback, model download, synthetic inference, publish/upload path, or visual/Golden shortcut is introduced.
