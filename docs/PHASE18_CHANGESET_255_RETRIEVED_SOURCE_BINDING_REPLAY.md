# Phase 18 Change Set 255 — Retrieved Source Binding Replay

## Purpose

Change Set 254 byte-bound retrieved source captures, but Change Set 253 consumed the bound manifest without reopening the captured source files. That left a time-of-check/time-of-use gap: source bytes could change after the binding receipt was emitted but before evidence compilation.

Change Set 255 closes that gap fail-closed.

## Added

- `engine/intelligence/qwen_image_retrieved_source_binding_replay.py`
  - validates the exact Change Set 254 binding receipt shape and schema;
  - rejects any downstream authority bit set true in the binding receipt;
  - re-hashes the bound story manifest and requires exact SHA-256 and byte-size agreement;
  - reopens every current capture file under the declared source root;
  - repeats path-containment checks;
  - requires current source SHA-256 and byte size to match both the binding receipt and bound manifest;
  - requires exact source-set agreement;
  - only after successful replay can it invoke Change Set 253 evidence compilation.
- `tests/test_phase18_qwen_image_retrieved_source_binding_replay.py`
  - verifies normal replay;
  - proves post-binding source mutation is rejected;
  - proves bound-manifest mutation is rejected;
  - proves forged downstream authority is rejected;
  - verifies six-evidence compilation only occurs after successful replay.
- `tools/phase18_replay_bound_sources_and_compile_evidence.py`
  - CPU-only operational CLI for replay + evidence compilation.

## Authority boundary

This change does **not** execute Change Set 252 production gate receipts, Change Set 237 freshness admission, Change Set 238 semantic replay, canonical Qwen generation, model loading, pixel creation, Visual Critic, Human Review, Golden approval, brand/typography approval, or publication.

The following remain false at this stage:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `canonical_generation_authorized`
- `inference_executed`
- `genuine_golden_png_created`
- `publication_ready`

## Why this materially reduces the Golden gap

The first genuine story can now move from captured source bytes to the six evidence files without trusting a stale binding receipt. The exact bytes that were originally hashed must still exist unchanged at evidence-compilation time.

The next safe non-GPU step is an atomic source-to-production-receipts runner that chains this replayed evidence pack into Change Set 252 while preserving all authority boundaries.