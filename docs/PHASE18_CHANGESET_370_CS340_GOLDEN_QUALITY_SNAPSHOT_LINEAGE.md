# Phase 18 Changeset 370 — CS340 Golden-Quality Snapshot Lineage

## Scope

CS370 hardens the existing CS340 continuation contract:

`engine/intelligence/qwen_image_visual_quality_evidence_to_golden_quality_adjudication.py`

No parallel gate is introduced. CS340 remains the established bridge from one exact CS339 visual-quality evidence admission into the existing CS276 Golden-quality adjudicator.

## Proven gap

CS369 made CS339 carry the exact Qwen generator snapshot byte lineage:

- `snapshot_byte_inventory_verified`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

CS340 previously replayed CS339, derived the exact CS272/CS263 lineage, ran CS276, and sealed its Golden-quality verdict, but its own receipt dropped those five generator-provenance fields.

## Change

CS340 schema advances from `v1` to `v2`.

The build path now:

1. freshly verifies CS339;
2. fails closed unless the generator snapshot byte inventory is explicitly verified;
3. validates the snapshot digest/count/byte-total/model-revision shapes;
4. freshly derives the exact CS272 selected by the admitted CS275 lineage;
5. compares all five generator snapshot fields between CS339 and CS272 before any CS276 output directory is created;
6. invokes the existing CS276 adjudicator exactly as before;
7. seals the five generator snapshot fields into the CS340 receipt.

The verification path now:

1. verifies the CS340 outer receipt digest;
2. validates its sealed snapshot lineage;
3. freshly verifies CS339;
4. compares CS340 snapshot lineage to fresh CS339 field-by-field;
5. freshly derives CS272 through the admitted CS275 lineage;
6. compares fresh CS339 to fresh CS272 field-by-field;
7. reverifies CS276 and all existing exact-source bindings.

## Authority preservation

CS370 does not grant Human Visual Review, final composed approval, final semantic approval, Genuine Golden PNG creation, publication readiness, or publication authority.

CS276 remains the only reused Golden-quality adjudicator. Generator identity remains independent from Golden-quality verifier identity. No scores, blockers, evidence, pixels, model execution, network calls, paid service, upload, or publication action is fabricated by CS340.

## Zero-cost / runtime policy

No dependency was added. No model download or network-model fallback was added. No paid execution path was added.

## Tests

The CS340 regression fixture now carries the five generator snapshot fields in both mocked CS339 and mocked CS272. Added coverage verifies:

- successful propagation of all five fields into the CS340 receipt;
- rejection of `snapshot_byte_inventory_verified=false`;
- rejection of `snapshot_inventory_sha256` drift between CS339 and CS272;
- rejection of `model_revision` drift between CS339 and CS272;
- continued rejection of premature Golden authority upstream;
- continued absence of generation, evidence fabrication, network, Human Review, Genuine Golden, upload, and publication shortcuts.

The exact code-and-test-bearing SHA for this changeset is `ac0cde1cd0f1e904d05d026d8e5711e53f657ebe`.
