# Phase 18 Changeset 380 — CS350 Publication-Readiness Snapshot Lineage

## Scope

Harden the existing `CS349 / CS285 Genuine Golden materialization -> CS350 / CS286 publication-readiness` boundary without creating a parallel readiness or publication authority.

## Proven gap

`CS349` schema v2 carries the exact five-field Qwen generator snapshot lineage:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

The existing `CS350` schema v1 independently replayed CS349 and CS285 and reused CS286, but discarded that generator provenance at the point where `publication_ready=true` could be admitted.

## Production change

`engine/intelligence/qwen_image_genuine_golden_materialization_to_publication_readiness.py`

- raises CS350 schema from v1 to v2;
- validates all five snapshot-lineage fields on the freshly verified CS349 receipt before CS286 can execute;
- copies those exact fields into the CS350 receipt;
- replays CS349 during CS350 verification and compares all five fields one-by-one;
- rejects a rehashed outer CS350 receipt if generator snapshot digest or model revision drifts from the freshly verified CS349 lineage;
- keeps generator identity independent from CS286 publication-readiness authority;
- reuses existing CS286 exactly once and preserves the existing exact Genuine Golden byte binding;
- performs no generation, pixel mutation, semantic-publication decision, upload, or publication side effect.

## Authority preservation

CS350 may admit `publication_ready=true` only after the existing CS286 contract successfully verifies the exact CS285 Genuine Golden artifact. It still records `authoritative=false`; no external publication side effect is created by this continuation.

All factual/freshness, Entity/Identity, sentiment neutrality / loser-respect, zero-cost, semantic QA, visual-quality, Human Visual Review, Final Presentation / Brand / Typography, Final Composed, Final Semantic, SemanticPublicationGate, and Genuine-Golden byte-identity requirements remain upstream prerequisites.

## Regression coverage

`tests/test_phase18_qwen_genuine_golden_materialization_to_publication_readiness.py`

- successful five-field lineage propagation;
- unverified snapshot inventory fails before CS286;
- premature upstream readiness still fails;
- exact CS285 receipt binding remains enforced;
- CS286 Genuine Golden byte-binding drift remains rejected;
- rehashed `snapshot_inventory_sha256` tampering is rejected against fresh CS349 replay;
- rehashed `model_revision` tampering is rejected against fresh CS349 replay;
- generation/network/materialization/publication shortcuts remain forbidden in CS350.

Exact code-and-test-bearing commit: `34d358f6dcfc9666cb8886c78f003c7632c2896a`.
