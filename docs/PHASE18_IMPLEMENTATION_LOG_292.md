# Phase 18 Implementation Log — Change Set 292

## Scope and baseline

Branch: `phase18/story-intelligence` only. `main` was read-only and was not modified.

Baseline reviewed before implementation: `ffd4a1b6a67b9278eaaf8ef3a0e341e0e1b4cefe` (CS291).

Before CS292 work began, the CS291 `Phase 18 Story Intelligence Verification` push workflow was confirmed `completed / success` on run `33389115034` (run number `4374`). A PR-triggered Story Intelligence verification on the same SHA also completed successfully.

During the initial state review, CS291's launch manifest was found to be complete as a standalone preflight artifact, but the genuine production inference CLI did not require that artifact. The CLI could therefore be called directly and reach its own local-runtime checks without first replaying the CS291 pre-launch attestation. CS292 closes that execution-edge bypass rather than adding another downstream approval gate.

## Added

- `docs/PHASE18_CHANGESET_292_LAUNCH_MANIFEST_EXECUTION_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_292.md`

## Modified

- `engine/intelligence/qwen_image_gpu_host_launch_manifest.py`
  - added `verify_gpu_host_launch_manifest_for_execution(...)`;
  - expanded execution-contract source byte bindings from six files to nine;
  - added the launch-manifest verifier itself, the story-bound prompt contract implementation, and the generation-authorization implementation to the byte-bound source set;
  - added exact execution-time equality checks for authorization path, CS257 evidence directory, local snapshot path/revision, dimensions, seed, steps, and guidance scale;
  - preserved the existing `$0-local`, no-network, local-files-only, BF16, sequential-CPU-offload and downstream-authority constraints.

- `tools/phase18_run_one_shot_canonical_inference.py`
  - added mandatory `--launch-manifest` argument;
  - replays the full launch manifest before prompt extraction, model import/load, authorization consumption, or inference;
  - requires the actual invocation to match the attested authorization, evidence directory, snapshot and inference settings exactly;
  - includes the verified launch-manifest digest in successful command output;
  - retains no free-form prompt, no retry loop, no network fallback, and no Golden/publication authority.

- `tests/test_phase18_qwen_image_gpu_host_launch_manifest.py`
  - updated the fixture for the expanded nine-source execution contract;
  - added exact execution-binding success regression;
  - added seed/settings drift rejection regression;
  - added authorization-path drift rejection regression;
  - retained CS291 cross-story, measured-envelope, CS257 byte-drift and manifest-tamper regressions.

## Deleted

None.

## Code commits in this change set

- `e4f9dbe17dcfad583e7fcce5af976dedcc018c33` — bind the launch manifest to the execution edge and expand source byte bindings.
- `f58e0d2add120cc929408c25426538286a91cd37` — require `--launch-manifest` in the genuine inference CLI and replay it before model operations.
- `dfcf53e9759cc286607cacf0b08d8c1940be90e7` — add execution-binding regressions and update the CS291 fixture.
- `080a635c6907fa895a9834ff0dee5f9a485e32b5` — document the CS292 contract.

## Security / correctness effect

CS292 changes the launch manifest from an optional preflight artifact into a mandatory prerequisite of the production inference CLI.

An operator can no longer change the seed, dimensions, inference steps, guidance scale, authorization file, CS257 evidence directory, or local model snapshot after manifest creation and still use the standard genuine inference entry point. The mismatch is rejected before model load.

The manifest also now invalidates itself when any of the code governing launch verification, story-bound prompt reconstruction, generation authorization, GPU readiness, local model loading, one-shot inference, local provenance, or the production CLI changes.

## Preserved gates

No Fact Lock, entity/identity verification, sentiment neutrality, loser-respect, zero-cost policy, semantic-publication gate, visual-quality gate, Human Review, Exact Brand Integrity, Typography Integrity, Genuine Golden materialization, or publication-readiness policy was weakened or bypassed.

A verified CS292 launch still grants no semantic, human-review, Golden-quality, Genuine-Golden, or publication authority. Those remain downstream and fail-closed.

## Tests

New/updated CPU regressions cover:

- exact attested invocation accepted;
- seed/settings drift rejected before model load;
- authorization-path drift rejected;
- expanded nine-file execution-contract byte binding;
- cross-story prompt rejection;
- inference settings outside the measured envelope rejected;
- CS257 evidence byte drift detected;
- launch-manifest tampering detected.

These tests are synthetic/control-plane tests only. They are not evidence of a successful Qwen model load or CUDA inference and do not create or claim a Golden PNG.

The final branch HEAD must be validated by GitHub Actions after this log commit; CI status is reported externally from the repository state and is not pre-declared as successful here.

## Exact remaining blocker

The available execution runtime for this work does not provide the compatible NVIDIA CUDA/BF16 environment required for genuine Qwen-Image execution. No model load, genuine inference, production canonical PNG, production composed PNG, or Genuine Golden PNG is fabricated by CS292.

The required zero-cost host must provide:

- an NVIDIA CUDA device and CUDA-enabled PyTorch;
- native BF16 support;
- a compatible `QwenImagePipeline`;
- sequential CPU offload support;
- the exact already-local `Qwen/Qwen-Image-2512` snapshot at revision `2ce1c28560fbc62c9f5531e076b237d3575330a9`;
- sufficient real VRAM and system RAM, demonstrated by actual load/inference rather than a guessed threshold.

## Remaining path

CS292 execution-bound launch manifest -> compatible zero-cost CUDA host -> static GPU preflight -> real local model load -> one-shot story-bound inference -> local execution provenance -> existing factual/identity/sentiment/semantic/composition/visual-quality/human/brand/typography gates -> real `SemanticPublicationGate` -> CS285 exact-byte Genuine Golden materialization -> CS286 publication readiness.
