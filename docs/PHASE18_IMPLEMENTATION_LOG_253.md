# Phase 18 Implementation Log 253

## Scope

Change Set 253 advances `phase18/story-intelligence` from six production verifier readiness/receipt execution toward one genuine fresh-story semantic replay by adding a canonical source-backed story evidence-pack compiler.

No change targets `main`.

## Baseline reviewed before writing

- `phase18/story-intelligence`: `5054e5265f66fc4f5c30effa97b7147879cff5c0`
- `main`: `2f446f0bbe252b3914ed127e4c8267836036b1d5`
- Change Set 252 production receipt executor is present and CI-green.
- Canonical production registry is 6/6.
- Genuine source-backed six-gate story evidence has not yet been produced.
- No compatible zero-cost CUDA runtime is available in this execution path.

## Added

### `engine/intelligence/qwen_image_source_backed_story_evidence_pack.py`

Commit: `f4cb68774629f0b1404b7544d8f2227c45beee61`

Adds a CPU-only compiler whose exact input manifest bytes become the story snapshot. The compiler:

- SHA-256 binds the manifest bytes once;
- requires structured source-document provenance;
- requires HTTPS source URLs, publisher, publication/retrieval UTC times and source-content SHA-256;
- requires every fact source, canonical identity source and source-backed emotional attribution to resolve to a declared source document;
- emits exactly six evidence files in `REQUIRED_FRESH_GATE_EVIDENCE` order;
- injects one common story snapshot SHA-256 into all six evidence files;
- records SHA-256 and byte size for every emitted evidence file;
- refuses non-empty output directories;
- emits an evidence-pack receipt with all downstream authority fields false.

It does not independently prove source truth, execute semantic replay, authorize generation, load weights, generate pixels, approve Golden quality or publish.

### `tests/test_phase18_qwen_image_source_backed_story_evidence_pack.py`

Commit: `426cdc8fe7e5fd62c4148a7a879f3d2d8d76d17d`

Regression coverage includes:

- one story snapshot SHA shared by all six evidence files;
- pack receipt remains fail-closed;
- compiled synthetic fixture feeds all six real production verifiers through Change Set 252;
- unknown fact source rejection;
- unknown identity source rejection;
- non-HTTPS source URL rejection;
- invalid source-content SHA rejection;
- unknown emotional-attribution source rejection;
- non-empty output directory rejection.

The `example.org` story is a test fixture only and must never be treated as genuine story evidence.

### `tools/phase18_compile_source_backed_story_evidence_pack.py`

Commit: `9c14ed72aee72a9a6179057a13f61b3a76d42185`

Adds a CPU-only command-line entry point for compiling one source-backed story manifest into the six canonical evidence files. Its printed summary repeats the fail-closed authority state and does not execute semantic replay or CUDA inference.

### Documentation

- `docs/PHASE18_CHANGESET_253_SOURCE_BACKED_STORY_EVIDENCE_PACK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_253.md`

## Modified

No pre-existing production, generation, publication, semantic gate, visual-quality or registry implementation was modified in Change Set 253. This implementation log was updated to record the CLI addition.

## Deleted

Nothing.

## Test / CI state

Phase 18 Story Intelligence Verification run `33234819162 / 3932` was started for test commit `426cdc8fe7e5fd62c4148a7a879f3d2d8d76d17d`. At the time this log was updated it was still `in_progress`; no CI-green claim is made until GitHub reports completion/success.

## Authority state

Change Set 253 intentionally leaves all downstream authority false:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Remaining non-GPU gap

A genuine public/source-backed story manifest must be assembled from retrieved source content rather than fixtures. Change Set 253 can then compile the exact same-story six-evidence set; Change Set 252 can create real production gate receipts; Change Set 237 must admit them within freshness; Change Set 238 must independently replay semantic details before `fresh_story_gates_passed` can become true.

## GPU blocker

A genuine Golden PNG remains blocked until one `$0-local` runtime proves, in one compatible execution environment, NVIDIA CUDA, native BF16, sufficient live VRAM and system RAM, the exact pinned `Qwen/Qwen-Image-2512` revision, compatible `Diffusers/QwenImagePipeline`, successful sequential CPU offload and canonical local-only zero-cost execution.

No inference result or PNG is fabricated.
