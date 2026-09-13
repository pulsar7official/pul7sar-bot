# Phase 18 Implementation Log 363 — Composition Execution Preflight Snapshot Lineage

## Scope and branch safety

Repository: `pulsar7official/pul7sar-bot`

Allowed branch: `phase18/story-intelligence` only.

Starting branch HEAD reviewed before writes: `610d1f8be39c83123c900af77f18b8051143b3db`.

`main` was reviewed separately and was not written, merged, rebased, reset, force-updated, or used as a write target.

## Proven gap

The branch tree established the first downstream contract after CS362 as:

`engine/intelligence/qwen_image_canonical_candidate_composition_execution_preflight.py`

That contract already fresh-replayed `verify_deterministic_composition_request(...)`, reopened the canonical candidate bytes, and verified exact repository-bound deterministic payload bytes. Its receipt nevertheless omitted the exact Qwen-Image generator snapshot-byte lineage carried by CS362.

This meant lineage continuity stopped immediately before executable composition readiness even though the immediate upstream contract still contained the evidence.

## Changes made

### Modified production code

`engine/intelligence/qwen_image_canonical_candidate_composition_execution_preflight.py`

Commit: `e306b809a3afffbbad5dc9f8174a8103f918c98a`

Changes:

- advanced the receipt schema from `v1` to `v2`;
- added strict snapshot-lineage extraction/shape validation;
- sealed `snapshot_byte_inventory_verified`, `snapshot_inventory_sha256`, `snapshot_file_count`, `snapshot_total_bytes`, and Qwen-Image generator `model_revision` into the preflight receipt;
- required the lineage to originate from a successful fresh CS362 deterministic-composition-request replay;
- added a verification-time fresh upstream replay and field-by-field lineage comparison;
- added explicit `SNAPSHOT_LINEAGE_DRIFT` fail-closed behavior;
- preserved all existing candidate-byte, deterministic-payload, renderer-contract, output-isolation, blocker/readiness, and closed-authority behavior;
- added no rendering or publication authority.

### Modified tests

`tests/test_phase18_qwen_image_canonical_candidate_composition_execution_preflight.py`

Commit: `dc8338923b5122a006ede4b8ebaeddf678642b4a`

Changes:

- upgraded the upstream CS362 fixture with exact generator snapshot lineage;
- asserted correct lineage propagation in a READY preflight;
- added rejection coverage for `snapshot_byte_inventory_verified != true`;
- added tamper coverage where `snapshot_inventory_sha256` is changed and the outer receipt digest is recomputed correctly, which must still fail on fresh upstream replay;
- added equivalent recomputed-digest tamper coverage for generator `model_revision`;
- retained existing payload byte-drift, candidate byte-drift, renderer-contract, missing-payload, and output-isolation regressions;
- retained standard-library `unittest`; no dependency was added.

### Added documentation

`docs/PHASE18_CHANGESET_363_COMPOSITION_EXECUTION_PREFLIGHT_SNAPSHOT_LINEAGE.md`

Commit: `08fa60bacce6ad5ee312626bd151671ae886a4f1`

This implementation log was also added as the canonical repository record for CS363.

### Deleted

Nothing.

## Authority and policy preservation

CS363 does not grant or bypass factual/freshness, Entity/Identity, sentiment-neutrality/loser-respect, semantic, generated-layer/composition, visual-quality, Human Visual Review, Golden-quality, Brand/Typography/Presentation, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden materialization, publication-readiness, or external-publication authority.

The preflight continues to require these downstream authorities to remain false at this boundary:

- `composition_executed=false`
- `composed_visual_approved=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `genuine_golden_png_created=false`
- `golden_quality_approved=false`
- `publication_ready=false`

No model download, paid execution fallback, network-model fallback, synthetic inference, authority shortcut, or publication shortcut was introduced.

## Test status

The code-and-test-bearing SHA is `dc8338923b5122a006ede4b8ebaeddf678642b4a`.

Fresh GitHub Actions observation after the implementation completed confirms terminal-green status:

- `Phase 18 Story Intelligence Verification` run `34103410071`, run number `5114`: `completed / success` on `dc8338923b5122a006ede4b8ebaeddf678642b4a`.
- Companion Phase 18 workflows observed on the same SHA also completed successfully: Adaptive Brand Pixel Verification, Data Monument Visual Study, Event Editorial Visual Study, Verified Match Result Visual Study, Tactical Intelligence Visual Study, Result Statement Visual Study, Event Hybrid Context Study, Premium Hybrid Result Visual Study, and Composition Matrix Verification.

This terminal-green record is documentation-only; it grants no new runtime, semantic, visual, Golden, or publication authority.

## Genuine Golden execution status

CS363 is preparatory integrity work. It does not fabricate Qwen inference, a production `canonical_candidate.png`, a CS284-approved real candidate, or a production `genuine_golden_visual.png`.

A genuine Golden PNG still requires a compatible zero-cost execution host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, sufficient RAM/VRAM demonstrated through actual model load/inference, the approved Qwen-Image/Diffusers runtime, and the exact approved already-local pinned generator/verifier assets, with no paid or network model fallback.
