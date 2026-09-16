# Phase 18 Change Set 366 — CS336 Snapshot Lineage

## Purpose

Harden the existing CS336 precomposition-to-composed-byte-admission continuation so the exact Qwen-Image generator snapshot-byte lineage already sealed by CS365/CS272 survives the CS336 wrapper boundary.

This Change Set does not add a parallel gate and does not grant semantic, visual, Human Review, Golden, Genuine-Golden, or publication authority.

## Proven gap

Before CS366, CS336 independently reverified CS271 and CS272 and rebound the exact composed PNG bytes, but its own success receipt did not preserve these CS365 lineage fields:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

Therefore an otherwise valid CS336 receipt could not itself prove which approved local Qwen-Image snapshot bytes generated the admitted composed candidate.

## Contract change

The existing CS336 schema is upgraded from:

`pul7sar-phase18-precomposition-to-composed-byte-admission-v1`

to:

`pul7sar-phase18-precomposition-to-composed-byte-admission-v2`

CS336 now:

1. requires valid generator snapshot lineage from freshly verified CS271;
2. requires the same lineage from freshly verified CS272;
3. compares CS271 and CS272 lineage field-by-field;
4. seals the exact five lineage fields in its own receipt;
5. during CS336 verification, freshly reverifies CS271 and CS272 and compares both against the sealed CS336 lineage;
6. rejects lineage drift even when an attacker recomputes the outer CS336 `receipt_sha256`.

## Fail-closed requirements

A successful CS336 receipt requires:

- `snapshot_byte_inventory_verified = true`;
- a 64-hex `snapshot_inventory_sha256`;
- positive integer `snapshot_file_count`;
- positive integer `snapshot_total_bytes`;
- non-empty `model_revision`;
- exact equality of all five fields across fresh CS271, fresh CS272, and the sealed CS336 receipt.

Any mismatch raises `SNAPSHOT_LINEAGE_DRIFT` and stops the continuation.

## Preserved authority boundary

The following remain false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`
- `authoritative`

CS366 changes provenance continuity only. It does not alter factual/freshness, Entity/Identity, sentiment/loser-respect, zero-cost/offline, semantic-publication, visual-quality, Golden-quality, Human Visual Review, Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine-Golden materialization, or publication-readiness authority.

## Zero-cost and generation boundary

No model download, network-model fallback, paid inference fallback, synthetic inference, retry loop, publication call, or downstream approval shortcut is introduced.

This Change Set does not claim genuine Qwen-Image inference, a production `canonical_candidate.png`, or a `genuine_golden_visual.png`.
