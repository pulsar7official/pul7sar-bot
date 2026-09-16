# Phase 18 Implementation Log — CS456

## Scope

Advance `phase18/story-intelligence` toward the first genuine Golden Visual PNG without modifying `main` and without weakening factual, identity, sentiment, zero-cost, semantic-publication, native-BF16, visual-quality, or human-review gates.

## Starting state

- Starting branch HEAD: `0bdb9a169ff552bd289b66f6c000944e0e5a19e8` (CS455).
- CS455 central verification and CPU diagnostics were confirmed successful before this change set.
- CS455 created a content-bound first-Golden GPU attempt contract containing SHA-256 bindings for the GPU handoff, canonical workflow, and canonical launcher.
- Remaining gap: the canonical launcher did not yet consume/replay those bindings immediately before invoking the resource-locked Candidate 1 entry point.

## Changes

### Modified

`tools/phase18_run_first_genuine_golden_v6_canonical_attested.py`

- Advanced canonical launch schema to `pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v3`.
- Added first-Golden GPU attempt-contract construction from the exact handoff created by the same canonical run.
- Added `--attempt-contract` CLI path with a repository-contained fail-closed default.
- Added attempt-contract path to output collision protection.
- Added SHA-256 replay immediately before the generation subprocess for:
  - exact GPU handoff bytes;
  - `.github/workflows/phase18-first-genuine-golden-v6.yml`;
  - `tools/phase18_run_first_genuine_golden_v6_canonical_attested.py`.
- Added fail-closed blockers for schema, commit, branch, `$0-local`, offline-only, readiness, pre-execution state, authority, and content drift.
- Candidate 1 generation is not invoked if any attempt-contract replay blocker is present.
- All closed authorities remain explicitly false in every return path.

### Added

`tests/test_phase18_first_golden_gpu_attempt_replay_gate.py`

Regression coverage verifies that:

- exact current handoff/workflow/launcher bytes satisfy the replay gate;
- handoff byte drift is detected by SHA-256 replay;
- a drifted attempt contract blocks the generation subprocess;
- the attempt-contract output participates in path-collision protection;
- factual/publication authority remains closed when the new gate blocks execution.

### Deleted

None.

## Gates deliberately unchanged

No changes were made to:

- factual verification/fact locks;
- real-person/entity identity verification;
- sentiment and loser-respect policy;
- `SemanticPublicationGate`;
- visual-quality or Human Review authority;
- Candidate 1 prompt, seed, dimensions, steps, guidance, or composition policy;
- Qwen2.5-VL or FLUX.2 approved model identities/revisions;
- native BF16 requirement;
- CUDA requirement;
- `$0-local` requirement;
- `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` policy;
- network-download prohibition;
- publication authority;
- Seeds 2–4 authority.

## Why this materially reduces the remaining gap

CS455 made a GPU attempt contract content-addressed, but a recorded digest has value only if the execution path replays it before generation. CS456 moves that protection into the canonical launcher itself. The exact handoff/workflow/launcher bytes are now rebound and rechecked in-process immediately before the resource-locked generation subprocess. This closes the remaining content-binding TOCTOU gap without consuming GPU time or granting generation/publication authority early.

## Testing state

The new commits intentionally rely on the repository's existing Phase 18 central verification and CPU diagnostic workflows for authoritative CI status. Do not describe CS456 as terminal-green until those workflows complete successfully on the final CS456 HEAD.

## Remaining blocker to a genuine PNG

A genuine PNG still requires an available compatible self-hosted NVIDIA execution host satisfying all existing fail-closed preconditions at once, including CUDA-enabled PyTorch, a real CUDA device, native BF16, approved GPU/compute capability, sufficient live-free VRAM/RAM/cache/filesystem headroom, coherent Qwen2.5-VL semantic runtime, compatible FLUX runtime, and the exact approved local model snapshots. Network model download and FP16/FP32 quality substitution remain prohibited.

No PNG is claimed by this change set.
