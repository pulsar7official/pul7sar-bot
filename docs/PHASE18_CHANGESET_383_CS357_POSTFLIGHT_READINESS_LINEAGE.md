# Phase 18 Changeset 383 — CS357 Postflight CUDA Readiness Lineage

## Scope

This changeset advances the zero-cost Qwen canonical-inference path without creating or claiming a Genuine Golden PNG. It preserves `main` isolation and modifies only `phase18/story-intelligence`.

## Problem closed

CS382 sealed the exact CS351 `static-readiness.json` byte binding into the CS354 inventory-bound launch manifest. CS357 launch-to-output attestation replayed that manifest, so readiness was checked indirectly, but the postflight attestation did not expose the exact readiness binding as explicit downstream provenance.

That omission made downstream auditability weaker than the pre-inference chain: a consumer could prove the launch manifest and model-byte inventory, but could not inspect a first-class postflight field showing which exact CS351 readiness receipt had authorized the load attempt.

## Implementation

`engine/intelligence/qwen_image_launch_to_output_attestation.py` now:

- upgrades the attestation schema from v1 to v2;
- imports the CS382 `READINESS_FIELD` from the inventory-bound launch manifest contract;
- validates the exact readiness binding (`repository_relative_path`, `sha256`, `byte_size`);
- copies that binding into `static_readiness_receipt` in the postflight attestation;
- requires `static_readiness_receipt_verified=true`;
- on every attestation verification, replays the CS354 manifest first, which independently reopens and semantically validates the CS351 readiness receipt, then compares the postflight readiness evidence against the freshly replayed launch manifest;
- rejects path, digest, byte-size, authority, or receipt drift fail-closed.

No Qwen model load, inference, pixel creation, upload, publication, semantic approval, human approval, Golden approval, or publication authority is added here.

## Tests

`tests/test_phase18_qwen_image_launch_to_output_attestation.py` now covers:

- acceptance of an exact readiness binding;
- rejection of missing readiness evidence;
- rejection of invalid readiness digest;
- rejection of an absolute/out-of-repository-style readiness path at the evidence layer;
- static production assertions that the attestation uses the inventory/readiness-bound manifest replay and exposes explicit readiness verification;
- all existing model-byte, story, settings, zero-cost/network, and premature-authority regression coverage.

## Authority preservation

The attestation continues to require all downstream authority fields to remain false:

- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`

This changeset improves evidence continuity only. It does not bypass factual, identity, sentiment, semantic-publication, visual-quality, Human Review, Brand/Typography, Final Composed, Final Semantic, Genuine-Golden materialization, or publication-readiness gates.
