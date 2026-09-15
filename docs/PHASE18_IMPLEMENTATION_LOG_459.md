# PUL7SAR Phase 18 — Implementation Log CS459

## Scope

Branch: `phase18/story-intelligence` only.

This change set advances the first genuine Golden Visual path by binding the CS458 stale-artifact freshness guard around the existing canonical attested launcher without weakening any factual, identity, sentiment, zero-cost, semantic-publication, visual-quality, BF16, local-cache, human-review, publication, or Seeds 2–4 gate.

## Prior state reviewed

- CS458 HEAD: `ece5271e6d58bee4e6dd673ead60dc228ca85bd1`.
- Retrieved GitHub Actions runs for that exact SHA were completed successfully.
- CS458 provided an independent CPU-safe `capture()` / `verify()` freshness guard, but the authoritative canonical launcher did not yet have a wrapper that automatically captured a baseline before the attempt and replayed freshness after it.

## Added

### `tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py`

Adds a fail-closed wrapper around the existing canonical attested launcher.

Execution order:

1. Validate that all output/evidence paths are distinct and remain inside the repository.
2. Capture the CS458 mutable-artifact freshness baseline.
3. Persist the baseline before invoking the canonical attempt.
4. Run the existing canonical attested/content-bound/output-replayed launcher unchanged.
5. Replay freshness against the pre-attempt baseline.
6. Persist freshness verification evidence.
7. Report `ready=true` only when both the existing canonical result is ready and `fresh_attempt_evidence=true` with no authority drift.

The wrapper never promotes authority. The returned top-level state explicitly keeps:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

The wrapper preserves the canonical PNG path/SHA only as evidence when the underlying canonical launcher supplies them; it does not create or fabricate a PNG itself.

### `tests/test_phase18_first_golden_canonical_fresh_wrapper.py`

Regression coverage for:

- baseline persistence occurring before canonical execution;
- freshness replay occurring after canonical execution;
- stale evidence rejecting an otherwise ready canonical result;
- canonical failure remaining fail-closed even when freshness succeeds;
- authority drift never being promoted by the wrapper;
- output-path collision failing before capture or canonical generation.

### `docs/PHASE18_IMPLEMENTATION_LOG_459.md`

This implementation log.

## Modified

None.

## Deleted

None.

## Preserved gates

No changes were made to:

- factual verification / fact locks;
- real-person or entity identity verification;
- sentiment / loser-respect policy;
- `$0-local` policy;
- offline-only / no-network-download policy;
- SemanticPublicationGate;
- visual-quality / Human Review authority;
- Candidate 1 prompt, seed, dimensions, steps, or guidance;
- approved Qwen2.5-VL or FLUX.2 model identities/revisions;
- CUDA / native-BF16 requirements;
- precision-substitution rejection;
- publication authority;
- Seeds 2–4 authority.

## Testing status

The new unit tests were committed to the branch and are intended to run under the repository's existing Phase 18 CPU verification/discovery workflow. No compatible CUDA/GPU execution was available in this automation runtime, so no genuine Golden PNG was claimed or fabricated.

## Remaining gap

The new freshness-bound wrapper materially closes the stale-evidence gap at the orchestration boundary, but the existing canonical GitHub GPU workflow still needs to be switched to invoke this wrapper (or equivalent in-launcher integration) before CS459 can be considered the authoritative workflow path.

After that wiring is terminal-green, the remaining execution blocker is still a compatible self-hosted NVIDIA host satisfying all of the existing requirements simultaneously: real CUDA execution, native BF16, approved GPU/compute capability, sufficient VRAM/RAM/cache/filesystem headroom, compatible runtimes, exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally, `$0-local`, offline-only, no model download, and no FP16/FP32 quality substitution.
