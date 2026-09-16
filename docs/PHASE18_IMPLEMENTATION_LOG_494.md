# Phase 18 Implementation Log — CS494

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

Baseline reviewed before changes: CS493 at `20ccb75ae5800b754b4f2d4a5b3cfc4881ca16ca`. Its GitHub check suite exposed 12 Phase 18 checks; the returned completed checks, including `verify-story-intelligence`, were successful.

## Why this change materially reduces the remaining gap

The authoritative first-Golden workflow already records a detailed execution-blocker probe, but that probe lives inside the full generation job. A candidate NVIDIA host therefore had no dedicated, generation-free dispatch path that could prove the complete local execution prerequisites and preserve exact blocker evidence before attempting Candidate 1.

CS494 adds a short, zero-cost, offline-only, GPU-bound preflight workflow. It is intentionally non-authoritative and never invokes generation, review packaging, publication, or Seeds 2–4. When a compatible self-hosted runner becomes available, this workflow can validate the exact host/runtime/cache prerequisites first and preserve diagnostics even when readiness fails.

## Added

- `.github/workflows/phase18-first-golden-preflight-only.yml`
  - manual dispatch restricted to `refs/heads/phase18/story-intelligence`;
  - immutable SHA checkout and branch reattachment;
  - same self-hosted `gpu/cuda/bf16/pul7sar-phase18` runner labels as the genuine Golden job;
  - `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`;
  - captures zero-cost network evidence, runner/CUDA identity, and exact approved local snapshot inventory;
  - runs `phase18_probe_first_golden_execution_blocker.py` with `continue-on-error` so blocker JSON survives;
  - independently asserts all authority fields remain false;
  - fails closed when `ready_for_authoritative_golden_preflight` is not true;
  - uploads diagnostics with `if: always()` and three-day retention;
  - contains no generation or Golden review-bundle command.

- `tests/test_phase18_first_golden_preflight_only_workflow.py`
  - locks GPU/self-hosted labels, zero-cost mode, offline mode, and exact branch restriction;
  - proves generation/publication/review packaging are absent;
  - locks runner/snapshot capture before blocker probe and readiness assertion before diagnostics upload;
  - locks preservation of diagnostics on blocker failure.

## Modified

None.

## Deleted

None.

## Tests / validation

The new regression test is committed for normal Phase 18 CI execution. This log does not claim terminal-green status until GitHub Actions completes on the final CS494 HEAD.

## Gates preserved

No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/network-isolation, semantic-publication, exact model/runtime provenance, CUDA/native-BF16, PNG structural/chunk-semantic/canonical, Human Visual Review, Golden-quality, publication, or Seeds 2–4 authority was weakened. No paid API, model download, CPU generation, FP16 generation, or FP32 generation fallback was added.

## First Genuine Golden PNG status

No genuine Golden PNG was generated in CS494 and no GPU result was fabricated.

The remaining execution blocker is external to repository preparation: an online self-hosted NVIDIA runner matching the required labels and exposing CUDA-enabled PyTorch, a real CUDA device with native BF16, sufficient GPU/host/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only constraints.

CS494 reduces the next execution step to a safe two-stage sequence: run the preflight-only workflow on the candidate NVIDIA host; only if it reports zero blockers should the authoritative first-Golden Candidate 1 workflow be dispatched.
