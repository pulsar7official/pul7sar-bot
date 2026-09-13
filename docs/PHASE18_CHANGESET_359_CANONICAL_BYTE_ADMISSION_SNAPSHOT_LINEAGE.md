# Phase 18 Change Set 359 — Canonical Byte Admission Snapshot Lineage

## Purpose

Close the first downstream lineage gap after CS358 without adding a parallel approval gate.

CS358 seals the exact approved local Qwen snapshot-byte inventory into `canonical_candidate_handoff.json`. The existing CS303 canonical candidate byte-admission contract replayed that handoff and preserved candidate bytes, story identity, model revision, cost mode, and authority closure, but its own admission receipt did not carry the snapshot inventory. CS359 upgrades that existing contract so the same model-byte lineage remains first-class evidence when the exact candidate is admitted for post-generation QA.

## Contract change

`qwen_image_canonical_candidate_byte_admission.py` now emits schema `pul7sar-phase18-qwen-image-2512-canonical-candidate-byte-admission-v3` and requires a replay-verified CS358 handoff to provide:

- `snapshot_byte_inventory_verified=true`;
- `snapshot_inventory_sha256`;
- `snapshot_file_count`;
- `snapshot_total_bytes`;
- `model_revision` equal to the handoff model revision.

The byte-admission receipt seals that compact evidence into its own digest. Verification then replays the bound CS358 handoff, extracts fresh inventory evidence, and requires exact equality with the sealed admission receipt. Recomputing the outer receipt digest after tampering therefore cannot manufacture valid model-byte lineage.

## Authority preservation

This is lineage propagation, not semantic or publication approval. The existing factual/freshness, Entity/Identity, sentiment neutrality/loser-respect, semantic QA, generated-layer/composition QA, visual quality, Golden quality, Human Visual Review, Brand/Typography/Presentation, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden materialization, and publication-readiness gates remain unchanged.

The admission receipt continues to require `$0-local`, `network_allowed=false`, `local_files_only=true`, and keeps `semantic_approved`, `human_visual_review_approved`, `golden_quality_approved`, `genuine_golden_png_created`, and `publication_ready` false.

No model download, network model fallback, paid fallback, synthetic inference, upload, publication shortcut, or publication authority is introduced.

## Regression intent

Tests cover successful lineage propagation, missing inventory authority, revision drift, and inventory tampering after admission with a deliberately recomputed outer receipt digest. Existing candidate-byte, symlink, premature-authority, and output-immutability regressions remain in place.
