# Phase 18 Implementation Log — CS461

## Scope

Branch-only change on `phase18/story-intelligence`. `main` was not modified.

## Goal

Close the remaining post-generation evidence gap in the freshness-bound First Genuine Golden v6 workflow by producing one fail-closed, content-addressed manifest that binds:

- the freshness-bound canonical wrapper result,
- freshness verification,
- source-bound artifact replay,
- the final resource-lock receipt,
- the exact PNG bytes,
- the immutable source commit SHA,
- GitHub workflow run identity when available.

This change does not generate pixels and does not weaken factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality/Human Review gates.

## Added

### `tools/phase18_verify_first_genuine_golden_v6_fresh_source_bound.py`

CPU-safe verifier that rejects the attempt unless all of the following agree:

- branch is exactly `phase18/story-intelligence`;
- cost mode is exactly `$0-local`;
- fresh wrapper reports `ready=true`, `fresh_attempt_evidence=true`, and actual Candidate 1 generation start;
- freshness verification has no blockers and proves all four mutable artifacts changed in the current attempt;
- source-bound replay is tied to the exact expected 40-character commit SHA;
- source replay proves local-only model receipts and semantic evidence;
- resource-lock schema/status/branch/candidate/cost identity match;
- PNG exists inside the repository, has a valid PNG signature, and its SHA-256 matches freshness, source replay, and resource-lock evidence;
- source replay's recorded resource-lock SHA-256 matches the actual resource-lock bytes;
- Human Review, Golden approval, publication, network-download, and Seeds 2–4 authorities remain closed.

On success the verifier emits `pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v1`, including SHA-256 digests for all bound evidence and the PNG.

### `tests/test_phase18_first_golden_fresh_source_bound_manifest.py`

Regression coverage for:

- valid content-addressed manifest construction;
- fail-closed stale mutable evidence;
- fail-closed PNG byte drift;
- workflow ordering proving the new verifier runs before evidence upload.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

Added the new verifier to the immutable source checkout requirements and added a post-source-binding step that creates:

- `output/phase18_gpu_smoke/first-genuine-golden-v6-fresh-source-bound-manifest.json`
- `output/phase18_gpu_smoke/first-genuine-golden-v6-fresh-source-bound-replay.json`

The step runs after freshness replay and source-bound artifact replay, and before `actions/upload-artifact`.

## Deleted

None.

## Gate preservation

Unchanged:

- factual and entity/identity verification;
- neutral/respectful sentiment rules;
- `$0-local` execution requirement;
- offline-only model resolution;
- native CUDA/BF16 requirement with no FP16/FP32 substitution;
- semantic preflight and SemanticPublicationGate semantics;
- Qwen2.5-VL and FLUX.2 pinned identities/revisions;
- Candidate 1 prompt/seed/dimensions/steps/guidance;
- Human Visual Review requirement;
- Golden quality approval remains false before Human Review;
- publication remains false;
- Seeds 2–4 remain unauthorized.

## Execution status

No Genuine Golden PNG was fabricated or claimed by this change. Actual Candidate 1 generation remains dependent on an available compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/cache headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under offline-only `$0-local` execution.
