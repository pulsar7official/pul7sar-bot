# Phase 18 Change Set 365

## CS365 — Composed Candidate Byte Admission Snapshot Lineage

### Objective

Preserve the exact Qwen-Image generator snapshot-byte lineage across the existing CS271 -> CS272 transition, so that admitting the exact composed PNG for post-composition QA cannot sever provenance from the exact generator bytes that produced the canonical candidate.

### Proven gap

`engine/intelligence/qwen_image_composed_candidate_byte_admission.py` is the direct downstream consumer of `verify_one_shot_composition_execution(...)`. Before CS365 it freshly reverified CS271, rebound the exact composed PNG, checked canvas dimensions, and kept all semantic/visual/Golden/publication authorities closed, but its v1 receipt did not preserve or independently compare the five generator snapshot-lineage fields already sealed by CS271.

### Production changes

- advanced CS272 receipt schema from `pul7sar-phase18-qwen-image-composed-candidate-byte-admission-v1` to `...-v2`;
- requires `snapshot_byte_inventory_verified=true` on fresh CS271 verification;
- strictly validates `snapshot_inventory_sha256`, `snapshot_file_count`, `snapshot_total_bytes`, and `model_revision`;
- seals all five generator snapshot-lineage fields into the CS272 receipt;
- on CS272 verification, freshly replays CS271, extracts the trusted lineage again, and compares all five sealed fields field-by-field;
- rejects lineage tampering even if the outer CS272 `receipt_sha256` is recomputed correctly;
- retains exact composed-PNG byte reopening, canvas-dimension binding, CS271 receipt-byte binding, and all downstream authority closures.

### Regression coverage

The CS272 test fixture now carries verified generator lineage and adds coverage for:

- exact lineage propagation;
- rejection of unverified snapshot inventory;
- rejection of snapshot inventory SHA tampering after recomputing the outer receipt digest;
- rejection of model revision tampering after recomputing the outer receipt digest;
- retention of composed-byte drift, CS271-byte drift, dimension drift, premature Golden authority, and output-reuse regressions.

### Authority preservation

CS365 grants only composed-candidate byte-admission evidence. It does not grant composed visual approval, semantic approval, Human Visual Review approval, Golden-quality approval, Genuine Golden PNG creation, publication readiness, or external publication.

Factual/freshness, Entity/Identity, sentiment neutrality and loser-respect, semantic QA, generated-layer/composition QA, visual-quality, Human Visual Review, Golden-quality, Brand/Typography/Presentation, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden materialization, and publication gates remain fail-closed.

No model download, paid fallback, network-model fallback, synthetic inference, retry shortcut, or publication shortcut is introduced.

### Genuine Golden status

This is safe preparatory work. It does not claim genuine Qwen-Image inference, a production `canonical_candidate.png`, or a `genuine_golden_visual.png`. Real generation remains contingent on a compatible zero-cost CUDA/BF16 host and the exact approved local pinned generator/verifier assets.
