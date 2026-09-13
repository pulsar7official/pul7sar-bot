# Phase 18 Implementation Log 401

## Scope
CS401 — add a fail-closed artifact-readiness manifest that can exist only after the complete First Genuine Golden v6 source-bound replay succeeds.

## Branch isolation
- Target branch: `phase18/story-intelligence` only.
- Starting branch HEAD: `7537df0b5b543ef3343b8d030aa7a3aded527af3`.
- `main` was read only; observed at `b40f5446fa8ce71accb53f46f364aedeba5c8d35` during this change set.
- No merge, rebase, reset, force update, or write to `main` was performed.

## Prior state verified
CS400 is terminal-green: Phase 18 Story Intelligence Verification run `34567609496` completed successfully on starting HEAD `7537df0b5b543ef3343b8d030aa7a3aded527af3`.

## Problem closed
The Golden v6 workflow intentionally uploads evidence with `if: always()` so failed GPU runs still preserve diagnostic evidence. That is useful for debugging, but it means the mere existence of an uploaded artifact cannot prove Candidate 1 reached the complete source-bound replay gate.

CS401 adds a distinct success marker that is written only after the composite byte/semantic/source-commit replay returns a fully verified result. Before CLI verification begins, any stale marker at the expected path is removed. Therefore a failed or partial run can still upload diagnostics, but cannot legitimately carry a fresh readiness manifest from the current replay attempt.

This readiness state means only `eligible_for_human_visual_review=true`; it does not approve Human Review, Golden Quality, publication, or Seeds 2–4.

## Changes
### Modified
`tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py`

- Adds `ARTIFACT_READY_FILENAME = first-genuine-golden-v6-artifact-ready.json`.
- Adds `build_artifact_ready_manifest(...)` with strict validation of:
  - source-bound replay verified status;
  - exact source-commit verification;
  - `$0-local` cost mode;
  - all 9 evidence files verified;
  - evidence semantics verified;
  - source SHA, resource-lock SHA-256, PNG SHA-256, and positive PNG byte count;
  - Human Review, Golden Quality, publication, and Seeds 2–4 authority all still false.
- Adds `write_artifact_ready_manifest(...)` using same-directory temporary-file replacement for atomic publication of the success marker.
- CLI execution removes any stale readiness marker before replay begins and writes a new one only after successful verification.
- The resulting manifest binds source commit, resource lock, and PNG identity while exposing only `eligible_for_human_visual_review=true`.

Code commit: `e5f11b0455c2a8e67f9ac89c98412d2da6dd8545`.

### Added
`tests/test_phase18_first_genuine_golden_v6_artifact_ready_manifest.py`

Regression coverage protects:
- review eligibility without downstream approval;
- source/resource-lock/PNG provenance binding;
- rejection of incomplete or semantically unverified evidence;
- rejection of any downstream authority drift;
- atomic valid-JSON manifest writing without leaving a temporary file.

Test commit: `61df1744f34943d4f0ad67fad4429e1bab523bd1`.

### Deleted
None.

### Dependencies
None changed.

### Workflow impact
No workflow YAML change was required. CS400 already invokes the source-bound verifier CLI before upload. The CLI now writes the readiness manifest next to the resource-lock receipt under `output/phase18_gpu_smoke/`, which is already included in the existing artifact upload glob.

The workflow still uses `if: always()` for evidence upload, preserving failed-run diagnostics. The new readiness manifest is what distinguishes a completely replay-verified Candidate 1 package from a partial diagnostic artifact.

### Generation/model/prompt behavior
No generation model, prompt, factual, identity, sentiment/loser-respect, zero-cost, semantic-publication, layer-ownership, or visual-quality gate was weakened or bypassed.

## Testing
Repository CI is triggered by the branch commits. CS401 must not be called terminal-green until Phase 18 Story Intelligence Verification completes successfully on the exact code-and-test-bearing SHA/current documented HEAD.

No genuine PNG is fabricated by these CPU-safe changes.

## Remaining blocker to the first genuine Golden PNG
A real execution still requires the First Genuine Golden v6 workflow to run on a compatible self-hosted NVIDIA host with:
- CUDA-enabled PyTorch;
- native BF16 support;
- sufficient VRAM/RAM/storage;
- exact approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally;
- `$0-local` / offline model resolution intact.

Until such an execution succeeds, Candidate 1 has no genuine Golden PNG and Human Review, Golden Quality, publication, and Seeds 2–4 remain fail-closed.
