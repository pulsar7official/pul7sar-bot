# Phase 18 Implementation Log 436 — First-Golden Source Identity Probe

## Scope

CS436 advances the first genuine Golden Visual v6 execution path without generating or fabricating a PNG. The change adds a fail-closed, non-authoritative source-identity probe that can be executed before GPU work to prove that execution is rooted in the dedicated Phase 18 branch and immutable source state.

## Reviewed starting state

- Starting branch: `phase18/story-intelligence`
- Starting HEAD: `db5714a0fb397b3ab59beec2c5377d1a7bb97c18`
- CS435 Story Intelligence Verification: terminal green.
- `main` was not modified.
- Existing authoritative resource lock already rejects a non-Phase-18 branch later in the heavy execution chain.
- The shared environmental blocker probe reports `branch_required` but does not independently persist an early source-identity receipt.

## Added

### `tools/phase18_probe_first_golden_source_identity.py`

A zero-cost, non-generating, fail-closed source probe that verifies:

1. Current branch is exactly `phase18/story-intelligence`.
2. Current `HEAD` resolves to a 40-character immutable commit SHA.
3. An optional dispatch/expected SHA exactly matches `HEAD`.
4. Tracked source state is clean before GPU execution; untracked output artifacts do not invalidate the source proof.
5. `origin/main` has a provable merge-base with the execution commit.
6. `main.py` is not part of the Phase 18 diff from that merge-base.

The receipt cannot authorize downloads, generation, publication, human Golden acceptance, or Seeds 2–4.

### `tests/test_phase18_first_golden_source_identity_probe.py`

Regression coverage proves fail-closed behavior for:

- execution on `main` or another branch;
- expected/dispatch SHA mismatch;
- dirty tracked source;
- `main.py` modification in the Phase 18 diff;
- invalid expected commit values;
- authority fields remaining closed in the valid case.

## Modified

None.

## Deleted

None.

## Gate preservation

No factual, entity/identity, sentiment-neutrality, zero-cost, semantic-publication, or visual-quality gate was weakened. No model ID, immutable revision, prompt, seed, generation parameter, dependency, CUDA policy, BF16 requirement, or publication authority was changed.

## Testing

The new tests are standard-library `unittest` tests and are discoverable by the existing Phase 18 Story Intelligence Verification suite. Full CI is required on the exact CS436 HEAD before this checkpoint can be called terminal-green.

## Remaining blocker to first genuine Golden PNG

No genuine Golden PNG is claimed by this checkpoint. Actual Candidate 1 execution still requires a compatible self-hosted NVIDIA execution host with CUDA-enabled PyTorch, at least one real CUDA device, native BF16, sufficient live VRAM/RAM/filesystem headroom, the approved generation and semantic runtimes, and exact immutable Qwen2.5-VL and FLUX.2 snapshots resolvable locally under `$0-local` and offline-only policy.

## Next safe integration step

Bind this source-identity receipt into the canonical/JIT/offload first-Golden workflows before the shared environmental blocker probe, passing the immutable dispatch SHA where available. That makes source identity evidence persistent before any GPU-heavy work while preserving the existing branch-isolation checks as defense in depth.
