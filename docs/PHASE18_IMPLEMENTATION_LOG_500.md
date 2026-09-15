# Phase 18 Implementation Log — CS500

## Scope
Harden the authoritative first-Golden pre-generation binding implementation on `phase18/story-intelligence` only. `main` was not modified.

## Baseline reviewed
- Starting branch HEAD: `30bcd1c521edbf6317414fb6c667cbe5a9cd00e5` (CS499).
- CS499 CI had 12 workflow runs on the exact HEAD; the completed runs inspected were successful.
- CS499 activated the semantically hardened pre-generation evidence binder immediately before freshness capture and Candidate 1.
- Remaining integrity gap: the wrapper trusted the imported binder implementation from the worktree without independently proving that the binder file being executed was the exact tracked file at the immutable dispatch/source SHA.

## Changes
### Modified
- `tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py`
  - added `_prove_binding_implementation_is_immutable(expected_commit)`;
  - validates the expected commit is a lowercase 40-character SHA;
  - proves the binder path is tracked at that exact commit using `git ls-tree`;
  - reads the committed binder bytes using `git show <sha>:<path>`;
  - compares committed bytes with the current worktree binder bytes;
  - fails closed on missing/untracked binder, Git proof failure, malformed SHA, or worktree drift;
  - performs this proof before invoking the binder, freshness capture, or canonical Candidate-1 attempt;
  - records `pre_generation_binding_implementation_immutable=true` only after the proof succeeds.
- `tests/test_phase18_authoritative_pre_generation_binding_activation.py`
  - regression-locks immutable-binder proof before binding and Candidate 1;
  - locks exact source-SHA tree lookup and committed-vs-worktree byte comparison;
  - preserves existing evidence-consumption and authority-closure checks.

### Added
- `docs/PHASE18_IMPLEMENTATION_LOG_500.md`.

### Deleted
- None.

## Gate preservation
No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/offline-only, semantic-publication, exact model/runtime, CUDA/native-BF16, PNG structure/chunk-semantics/canonical, Human Visual Review, Golden-quality, publication, or Seeds 2-4 gate was weakened. No paid API, model download, CPU generation fallback, FP16 substitution, or FP32 substitution was introduced.

## Effective critical-path improvement
The authoritative path now proves not only that the four pre-generation evidence files are cryptographically and semantically valid, but also that the code performing that proof is exactly the binder implementation tracked at the immutable source SHA. A modified/untracked worktree binder cannot be used to authorize entry into the canonical Candidate-1 attempt.

## Testing
- Regression coverage updated to lock ordering: immutable binder proof -> evidence bind -> persist binding -> freshness capture -> canonical attempt.
- Regression coverage locks `git ls-tree`, `git show`, byte equality, and closed authority fields.
- GitHub CI must complete on the final CS500 HEAD before CS500 is called terminal-green.

## Golden PNG status / blocker
No Genuine Golden Visual PNG was fabricated or claimed. Actual Candidate-1 execution still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device with native BF16, sufficient GPU/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` / offline-only constraints.

## Remaining work
1. Let CS500 complete CI.
2. On a compatible NVIDIA host, run the preflight-only qualification path.
3. Only with zero blockers, dispatch the authoritative first-Golden workflow.
4. Candidate 1 must pass all existing factual, identity, sentiment, semantic-publication, provenance, PNG, review-bundle, Human Visual Review, and Golden-quality gates before approval or publication authority can exist.
