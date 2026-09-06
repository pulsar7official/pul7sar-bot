# Phase 18 Implementation Log 231

## Change Set

**231 — Qwen Image 2512 Runtime Qualification Candidate**

## Baseline review

- Phase 18 baseline head before this change set: `b7c1054daf385eb63445622b8bdbd6c42f7d354d`.
- Observed `main` baseline during initial review: `2a6dee5bb64895a1658be84d7ce018cd71a08dff`.
- No merge, rebase, force-update, or write to `main` was performed.
- `main.py` was not modified.
- Change Set 230 baseline CI was confirmed successful before implementation:
  - Phase 18 Story Intelligence Verification PR Run `33153410560 / 3672`: success.
  - Companion workflows observed on the same `b7c1054d...` head also completed successfully.

## Gap found during review

Change Set 230 validates each locked runtime-envelope probe and its engineering PNG independently. Before a later runtime-qualification decision, the evidence also needs a cross-probe coherence boundary. Without it, individually valid observations could theoretically be stitched from different GPU/software environments and still look like one complete envelope.

Change Set 231 prevents that ambiguity and also locks the derived summary so a rehashed candidate cannot claim a larger measured envelope than the locked probes actually covered.

## Added files

### `engine/intelligence/qwen_image_runtime_qualification_candidate.py`

Creation commit: `a81ba510bdb78bf5b4817f1a607d9a77c39eecee`.

Adds a CPU-only, fail-closed normalization contract that:

- replays a Change Set 230 execution receipt;
- requires the full locked 512/768/1024 envelope to be completed successfully;
- requires coherent GPU/runtime identity across all three probes;
- rejects mixed GPU name, total VRAM, Torch, CUDA, Diffusers, pipeline, dtype, offload, or BF16 evidence;
- derives conservative measured resource summaries;
- produces a SHA-bound qualification candidate;
- leaves every production, Golden, semantic, and publication authority false.

Hardening commit: `f85d056e778837182db7e5d9e63c40436edb9618`.

Replay was tightened so a candidate cannot be made stronger merely by editing its summary and recomputing the digest. The verifier now requires:

- the locked maximum probe extent to remain exactly 1024×1024 / 8 steps;
- the summary field set to be exact;
- maximum CUDA allocated memory not to exceed maximum CUDA reserved memory;
- summarized free VRAM not to exceed the coherent runtime's total VRAM;
- total VRAM itself to be positive.

### `tests/test_phase18_qwen_image_runtime_qualification_candidate.py`

Creation commit: `c0bc1f07dbe1d2a6bf8f5463e196a27361becdfe`.

Adds canonical `unittest` regression coverage for:

- a complete same-runtime envelope becoming a non-authoritative candidate;
- mixed GPU-name rejection even after the source execution receipt is rehashed;
- mixed CUDA-version rejection;
- mixed total-VRAM rejection;
- stopped/incomplete envelope rejection;
- authority forgery rejection even after candidate digest recomputation;
- candidate digest tamper detection.

### `tests/test_phase18_qwen_image_runtime_qualification_candidate_replay.py`

Creation commit: `bca5026181cd0f246c801529a85f272c794b7aab`.

Adds focused replay-hardening regressions proving that rehashing does not permit:

- claiming a 2048-pixel measured extent when the locked envelope ends at 1024;
- reporting maximum CUDA allocation above maximum CUDA reservation;
- reporting free VRAM above the coherent runtime's total VRAM.

### `tools/phase18_build_qwen_runtime_qualification_candidate.py`

Creation commit: `d32c2560538a1030c973699b029496485bcb7aae`.

Adds a CPU-only CLI that reads an on-disk Change Set 230 execution receipt, SHA-binds the receipt file, replays referenced engineering PNGs through the qualification builder, and writes a normalized candidate receipt.

It does not load a model, invoke CUDA, mutate the generation queue, or grant canonical/Golden/publication authority.

### `docs/PHASE18_CHANGESET_231_QWEN_RUNTIME_QUALIFICATION_CANDIDATE.md`

Creation commit: `29e4c6af506e3ce5d02c8e68f01303e955ee4e2a`.

Documents purpose, evidence semantics, same-runtime requirement, preserved gates, and the remaining CUDA blocker.

### `docs/PHASE18_IMPLEMENTATION_LOG_231.md`

Initial creation commit: `bc77959a029a06f526b1acd6e25edb58eb879c09`.

This update records subsequent replay hardening and its regression coverage.

## Modified files

- `engine/intelligence/qwen_image_runtime_qualification_candidate.py` — hardened in `f85d056e778837182db7e5d9e63c40436edb9618`.
- `docs/PHASE18_IMPLEMENTATION_LOG_231.md` — updated to record all Change Set 231 implementation and hardening work.

No existing canonical-generation or semantic-publication runtime file was modified.

## Deleted files

None.

## Test scope

All new tests are CPU-only. They exercise evidence validation, cross-probe coherence, digest replay, summary consistency, and authority boundaries without pretending that a compatible NVIDIA host was used.

No real Qwen inference result, runtime floor, Golden PNG, or visual score is asserted by these tests.

## Gate preservation

No factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gate was weakened.

The candidate hard-codes the following as false:

- `runtime_floor_proven = false`
- `local_runtime_qualified = false`
- `canonical_generation_authorized = false`
- `canonical_pixels_reusable = false`
- `queue_mutated = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`

Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local`, pinned-model provenance, Semantic/Layer Ownership, generated-text/branding/exact-fact/entity-mark/exact-sport-geometry restrictions, byte-bound Visual Critic, Human Review, Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand Integrity, Typography Integrity, and SemanticPublicationGate remain downstream and fail-closed.

## Genuine Golden Visual status

No accepted genuine Golden Visual PNG was generated in Change Set 231. No GPU result, runtime floor, or visual score was fabricated.

## Remaining blocker

The currently accessible execution environment does not expose a compatible self-hosted NVIDIA CUDA host with the exact pinned Qwen Image 2512 snapshot and proven native BF16, sufficient live VRAM/system RAM, compatible Diffusers/QwenImagePipeline runtime, sequential CPU offload, and `$0-local` execution.

The next real hardware step remains execution of the locked Change Set 230 envelope. If and only if all probes succeed on one coherent runtime environment, Change Set 231 can normalize that real evidence for a later explicit local-runtime qualification decision.

## Final CI state

Pending GitHub Actions on the final Change Set 231 head. Do not treat Change Set 231 as CI-green until the final Phase 18 Story Intelligence Verification completes successfully.
