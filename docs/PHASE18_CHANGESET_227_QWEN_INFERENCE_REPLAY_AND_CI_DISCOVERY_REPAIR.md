# Phase 18 Change Set 227 — Qwen Inference Replay and CI Discovery Repair

## Purpose

Change Set 226 added a real single-inference engineering probe for the exact pinned `Qwen/Qwen-Image-2512` snapshot, but its regression module was written as free `pytest` functions while the canonical Phase 18 CPU validator executes `python -m unittest discover`. The module was imported, but its test functions were not part of the canonical discovered test count.

Separately, the v1 inference receipt verifier checked SHA integrity and authority boundaries but did not fully prove that a claimed successful measurement was internally consistent with the child exit code, actual offload mode, native BF16 state, and PNG evidence.

Change Set 227 repairs both gaps before any further runtime-floor work.

## Canonical CI discovery

`tests/test_phase18_qwen_image_inference_measurement.py` is now a `unittest.TestCase` suite, matching the established Phase 18 test contract. The single-inference regressions are therefore executed by `tools/phase18_cpu_validate.py` rather than merely imported.

## Receipt replay hardening

`verify_inference_measurement_receipt()` now additionally requires:

- the exact pinned Qwen Image model revision in the snapshot path;
- SHA-256-shaped upstream load evidence identifiers;
- fixed probe guidance in addition to width/height/steps/seed;
- success status, `inference_succeeded`, `single_inference_proven`, and child exit code to agree;
- successful measurements to report `QwenImagePipeline`;
- actual offload mode to be `sequential_cpu`;
- native BF16 to be proven;
- output PNG path, SHA-256, and positive byte size to be present;
- successful observations to contain no failure fields.

Recomputing the outer receipt SHA is therefore insufficient to turn a failed or differently-executed probe into a successful measurement.

## Safety boundary

This change does not grant runtime qualification or canonical generation. The probe remains engineering measurement only:

- `canonical_pixels_reusable=false`
- `runtime_floor_proven=false`
- `local_runtime_qualified=false`
- `canonical_generation_authorized=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`

No Fact, Identity, Sentiment/Neutrality, `$0-local`, SemanticPublication, Brand/Typography, or Golden quality gate is weakened.

## Files

Modified:

- `engine/intelligence/qwen_image_inference_measurement.py`
- `tests/test_phase18_qwen_image_inference_measurement.py`

Added:

- `docs/PHASE18_CHANGESET_227_QWEN_INFERENCE_REPLAY_AND_CI_DISCOVERY_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_227.md`

Deleted: none.

`main` and `main.py` are untouched.
