# Phase 18 Change Set 256 — Atomic Source-to-Production Receipts

## Purpose

Change Set 256 removes the remaining manual execution gap between Change Set 255
retrieved-source byte replay and Change Set 252 production-gate receipt execution.
It does not generate pixels and it does not grant fresh-story, generation, Golden,
human-review, or publication authority.

## Added

- `engine/intelligence/qwen_image_source_to_production_receipts.py`
  - replays Change Set 254 source bindings through the Change Set 255 bridge;
  - compiles the byte-bound Change Set 253 six-evidence pack;
  - immediately executes the six canonical Change Set 252 production verifiers;
  - writes one production receipt per canonical gate in canonical order;
  - byte-binds the binding receipt, bound manifest, evidence-pack receipt, and each
    production gate receipt in a run receipt;
  - stages every output privately and publishes the final output directory only after
    all six verifiers pass;
  - removes staging output on failure.
- `tests/test_phase18_qwen_image_source_to_production_receipts.py`
  - verifies complete publication on success;
  - verifies no final or staging artifact survives a gate failure;
  - rejects pre-existing output targets;
  - rejects production receipt gate-order drift;
  - verifies all downstream authority remains false.
- `tools/phase18_run_source_to_production_receipts.py`
  - CPU-only CLI with an explicit caller-supplied UTC evaluation timestamp.

## Authority boundary

A successful Change Set 256 run means only that current captured source bytes survived
binding replay, the six same-story evidence files were compiled, and all six production
verifiers returned passing production receipts.

It explicitly does **not** mean that Change Set 237 freshness admission or Change Set 238
independent semantic replay occurred. The run receipt therefore keeps these and all
later authorities false:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `controlled_trial_preflight_valid`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Atomic publication rule

The requested final output path must not already exist. Work occurs under a private
sibling staging directory. Only after source replay, evidence compilation, six production
verifier executions, receipt serialization, byte binding, and run-receipt construction
all succeed is the staging directory renamed into the requested final output path.
Any exception removes the staging directory.

This is filesystem publication atomicity for the receipt run; it is not a claim of a
transaction across external source retrieval, GitHub, or future GPU execution.

## Remaining path to first genuine Golden PNG

1. Run Change Set 256 on one genuinely retrieved, source-backed current story.
2. Submit its six production receipts to Change Set 237 freshness admission.
3. Run Change Set 238 independent semantic replay and require the semantic-detail hashes
   to match the production verifier outputs.
4. Obtain explicit generation authorization only after all controlled-trial/runtime gates
   independently pass.
5. Execute Qwen-Image-2512 only on a compatible `$0-local` CUDA host.
6. Continue through Semantic/Layer QA, byte-bound Visual Critic, human review, Golden
   threshold, exact brand/typography, and `SemanticPublicationGate`.

No genuine Golden PNG is claimed by this change set.
