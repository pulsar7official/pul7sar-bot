# Phase 18 Implementation Log — CS447

## Scope

CS447 repairs the remaining central CPU-verification regression introduced around the attested first-Golden CLI contract, corrects the CS446 verification-history record, and preserves every production gate unchanged on `phase18/story-intelligence` only.

No write was made to `main`.

## Reviewed starting state

- Reviewed branch HEAD: `1d8f0de482c9c3abdb1aadeca06e08ba76c7645b`.
- Exact-HEAD auxiliary Phase 18 study workflows were green, but `Phase 18 Story Intelligence Verification` was terminal-red for both push (`34760936068`) and pull request (`34760937767`).
- Both central failures stopped in `Syntax and discover validation`; downstream production-isolation and visual-study steps were therefore correctly skipped.
- Direct inspection of the canonical workflow confirmed that the production protections were still present: branch isolation from `main.py`, `$0-local`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, CUDA-only PyTorch, native BF16, and refusal of FP16/FP32 substitution.
- Direct inspection of the attested pre-GPU runner and canonical launcher confirmed that network-download, publication, and Seeds 2–4 authority remained explicitly closed.
- No compatible CUDA/BF16 self-hosted execution result existed, so no genuine Golden PNG could be claimed.

## Changes

### Modified

- `tests/test_phase18_first_golden_attested_cli_contract.py`
  - Replaced regex-based `argparse` flag discovery with standard-library `ast` inspection.
  - The AST walker accepts formatting changes, line wrapping, and quote-style changes while extracting only literal long-form options passed to `*.add_argument(...)`.
  - Existing checks for immutable `--expected-commit`, evidence paths, stale `*-out` aliases, `$0-local`, offline-only execution, and closed authority remain.
  - No third-party dependency was added.

- `docs/PHASE18_IMPLEMENTATION_LOG_446.md`
  - Corrected the inaccurate statement that CS445 had already been terminal-green before CS446.
  - Added an explicit historical note that later terminal verification showed the central CPU verification failure.
  - Recorded the CS447 structural-test repair without rewriting production history.

### Added

- `docs/PHASE18_IMPLEMENTATION_LOG_447.md`
  - This implementation record.

### Deleted

- Nothing.

## Commit sequence before this log commit

- `c5ef1c962118b358d45bf9975a8dca4366a3c326` — initial focused CLI-contract test repair pass.
- `8f952b88dc17e9651e0bb5ea5c4d0ef2c74af0cd` — replace regex flag discovery with structural AST inspection.
- `2b0757371a5af267e576131be9e85056bd8a10cc` — correct CS446 verification-history documentation.

## Production gates preserved

CS447 changes no generation or publication code. It does not change:

- factual verification;
- entity/person identity verification;
- result/sentiment neutrality;
- SemanticPublicationGate behavior;
- visual-quality thresholds;
- Human Visual Review authority;
- Candidate 1 prompt, seed, dimensions, steps, guidance, or other generation parameters;
- Qwen2.5-VL model identity/revision;
- FLUX.2 model identity/revision;
- native BF16 requirement;
- CUDA requirement;
- `$0-local` cost mode;
- `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`;
- local-cache-only model resolution;
- network-download authority;
- publication authority;
- Seeds 2–4 authority.

No network model download was authorized. No FP16/FP32 fallback was introduced. `main` was not modified.

## Tests and verification status

The focused test implementation is standard-library-only and is intended to run under the repository's existing `unittest discover` CPU validation path. New exact-HEAD GitHub Actions runs are expected after the CS447 commits; CS447 must not be described as terminal-green until those runs complete successfully.

## Why this materially reduces the gap to the first genuine PNG

The first compatible GPU host must not be wasted on a preventable CPU/contract-test failure. CS447 removes formatting-sensitive CLI introspection from the critical pre-GPU contract and restores a structurally meaningful test: workflows must still pass the exact immutable commit and evidence flags that the Python entrypoints actually expose.

Once central CPU verification is green, the remaining material blocker is execution availability rather than orchestration: a compatible self-hosted NVIDIA runner must prove CUDA-enabled PyTorch, at least one real CUDA device, native BF16, approved GPU identity/compute capability, sufficient live-free VRAM, sufficient host RAM and filesystem/cache headroom, compatible generation and Qwen semantic runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already locally resolvable under offline `$0-local` execution.

## Genuine Golden PNG status

No PNG was generated, simulated, or claimed in CS447.
