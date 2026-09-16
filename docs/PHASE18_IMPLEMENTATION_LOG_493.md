# Phase 18 Implementation Log — CS493

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

Baseline reviewed before changes: CS492 at `86047a7c49e1a9cdd2f3dc626dc5aefcde982731`.

## Why this change

The first genuine Golden workflow already records a fail-closed execution-blocker probe before the explicit CUDA/native-BF16 preflight and before Candidate 1 generation. On failure it uploads only `output/phase18_gpu_smoke/**` as short-lived diagnostics, while the success path uploads only the exact Human Review bundle. This is important operational evidence: when a compatible GPU/runtime/cache prerequisite is missing, the run must preserve the exact blocker without allowing failed-attempt diagnostics to masquerade as a Golden review artifact.

CS492 locked the PNG semantic critical path but did not independently regression-lock this blocker-observability and success/failure artifact separation contract.

## Added

- `tests/test_phase18_first_golden_blocker_diagnostics_workflow.py`
  - Requires the execution-blocker probe command and its JSON output path.
  - Requires the blocker probe to precede CUDA/native-BF16 preflight and Candidate 1 generation.
  - Requires the failed-attempt diagnostic upload to remain after generation in workflow order and guarded by `if: failure()`.
  - Requires failed diagnostics to upload only `output/phase18_gpu_smoke/**`.
  - Requires successful runs to upload only the exact `output/phase18_golden_review/${{ github.run_id }}-${{ github.run_attempt }}/**` bundle.
  - Rejects accidental inclusion of GPU-smoke diagnostics in the success artifact and accidental inclusion of the Human Review bundle in the failure artifact.

## Modified

None in production code or workflow behavior. The new test was aligned in a follow-up commit to assert the actual blocker-probe command rather than an immutable-source presence assertion that the workflow does not currently make.

## Deleted

None.

## Gates preserved

No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/offline-only, semantic-publication, exact model/runtime provenance, CUDA/native-BF16, PNG structural/chunk-semantic/canonical, Human Visual Review, Golden-quality, publication, or Seeds 2–4 authority was weakened or opened.

No paid API, model download, CPU generation fallback, FP16 fallback, FP32 fallback, or publication bypass was introduced.

## Testing / validation

CS492 was reviewed first and its GitHub Actions runs were observed completed successfully before this change. CS493 adds a static workflow regression test; repository CI on the exact CS493 head remains authoritative for terminal-green status.

## Remaining gap

No genuine Golden PNG is claimed by this change. The material execution blocker remains availability of a self-hosted NVIDIA runner satisfying the existing workflow labels and runtime contract: CUDA-enabled PyTorch, a real CUDA device, native BF16 support, sufficient GPU/host/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only constraints.

Once such a host executes the workflow, the blocker probe is now regression-locked to remain observable on failure without contaminating the success Human Review artifact path.
