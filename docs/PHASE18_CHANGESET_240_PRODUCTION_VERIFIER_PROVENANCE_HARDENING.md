# Phase 18 Change Set 240 — Production Verifier Provenance Hardening

## Purpose

Change Set 239 made the six production gate replay bindings explicit and fail-closed, but its readiness definition accepted any callable that had a compatible replay signature plus stable verifier ID/version metadata. That was insufficient: a test fixture, receipt echo, or stub could theoretically attach those two attributes and appear structurally ready.

Change Set 240 closes that gap before any fresh-story semantic replay can be treated as production-backed.

## What changed

`engine/intelligence/qwen_image_production_gate_verifier_readiness.py` now requires every registered verifier to declare all of the following metadata in addition to its compatible `(Path, story_snapshot_sha256, receipt)` callable signature:

- `PUL7SAR_VERIFIER_ID`
- `PUL7SAR_VERIFIER_VERSION`
- `PUL7SAR_VERIFIER_GATE_ID` matching the registry gate exactly
- `PUL7SAR_PRODUCTION_BACKED is True`
- `PUL7SAR_SOURCE_MODULE`
- `PUL7SAR_SOURCE_CALLABLE`

The readiness schema is bumped to `pul7sar-phase18-qwen-image-2512-production-gate-verifier-readiness-v2`.

The audit also rejects source metadata that is explicitly test/stub-like (`tests`, `test`, `unittest`, `__main__`, or fixture/stub/fake/mock/dummy/placeholder tokens), rejects duplicate verifier identities, and rejects duplicate `(source_module, source_callable)` bindings across gates.

## Authority boundary

This hardening is still only a wiring/provenance readiness audit. It does **not** execute the source callable, does **not** prove semantic correctness, and does **not** grant generation or publication authority.

Even a fully ready registry remains:

- `production_semantic_replay_executed = false`
- `fresh_story_gates_passed = false`
- `canonical_generation_authorized = false`
- `model_weights_loaded = false`
- `inference_executed = false`
- `genuine_golden_png_created = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`

## Gates preserved

No Fact Lock, Entity/Identity, Sentiment/Neutrality, zero-cost, semantic/layer ownership, semantic-publication, brand, typography, visual critic, or human-review gate was relaxed. The canonical production verifier registry remains empty until real production adapters exist.

## Tests

`tests/test_phase18_qwen_image_production_gate_verifier_readiness.py` now additionally verifies that readiness fails closed for:

- missing provenance metadata;
- a declared gate mismatch;
- test/stub-like source module/callable metadata;
- non-boolean production-backed claims;
- duplicate production source bindings;
- existing incompatible signature, duplicate verifier identity, extra gate, registry-module drift, and forged downstream authority cases.

## Golden PNG status

No CUDA/Qwen inference was executed by this change set and no Golden PNG is claimed. The GPU blocker remains unchanged: a compatible zero-cost NVIDIA CUDA host with native BF16, sufficient live VRAM/system RAM, the exact pinned Qwen Image 2512 snapshot, compatible Diffusers/QwenImagePipeline, and successful sequential CPU offload is still required for genuine runtime qualification and canonical inference.
